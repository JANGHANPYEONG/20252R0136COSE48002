import requests
import numpy as np

import cv2
from PIL import Image
from skimage.segmentation import slic
from skimage.feature import greycomatrix, greycoprops, local_binary_pattern
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.spatial import KDTree

import torch
import torch.nn.functional as F

import mlflow
import mlflow.pytorch

from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor
import matplotlib.pyplot as plt

import io

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
from utils import Colorpalette


## ---------------- 공통: ndarray to image ---------------- ##
def ndarray_to_image(s3_conn, response, image_name):
    # Min-Max scaling을 통해 값을 [0, 255] 범위로 조정
    min_val = response.min()
    max_val = response.max()
    scaled_array = (response - min_val) / (max_val - min_val) * 255
    image = Image.fromarray(scaled_array.astype(np.uint8))

    # 이미지 데이터를 바이트 배열로 변환
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    
    # AWS S3에 업로드
    bucket_name = s3_conn.bucket  # 버킷 이름

    # 업로드
    s3_conn.upload_fileobj(buffer, bucket_name, image_name)

    # 업로드된 이미지의 URL 생성
    image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_name}"
    
    return image_url


## ---------------- Model 호출 ---------------- ##
def serve_mlflow(model_name, version):
    mlflow.set_tracking_uri("http://0.0.0.0:6002")
    model_uri = f"models:/{model_name}/{version}"

    try:
        model = mlflow.pytorch.load_model(model_uri)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        print(f"Success to load model")

        return model
    except mlflow.exceptions.MlflowException as e:
        print(f"Error loading model: {e}")


## ---------------- 단면 도출 ---------------- ##
# CLS Attention Map 가져오기
def get_cls_attention_map(model, input_tensor):
    cls_weights = []

    def hook_fn(module):
        cls_weights.append(module.cls_attn_map.mean(dim=1))

    hooks = []
    for block in model.base_model.blocks:
        hooks.append(block.attn.register_forward_hook(hook_fn))

    with torch.no_grad():
        _ = model(input_tensor)

    for hook in hooks:
        hook.remove()

    return cls_weights[-1]  # 마지막 레이어(12번째)의 CLS Attention Map 반환


# 이미지 마스킹 및 크롭 함수
def mask_and_crop_images(images, cls_attention_maps, threshold=0.5, crop_percent=0.1):
    B, C, H, W = images.shape
    masked_cropped_and_centered_images = []

    for i in range(B):
        cls_map = cls_attention_maps[i].view(14, 14)  # 14x14 크기로 재구성
        cls_resized = F.interpolate(cls_map.unsqueeze(0).unsqueeze(0), (H, W), mode='bilinear').squeeze()
        cls_resized = (cls_resized - cls_resized.min()) / (cls_resized.max() - cls_resized.min())

        mask = (cls_resized > threshold).float()
        masked_image = images[i] * mask

        # 색깔이 있는 부분 찾기 (검은색이 아닌 부분)
        non_black = torch.any(masked_image != 0, dim=0)
        non_zero = torch.nonzero(non_black)

        if len(non_zero) > 0:
            top, left = non_zero.min(0)[0]
            bottom, right = non_zero.max(0)[0]

            # Crop 영역 계산
            height = bottom - top
            width = right - left

            # crop_percent만큼만 각 방향에서 제거
            crop_amount_y = int(height * crop_percent / 2)
            crop_amount_x = int(width * crop_percent / 2)

            crop_top = max(0, top + crop_amount_y)
            crop_bottom = min(H, bottom - crop_amount_y)
            crop_left = max(0, left + crop_amount_x)
            crop_right = min(W, right - crop_amount_x)

            # Crop 수행
            cropped_image = masked_image[:, crop_top:crop_bottom, crop_left:crop_right]

            # 크롭된 이미지의 새 크기
            new_h, new_w = crop_bottom - crop_top, crop_right - crop_left

            # 새 이미지 생성 (검은 배경)
            centered_image = torch.zeros_like(images[i])

            # 크롭된 이미지를 중앙에 위치시키기
            start_y = (H - new_h) // 2
            start_x = (W - new_w) // 2
            centered_image[:, start_y:start_y + new_h, start_x:start_x + new_w] = cropped_image

        else:
            centered_image = torch.zeros_like(images[i])

        masked_cropped_and_centered_images.append(centered_image)

    return torch.stack(masked_cropped_and_centered_images)


def extract_reddest_among_dominant_colors(image_path, k=5):
    # 이미지 로드
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # 검은색 픽셀 제외
    mask = np.all(image != [0, 0, 0], axis=-1)
    non_black_pixels = image[mask]

    # K-means 클러스터링
    kmeans = KMeans(n_clusters=k, n_init=10)
    kmeans.fit(non_black_pixels.reshape(-1, 3))

    # 클러스터 중심점 얻기
    colors = kmeans.cluster_centers_

    # 각 클러스터의 비율 계산
    distribution, _ = np.histogram(kmeans.labels_, bins=np.arange(k + 1))
    distribution = distribution.astype("float")
    distribution /= distribution.sum()

    sorted_indices = np.argsort(distribution)[::-1]
    dominant_colors = colors[sorted_indices]  # return 용
    dominant_distribution = distribution[sorted_indices]  # return 용

    # 하얀색 필터링 (기준: [202.06807512, 194.87042254, 191.93239437])
    white_color = np.array([202.06807512, 194.87042254, 191.93239437])

    additional_colors = [
        np.array([186, 184, 186]),
        np.array([171, 144, 129]),
        np.array([165, 153, 144]),
        np.array([165, 128, 110]),
        np.array([144, 94, 81]),
        np.array([129, 94, 82]),
        np.array([127, 108, 96]),
        np.array([111, 91, 84]),
        np.array([106, 86, 84]),
        np.array([95, 60, 60]),
        np.array([78, 56, 50]),
        np.array([80, 43, 33]),
        np.array([80, 39, 20]),
        np.array([66, 36, 35]),
        np.array([46, 12, 8]),
        np.array([42, 16, 12]),
        np.array([40, 17, 16]),
        np.array([35, 8, 7]),
        np.array([25, 8, 6]),
    ]

    threshold = 5

    def is_far_from_color(color, reference_color, threshold):
        return np.linalg.norm(color - reference_color, axis=1) > threshold

    # 모든 색상 필터링 조건 적용
    non_white_indices = is_far_from_color(dominant_colors, white_color, 20)

    non_filtered_indices = non_white_indices
    for color in additional_colors:
        non_additional_indices = is_far_from_color(dominant_colors, color, threshold)
        non_filtered_indices = non_filtered_indices & non_additional_indices

    # 하얀색이 아닌 색상과 분포값 선택
    filtered_colors = dominant_colors[non_filtered_indices]
    filtered_distribution = dominant_distribution[non_filtered_indices]

    # 상위 2개의 색상 선택 (하얀색 필터링 후)
    sorted_colors = filtered_colors[:2]

    # 주어진 RGB 값들
    red_colors = np.array([
        [212, 102, 81],
        [202, 89, 72],
        [185, 110, 103],
        [184, 74, 63],
        [166, 60, 53],
        [165, 89, 74],
        [160, 120, 119],
        [153, 109, 109],
        [152, 64, 71],
        [152, 47, 46],
        [148, 76, 66],
        [146, 88, 82],
        [143, 84, 78],
        [141.12587038, 65.83824317, 56.43813605],
        [139, 47, 44],
        [135, 35, 31],
        [134, 47, 44],
        [137, 85, 85],
        [134, 53, 67],
        [129.26635239, 73.01591043, 75.14348851],
        [129, 58, 49],
        [128.12528736, 62.96666667, 56.975],
        [125, 57, 66],
        [124, 25, 28],
        [122, 61, 51],
        [121, 54, 51],
        [118, 60, 59],
        [114.28116018, 54.21478965, 50.98850274],
        [113, 28, 36],
        [110, 29, 22],
        [108, 38, 34],
        [107, 41, 41],
        [105, 34, 27],
        [103, 28, 43],
        [77, 33, 29],
        [98, 49, 49],
        [98, 38, 37],
        [91, 32, 24],
        [90, 24, 18],
        [82, 19, 17],
        [82, 33, 28],
        [66, 16, 12],
        [53, 11, 7],
    ])

    # 빨간색에 가까운 정도 계산
    def calculate_redness_score(color, red_colors):
        distances = np.linalg.norm(red_colors - color, axis=1)
        return np.min(distances)  # 가장 작은 오차값 반환

    # 각각의 색상에 대해 오차 계산
    red_scores = [calculate_redness_score(color, red_colors) for color in sorted_colors]

    # 더 작은 오차값을 지니는 색상 선택 (오차값이 같으면 인덱스가 더 작은 값을 선택)
    min_error = np.min(red_scores)
    min_error_indices = np.where(red_scores == min_error)[0]
    reddest_color_index = min_error_indices[0]  # 가장 작은 인덱스를 선택

    reddest_color_rgb = sorted_colors[reddest_color_index]

    return reddest_color_rgb


# 단일 이미지 처리 및 시각화 함수
def process_and_visualize_single_image(model, device, image_path, meat_id, threshold=0.5, crop_percent=0.1, k=5):
    # 이미지 로드 및 전처리
    # URL에서 이미지 다운로드
    response = requests.get(image_path)
    image = Image.open(io.BytesIO(response.content))

    transform = Compose([
        Resize(256),
        CenterCrop(224),
        ToTensor(),
    ])
    input_tensor = transform(image).unsqueeze(0).to(device)

    # CLS Attention Map 계산
    cls_attention_maps = get_cls_attention_map(model, input_tensor)

    # 마스킹 및 크롭 적용
    masked_and_cropped_image = mask_and_crop_images(input_tensor, cls_attention_maps, threshold, crop_percent)

    # 크롭된 이미지 저장
    cropped_image_path = f'opencv_utils/cropped_image_{meat_id}.jpg'
    plt.imsave(cropped_image_path, masked_and_cropped_image.squeeze().permute(1, 2, 0).cpu().numpy())

    reddest_color = extract_reddest_among_dominant_colors(cropped_image_path)

    return reddest_color


def resize_short_side(image, target_size):
    h, w = image.shape[:2]
    short_side = min(h, w)
    scale = target_size / short_side

    new_h = int(h * scale)
    new_w = int(w * scale)

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
    return resized


def create_slic_color_palette(image, num_segments=256, num_colors=12):  # 이미지 컬러팔레트에 쓰이는 것과 동일
    # 이미지 사이즈 정보
    # SLIC 슈퍼픽셀 생성: skimage.segmentation 이용
    segments = slic(image, n_segments=num_segments, compactness=10, sigma=1, start_label=1)
    # 실제 생성된 슈퍼픽셀 개수 확인: num_segments로 생성한 개수와 실 생성한 픽셀 수 다름.
    unique_segments = np.unique(segments)
    actual_num_segments = len(unique_segments)

    # 각 슈퍼픽셀의 주요 색상 추출
    superpixel_colors = np.zeros((actual_num_segments, 3))
    for i, seg_val in enumerate(unique_segments):
        mask = segments == seg_val
        superpixel_colors[i] = image[mask].mean(axis=0)

    # 슈퍼픽셀의 주요 색상으로 이미지 생성
    superpixel_image = np.zeros_like(image)
    for i, seg_val in enumerate(unique_segments):
        mask = segments == seg_val
        superpixel_image[mask] = superpixel_colors[i]
    
    # K-Means 클러스터링을 사용하여 주요 색상 num_colors개 만큼 추출
    kmeans = KMeans(n_clusters=num_colors, n_init=10)
    kmeans.fit(superpixel_colors)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_

    # 각 클러스터의 빈도 계산: count 개념
    _, counts = np.unique(labels, return_counts=True)
    counts_sorted_indices = np.argsort(-counts)
    sorted_palette = colors[counts_sorted_indices]
    sorted_counts = counts[counts_sorted_indices]

    # 각 색상의 비율 계산: %로 계산
    total_count = np.sum(sorted_counts.astype(float))
    proportions = sorted_counts / total_count

    return sorted_palette, proportions, segments, superpixel_image


def cluster_color_areas(image, target_color, color_threshold, eps, min_samples):
    image_rgb = image

    # 이미지를 2차원 배열로 변환
    pixel_values = image_rgb.reshape((-1, 3))

    # 타겟 색상 거리 계산
    distances_to_target = np.linalg.norm(pixel_values - target_color, axis=1)

    # 제외할 색상 거리 계산
    distances_to_exclude = np.linalg.norm(pixel_values - (98, 58, 37), axis=1)

    # 조건에 맞는 픽셀 선택
    selected_mask = (distances_to_target < color_threshold) & (distances_to_exclude > 5)
    selected_pixels = np.column_stack(np.where(selected_mask.reshape(image_rgb.shape[:2])))
    
    # 선택된 픽셀이 없는 경우 예외 처리
    if len(selected_pixels) == 0:
        print("No pixels found within the specified color threshold.")
        return image_rgb, None, 0, None, None

    # DBSCAN을 사용하여 군집화
    db = DBSCAN(eps=eps, min_samples=min_samples).fit(selected_pixels)

    # 각 픽셀에 클러스터 할당
    labels = db.labels_

    # 클러스터의 수 (노이즈를 포함하지 않음)
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

    # 클러스터 색상 할당
    segmented_image = np.zeros_like(image_rgb, dtype=np.uint8)
    for label in set(labels):
        if label == -1:
            # 노이즈는 무시
            continue
        mask = (labels == label)

        color = 255 * (label + 1) // (n_clusters + 1)
        color = (100, color, 100)
        segmented_image[selected_pixels[mask][:, 0], selected_pixels[mask][:, 1]] = color

    return image_rgb, segmented_image, n_clusters, labels, selected_pixels


def extract_largest_clusters(segmented_image, labels, selected_pixels):
    # 각 클러스터의 면적 계산
    unique_labels, counts = np.unique(labels, return_counts=True)
    if -1 in unique_labels:
        counts = counts[unique_labels != -1]
        unique_labels = unique_labels[unique_labels != -1]

    # 클러스터 면적 기준으로 정렬
    largest_indices = np.argsort(counts)[::-1]  # 내림차순으로 정렬
    
    if counts[largest_indices[0]] <= 2600:
        return segmented_image
    else :
        # 임계값 이하의 contour 소거
        contours, _ = cv2.findContours(cv2.threshold(cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY), 1, 255, cv2.THRESH_BINARY)[1], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered_contours = [contour for contour in contours if cv2.contourArea(contour) >= 2600]

        if len(filtered_contours) == 0:
            print("No contours found above the threshold.")
            return segmented_image

        # 가장 큰 두 클러스터 선택
        largest_contours = sorted(filtered_contours, key=cv2.contourArea, reverse=True)[:2]

        if len(largest_contours) < 2:
            return segmented_image

        # 이미지 중심 좌표 계산
        h, w = segmented_image.shape[:2]
        center = np.array([w / 2, h / 2])

        # 가장 큰 두 클러스터의 중심 좌표 계산
        cluster_centers = []
        for contour in largest_contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = 0, 0
            cluster_centers.append((cx, cy))

        # 중심으로부터의 거리 계산
        cluster_centers = np.array(cluster_centers)
        distances = np.linalg.norm(cluster_centers - center, axis=1)

        # 가장 중심에 가까운 클러스터 선택
        central_cluster_index = np.argmin(distances)
        central_cluster_contour = largest_contours[central_cluster_index]

        # 중심 클러스터의 마스크 생성
        central_cluster_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(central_cluster_mask, [central_cluster_contour], -1, 1, thickness=cv2.FILLED)

        mask_2d = np.zeros((h, w), dtype=bool)
        mask_2d[selected_pixels[:, 0], selected_pixels[:, 1]] = central_cluster_mask[selected_pixels[:, 0], selected_pixels[:, 1]]

        # 마스킹된 이미지 생성
        masked_image = np.zeros_like(segmented_image)
        masked_image[mask_2d] = segmented_image[mask_2d]

        return masked_image


# 이미지의 중심 계산
def find_central_contour(image, contours, n_largest=2):
    # 이미지를 그레이스케일로 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 특정 영역 (0, 0)에서 (50, 50)을 검은색으로 설정
    gray[:55, :] = 0
    gray[214:, :] = 0 # y축
    gray[:, :45] = 0
    gray[:, 190:] = 0 # x축

    # Threshold를 적용하여 이진화
    _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    # Contours를 찾기
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 빈 이미지 생성
    contour_image = np.zeros(image.shape[:2], dtype=np.uint8)

    # 모든 contour를 이미지에 그리기
    cv2.drawContours(contour_image, contours, -1, 255, thickness=cv2.FILLED)

    # 이미지 dilate
    kernel = np.ones((5, 5), np.uint8)
    dilated_image = cv2.dilate(contour_image, kernel, iterations=1)

    # 새로운 contour 찾기
    new_contours, _ = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 모든 점들을 결합
    all_points = np.vstack(new_contours)

    # Convex hull을 계산
    hull = cv2.convexHull(all_points)

    # 결과를 표시할 이미지 생성
    result_image = np.zeros_like(image)

    # 병합된 contour를 파란색으로 그림
    cv2.drawContours(result_image, [hull], -1, (255, 0, 0), 2)
    
    return result_image, [hull], 1


# 최종 단면 도출 함수
def process_visualize(model, s3_conn, image_url):
    # URL에서 이미지 데이터를 가져옵니다
    response = requests.get(image_url)
    image_array = np.frombuffer(response.content, np.uint8)

    # 이미지를 디코딩합니다
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # BGR에서 RGB로 변환
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # # 사용 예시
    target_size = 256  # 원하는 짧은 변의 길이
    image_rgb = resize_short_side(image_rgb, target_size)

    image_rgb = image_rgb[100:350,0:224]  #[y:y+h, x:x+w]

    target_C = process_and_visualize_single_image(model, image_url, threshold=0.5, crop_percent=0.35)

    sorted_palette, _, _, _ = create_slic_color_palette(image_rgb, num_segments=3000, num_colors=10)

    # 팔레트 색상 목록을 배열로 변환
    palette_colors = sorted_palette

    # KDTree 생성
    tree = KDTree(palette_colors)

    # 가장 가까운 색상 찾기
    _, index = tree.query(target_C)
    closest_color_value = palette_colors[index]

    # target_color = sorted_palette[1-1]
    target_color = closest_color_value

    color_threshold = 15  # 색상 거리 임계값
    eps = 5  # 두 샘플이 같은 클러스터에 속하기 위한 최대 거리
    min_samples = 3  # 한 클러스터 내의 최소 샘플 수

    # 이미지 군집화 -> image_path와 target_color는 위에서 구한 값 적용
    _, segmented_image, _, labels, selected_pixels = cluster_color_areas(image_rgb, target_color, color_threshold, eps, min_samples);
    largest_cluster_image = extract_largest_clusters(segmented_image, labels, selected_pixels);

    gray = cv2.cvtColor(largest_cluster_image, cv2.COLOR_BGR2GRAY)

    _, otsu = cv2.threshold(gray, 3, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    outline_image = np.zeros_like(image_rgb)

    # 컨투어 면적이 큰 순으로 정렬
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

    COLOR = (0, 200, 0)
    cv2.drawContours(outline_image, contours, -1, COLOR, 2)
    _, largest_contour, flag = find_central_contour(outline_image, sorted_contours)

    flag = 1
    if flag == 0:
        # 근사 컨투어 계산을 위한 0.01의 오차 범위 지정
        epsilon = 0.01 * cv2.arcLength(largest_contour, True)
        approx_contour = cv2.approxPolyDP(largest_contour, epsilon, True)

        # 컨투어 확장
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [approx_contour], -1, 255, thickness=cv2.FILLED)

        kernel = np.ones((21, 21), np.uint8)  # 커널 크기를 조정하여 확장 크기 조절
        dilated_mask = cv2.dilate(mask, kernel, iterations=1)

        ## Convex Hull 계산
        hull = cv2.convexHull(approx_contour)

        # 마스크를 생성합니다.
        mask = np.zeros_like(gray)
        cv2.drawContours(mask, [hull], -1, 255, thickness=cv2.FILLED)

        # 마스크 적용하여 타원 부분만 추출
        masked_image = cv2.bitwise_and(image_rgb, image_rgb, mask=dilated_mask) 

    # 바로 마스크 생성 
    else :
        mask = np.zeros_like(gray)
        if largest_contour is not None :
            cv2.drawContours(mask, largest_contour, -1, 255, thickness=cv2.FILLED)

        # 마스크 적용하여 타원 부분만 추출
        masked_image = cv2.bitwise_and(image_rgb, image_rgb, mask=mask)

    # BGR에서 RGB로 변환
    masked_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2RGB)
    
    section_image_url = ndarray_to_image(s3_conn, response, masked_image)
    return section_image_url


## ---------------- 단백질, 지방 컬러팔레트 ---------------- ##
palette = Colorpalette()

def calculate_distance(color1, color2):
    return np.sqrt(np.sum((np.array(color1) - np.array(color2))**2))

def find_closest_color(input_color, color_list):
    distances = [calculate_distance(input_color, color) for color in color_list]
    return min(distances)

def determine_color(palette_as_list, proportions):
    protein_count = 0  # 단백질 개수
    fat_count = 0      # 지방 개수
    background_count = 0  # 배경 개수

    protein_proportion = 0
    fat_proportion = 0

    for i in range(0, len(palette_as_list)):
        background = find_closest_color(palette_as_list[i], palette.black)
        if background < 40:
            background_count += 1
        else:
            red_distance = find_closest_color(palette_as_list[i], palette.reds)
            white_distance = find_closest_color(palette_as_list[i], palette.whites)

            if red_distance < white_distance:
                protein_count += 1
                protein_proportion += proportions[i]
            else:
                fat_count += 1
                fat_proportion += proportions[i]
                
    total = protein_proportion + fat_proportion
    if total > 0:
        protein_ratio = protein_proportion / total
        fat_ratio = fat_proportion / total
    else:
        protein_ratio = 0
        fat_ratio = 0

    protein_ratio *= 100
    fat_ratio *= 100
    
    return round(protein_ratio), round(fat_ratio)

def color_list_distance(pixel, white_exclude_color):
    for i in range(0, len(white_exclude_color)):
        dst = calculate_distance(pixel, white_exclude_color[i])
        if dst <= 40:
            return 0
    return 1


## ---------------- 전체 컬러팔레트, 지방 단백질 비율 ---------------- ##
# 최종 함수 (컬러팔레트 리스트 3개, 단&지 비율)
def final_color_palette_proportion(image_path):
    
    #이미지 불러오기
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    original_sorted_palette, proportions, segments, superpixel_image = create_slic_color_palette(image, num_segments=3000, num_colors = 11)
    
    original_sorted_palette = original_sorted_palette[1:]

    # SLIC 슈퍼픽셀 생성: skimage.segmentation 이용
    segments = slic(image, n_segments=palette.num_segments, compactness=10, sigma=1, start_label=1)
    # 실제 생성된 슈퍼픽셀 개수 확인: num_segments로 생성한 개수와 실 생성한 픽셀 수 다름.
    unique_segments = np.unique(segments)
    actual_num_segments = len(unique_segments)

    # 각 슈퍼픽셀의 주요 색상 추출
    superpixel_colors = np.zeros((actual_num_segments, 3))
    for i, seg_val in enumerate(unique_segments):
        mask = segments == seg_val
        superpixel_colors[i] = image[mask].mean(axis=0)

    # 슈퍼픽셀의 주요 색상으로 이미지 생성
    superpixel_image = np.zeros_like(image)
    for i, seg_val in enumerate(unique_segments):
        mask = segments == seg_val
        superpixel_image[mask] = superpixel_colors[i]

    kmeans = KMeans(n_clusters=palette.num_colors, n_init=10)
    kmeans.fit(superpixel_colors)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_

    # 각 클러스터의 빈도 계산: count 개념
    _, counts = np.unique(labels, return_counts=True)
    counts_sorted_indices = np.argsort(-counts)
    sorted_palette = colors[counts_sorted_indices]
    sorted_counts = counts[counts_sorted_indices]

    sorted_palette = sorted_palette[1:]
    proportions = proportions[1:]

    # 각 색상의 비율 계산: %로 계산
    total_count = np.sum(sorted_counts.astype(float))
    proportions = sorted_counts / total_count

    # n번째 색상에 해당하는 클러스터 인덱스
    target_cluster_index = counts_sorted_indices[1]

    # 특정 클러스터에 속하는 슈퍼픽셀의 경계만 표시하기 위해 마스크 생성
    boundary_mask = np.zeros_like(segments, dtype=bool)
    for i, seg_val in enumerate(unique_segments):
        if labels[i] == target_cluster_index:
            boundary_mask |= (segments == seg_val)

    protein_ratio, _ = determine_color(sorted_palette, proportions)

    # 지방에 해당하는 모든 인덱스를 한 번에 이미지에 표시
    boundary_mask = np.zeros_like(segments, dtype=bool)
    for t in palette.white_idx_list:
        # 지방색상에 해당하는 클러스터 인덱스
        target_cluster_index = counts_sorted_indices[t]

        # 특정 클러스터에 속하는 슈퍼픽셀의 경계 마스크 업데이트
        for i, seg_val in enumerate(unique_segments):
            if labels[i] == target_cluster_index:
                boundary_mask |= (segments == seg_val)

    # 경계 내의 픽셀 색상을 추출하여 검정색과 제외 색상을 제외하고 주요 색상 5개 추출
    fat_region_pixels = image[boundary_mask]
    non_excluded_pixels = [
        pixel for pixel in fat_region_pixels 
        if calculate_distance(pixel, palette.black[0]) > 40 and color_list_distance(pixel, palette.white_exclude_color)
    ]
    #바깥 영역의 픽셀을 추출
    outside_mask = ~boundary_mask
    outside_pixels = image[outside_mask]
    outside_non_excluded_pixels = [
        pixel for pixel in outside_pixels 
        if calculate_distance(pixel, palette.black[0]) > 40 and color_list_distance(pixel, palette.red_exclude_color)
    ]
    
    # reds에 가까운 색상을 찾기
    red_proximity_pixels = [
        pixel for pixel in non_excluded_pixels
        if find_closest_color(pixel, palette.red_list_select) < 30
    ]

    # whites에 가까운 색상을 찾기
    whites_proximity_pixels = [
        pixel for pixel in non_excluded_pixels
        if find_closest_color(pixel, palette.whites_list_select) < 30
    ]

    #지방 주요 색상 5개를 추출 
    n_clusters_white = min(5, len(whites_proximity_pixels))
    if n_clusters_white > 0:
        kmeans = KMeans(n_clusters=n_clusters_white, n_init=10)
        kmeans.fit(whites_proximity_pixels)
        fat_colors = kmeans.cluster_centers_
    else:
        fat_colors = []

    #단백질 주요 색상 5개 추출
    n_clusters_red = min(5, len(outside_non_excluded_pixels))
    if n_clusters_red > 0:
        kmeans = KMeans(n_clusters=n_clusters_red, n_init=10)
        kmeans.fit(outside_non_excluded_pixels)
        protein_colors = kmeans.cluster_centers_
    else:
        protein_colors = []
    
    result = {
        "fat_color_palette": fat_colors,
        "protein_color_palette": protein_colors,
        "total_color_palette": original_sorted_palette,
        "protein_ratio": protein_ratio
    }
    return result


## ---------------- texture 정보 ---------------- ##
def create_texture_info(img_path):
    image = cv2.imread(img_path)
    # 이미지 로드
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 마스크 생성: 검정색 배경을 제외
    mask = cv2.inRange(image, (1, 1, 1), (255, 255, 255))

    # 관심 영역만 추출 (검정색 배경 제외)
    roi = gray[mask != 0] #1차원 배열인 상태 

    # GLCM 계산을 위한 형태로 변환
    roi_reshaped = roi.reshape(-1, 1)

    # GLCM 계산
    distances = [1]
    angles = [np.pi/2]
    glcm = greycomatrix(roi_reshaped, distances, angles, 256, symmetric=True, normed=True)

    # 텍스처 특징 추출
    texture_result = {
        "contrast" : greycoprops(glcm, 'contrast'),
        "dissimilarity" : greycoprops(glcm, 'dissimilarity'),
        "homogeneity" : greycoprops(glcm, 'homogeneity'),
        "energy" : greycoprops(glcm, 'energy'),
        "correlation" : greycoprops(glcm, 'correlation')
    }

    return texture_result


## ---------------- LBP images, Gabor Filter images ---------------- ##
def lbp_calculate(s3_conn, img_path, meat_id, seqno):
    image = cv2.imread(img_path)
    # 이미지가 컬러 이미지인 경우 그레이스케일로 변환
    if len(image.shape) == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # LBP 결과를 저장할 배열 생성
    lbp1 = np.zeros_like(image)
    
    # 각 픽셀에 대해 LBP 계산
    for i in range(1, image.shape[0] - 1):
        for j in range(1, image.shape[1] - 1):
            # 중심 픽셀 값
            center = image[i, j]
            # 주변 8개 픽셀 값과 비교하여 이진 패턴 생성
            binary_pattern = 0
            binary_pattern |= (image[i-1, j-1] >= center) << 7
            binary_pattern |= (image[i-1, j  ] >= center) << 6
            binary_pattern |= (image[i-1, j+1] >= center) << 5
            binary_pattern |= (image[i,   j+1] >= center) << 4
            binary_pattern |= (image[i+1, j+1] >= center) << 3
            binary_pattern |= (image[i+1, j  ] >= center) << 2
            binary_pattern |= (image[i+1, j-1] >= center) << 1
            binary_pattern |= (image[i,   j-1] >= center) << 0
            # 결과 저장
            lbp1[i, j] = binary_pattern
            
    # Compute LBP
    radius = 3
    n_points = 8 * radius
    lbp2 = local_binary_pattern(image, n_points, radius, method='uniform')
    
    # Save the LBP image
    image_name1 = f'openCV_images/{meat_id}-{seqno}-lbp1-{i+1}.png'
    image_name2 = f'openCV_images/{meat_id}-{seqno}-lbp2-{i+1}.png'
    
    lbp_image1 = ndarray_to_image(s3_conn, lbp1, image_name1)
    lbp_image2 = ndarray_to_image(s3_conn, lbp2, image_name2)
    
    result = {
        "lbp1": lbp_image1,
        "lbp2": lbp_image2
    }

    return result


def create_gabor_kernels(ksize, sigma, lambd, gamma, psi, num_orientations):
    kernels = []
    for theta in np.linspace(0, np.pi, num_orientations, endpoint=False):
        kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lambd, gamma, psi, ktype=cv2.CV_32F)
        kernels.append(kernel)
    return kernels


def apply_gabor_kernels(img, kernels):
    responses = []
    for kernel in kernels:
        response = cv2.filter2D(img, cv2.CV_32F, kernel)
        responses.append(response)
    return responses


def compute_texture_features(responses):
    features = []
    for response in responses:
        mean = np.mean(response)
        std_dev = np.std(response)
        energy = np.sum(response**2)
        features.append([mean, std_dev, energy])
    return features


def gabor_texture_analysis(s3_conn, img_path, id, seqno):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

    # Gabor 필터 파라미터
    ksize = 31
    sigma = 4.0
    lambd = 10.0
    gamma = 0.5
    psi = 0
    num_orientations = 8  # 방향의 수

    kernels = create_gabor_kernels(ksize, sigma, lambd, gamma, psi, num_orientations)
    responses = apply_gabor_kernels(img, kernels)
    features = compute_texture_features(responses)
    
    result = {}
    for i, response in enumerate(responses):
        image_name = f'openCV_images/{id}-{seqno}-garbor-{i+1}.png'
        image_path = ndarray_to_image(s3_conn, response, image_name)
        
        result[i+1] = {
            "images": image_path,
            "mean": features[i][0],
            "std_dev": features[i][1],
            "energy": features[i][2]
        }

    return result

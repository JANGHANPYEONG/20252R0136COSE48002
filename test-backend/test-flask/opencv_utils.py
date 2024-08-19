import os
import pprint
import numpy as np
from numba import jit

import cv2
from PIL import Image
from skimage.segmentation import slic
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern
from sklearn.cluster import KMeans

import torch
from torch.utils.data import Dataset
from torchvision import transforms

import mlflow
import mlflow.pytorch

import io

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
from utils import ColorPalette


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
def serve_mlflow(run_id):
    mlflow.set_tracking_uri("http://0.0.0.0:6002")
    model_uri = f"runs:/{run_id}/best_model"

    try:
        model = mlflow.pytorch.load_model(model_uri)
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        print(f"Success to load model")

        return model
    except mlflow.exceptions.MlflowException as e:
        print(f"Error loading model: {e}")


## ---------------- 단면 도출 ---------------- ##
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MeatDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = []
        self.labels = []
        self.image_names = []
        
        self.classes = ['등심1++', '등심1+', '등심1', '등심2', '등심3']
        for idx, class_name in enumerate(self.classes):
            class_dir = os.path.join(root_dir, class_name)
            for img_name in os.listdir(class_dir):
                img_path = os.path.join(class_dir, img_name)
                self.images.append(img_path)
                self.labels.append(idx)
                self.image_names.append(img_name)

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        image_name = self.image_names[idx]
        
        if self.transform:
            image, _ = self.transform(image, Image.new('L', image.size))
        
        return image, label, image_name

class SegmentationTransform:
    def __init__(self, output_size=(448, 448)):
        self.output_size = output_size
    
    def __call__(self, image, mask):
        if isinstance(mask, np.ndarray):
            mask = Image.fromarray(mask.astype(np.uint8))
        
        image = transforms.Resize(256)(image)
        mask = transforms.Resize(256, interpolation=Image.NEAREST)(mask)
        
        pad_width = max(0, self.output_size[0] - image.size[0])
        pad_height = max(0, self.output_size[1] - image.size[1])
        pad_left = pad_width // 2
        pad_top = pad_height // 2
        pad_right = pad_width - pad_left
        pad_bottom = pad_height - pad_top
        
        padding = transforms.Pad((pad_left, pad_top, pad_right, pad_bottom))
        image = padding(image)
        mask = padding(mask)
        
        if image.size != self.output_size:
            crop = transforms.CenterCrop(self.output_size)
            image = crop(image)
            mask = crop(mask)
        
        image = transforms.ToTensor()(image)
        mask = transforms.ToTensor()(mask)
        
        return image, mask


def apply_mask(image, mask):
    return image * mask.to(device)


def extract_section_image(s3_conn, s3_image_path, s3_bucket, meat_id, seqno):
    # 데이터셋 및 DataLoader 설정
    transform = SegmentationTransform(output_size=(448, 448))
    
    # 사전 학습된 모델 로드
    run_id = "f702e1cbf98047ccbf9cb7ab5bf79a9e"
    model = serve_mlflow(run_id)
    model.eval()
    
    # S3에서 이미지 다운로드
    if s3_bucket:
        s3 = s3_conn
        bucket_name = s3_bucket
        object_key = s3_image_path

        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        img = Image.open(io.BytesIO(response['Body'].read())).convert("RGB")
        
    else:
        img = Image.open(s3_image_path).convert("RGB")
    # 이미지 변환
    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
    ])
    img_tensor = transform(img).unsqueeze(0).to(device)
    
    # 모델에 입력
    with torch.no_grad():
        output = model(img_tensor)
    
    # 마스크 생성 (U-Net 출력을 이진 마스크로 변환)
    mask = (output > 0.5).float().to(device)
    
    # 마스크 적용
    masked_img = apply_mask(img_tensor, mask)
    
    # 224x224로 center crop
    crop = transforms.CenterCrop(224)
    cropped_img = crop(masked_img).squeeze(0)
    
    # 이미지 저장 준비
    img = cropped_img.cpu().permute(1, 2, 0).clamp(0, 1).numpy()
    img = (img * 255).astype(np.uint8)
    img = Image.fromarray(img)

    # output_key를 설정
    output_key = os.path.join('section_images', f"{meat_id}-{seqno}.png")

    # 이미지 데이터를 바이트 스트림으로 변환
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # S3에 업로드
    s3.put_object(Bucket=s3_bucket, Key=output_key, Body=img_byte_arr, ContentType='image/png')

    print(f"Image processed and saved to S3 at {output_key}")
    return output_key  ## section_images/asdf-1.png


## ---------------- 단백질, 지방 컬러팔레트 ---------------- ##
palette = ColorPalette()

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


@jit(nopython=True)
def calculate_distance(color1, color2):
    return np.sqrt(np.sum((color1 - color2)**2))

@jit(nopython=True)
def find_closest_color(color, color_list):
    distances = np.sqrt(np.sum((color_list - color)**2, axis=1))
    return np.min(distances)

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
def final_color_palette_proportion(img):
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    original_sorted_palette, proportions, segments, superpixel_image = create_slic_color_palette(image, num_segments=3000, num_colors = 11)
    
    original_sorted_palette = original_sorted_palette[1:]

    # SLIC 슈퍼픽셀 생성: skimage.segmentation 이용
    segments = slic(image, n_segments=palette.num_segments, compactness=10, sigma=1, start_label=1)
    # 실제 생성된 슈퍼픽셀 개수 확인: num_segments로 생성한 개수와 실 생성한 픽셀 수 다름.
    unique_segments = np.unique(segments)
    actual_num_segments = len(unique_segments)
    print(1)

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
    print(2)

    kmeans = KMeans(n_clusters=palette.num_colors, n_init=10)
    kmeans.fit(superpixel_colors)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_
    print(3)

    # 각 클러스터의 빈도 계산: count 개념
    _, counts = np.unique(labels, return_counts=True)
    counts_sorted_indices = np.argsort(-counts)
    sorted_palette = colors[counts_sorted_indices]
    sorted_counts = counts[counts_sorted_indices]

    sorted_palette = sorted_palette[1:]
    proportions = proportions[1:]
    print(4)

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
    print(5)

    # 지방에 해당하는 모든 인덱스를 한 번에 이미지에 표시
    boundary_mask = np.zeros_like(segments, dtype=bool)
    for t in palette.white_idx_list:
        # 지방색상에 해당하는 클러스터 인덱스
        target_cluster_index = counts_sorted_indices[t]

        # 특정 클러스터에 속하는 슈퍼픽셀의 경계 마스크 업데이트
        for i, seg_val in enumerate(unique_segments):
            if labels[i] == target_cluster_index:
                boundary_mask |= (segments == seg_val)
    print(5)

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
def create_texture_info(image):
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
    glcm = graycomatrix(roi_reshaped, distances, angles, 256, symmetric=True, normed=True)

    # 텍스처 특징 추출
    texture_result = {
        "contrast" : graycoprops(glcm, 'contrast')[0][0],
        "dissimilarity" : graycoprops(glcm, 'dissimilarity')[0][0],
        "homogeneity" : graycoprops(glcm, 'homogeneity')[0][0],
        "energy" : graycoprops(glcm, 'energy')[0][0],
        "correlation" : graycoprops(glcm, 'correlation')[0][0]
        }
    
    return texture_result


## ---------------- LBP images, Gabor Filter images ---------------- ##
def lbp_calculate(s3_conn, image, meat_id, seqno):
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
    
    print("Success to create gabor_texture")
    
    # Save the LBP image
    image_name1 = f'openCV_images/{meat_id}-{seqno}-lbp1-{i+1}.png'
    image_name2 = f'openCV_images/{meat_id}-{seqno}-lbp2-{i+1}.png'
    
    print(image_name1, image_name2)
    
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


def gabor_texture_analysis(s3_conn, image, id, seqno):
    img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

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
    pprint.pprint(features)
    print("Success to create gabor_texture")
    
    result = {}
    for i, response in enumerate(responses):
        image_name = f'openCV_images/{id}-{seqno}-garbor-{i+1}.png'
        image_path = ndarray_to_image(s3_conn, response, image_name)
        
        result[i+1] = {
            "images": image_path,
            "mean": float(features[i][0]),
            "std_dev": float(features[i][1]),
            "energy": float(features[i][2])
        }

    return result

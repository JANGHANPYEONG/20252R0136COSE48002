import cv2
import numpy as np
from sklearn.cluster import KMeans
from skimage.feature import greycomatrix, greycoprops, local_binary_pattern
import matplotlib.pyplot as plt
from PIL import Image
import io


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
    bucket_name = 'test-deeplant-bucket'  # 버킷 이름

    # 업로드
    s3_conn.upload_fileobj(buffer, bucket_name, image_name)

    # 업로드된 이미지의 URL 생성
    image_url = f"https://{bucket_name}.s3.amazonaws.com/{image_name}"
    
    return image_url


## ---------------- 단면 도출 ---------------- ##



## ---------------- 단백질, 지방 컬러팔레트 ---------------- ##
# 주어진 색상들 (RGB 형식)
protein_colors = [
    (202, 89, 72),
    (184, 74, 63),
    (166, 60, 53),
    (152, 47, 46),
    (139, 47, 44)
]

# 주어진 색상들 (RGB 형식)
fat_colors = [
    (254, 254, 238),
    (252, 247, 218),
    (248, 239, 200),
    (247, 230, 184),
    (243, 222, 168)
]


# 색상에 가장 가까운 색을 찾기 위한 함수
def find_closest_color(color, color_list):
    color = np.array(color)
    color_list = np.array(color_list)
    distances = np.sqrt(np.sum((color_list - color) ** 2, axis=1))
    return color_list[np.argmin(distances)]


# 이미지에서 색상 추출
def extract_protein_or_fat_palette_from_image(image_path, colors):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 주어진 색상 리스트를 기준으로 색상 추출
    palette = {}
    for color in colors:
        color = np.array(color)
        # 이미지에서 색상 차이를 최소화하는 색상 찾기
        closest_color = find_closest_color(color, image.reshape(-1, 3))
        palette[color] = closest_color.tolist()
        
    return palette


## ---------------- 전체 컬러팔레트 ---------------- ##
def create_total_color_palette(image, num_colors=10):
    # 이미지를 리쉐이프하여 색상 값을 2차원 배열로 변환
    pixels = image.reshape((-1, 3))

    # K-Means 클러스터링을 사용하여 주요 색상 추출
    kmeans = KMeans(n_clusters=num_colors + 10)  # 여유롭게 클러스터 수를 설정
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_
    labels = kmeans.labels_

    # 각 클러스터의 빈도 계산
    _, counts = np.unique(labels, return_counts=True)
    counts_sorted_indices = np.argsort(-counts)
    sorted_palette = colors[counts_sorted_indices]
    sorted_counts = counts[counts_sorted_indices]

    # 검정색 제거 (검정색의 기준을 설정, 예: RGB가 모두 50 이하인 경우)
    def is_black(color, threshold=50):
        return np.all(color <= threshold)

    filtered_palette = []
    filtered_proportions = []
    total_count = sum(sorted_counts)

    for color, count in zip(sorted_palette, sorted_counts):
        if not is_black(color):
            proportion = count / total_count
            filtered_palette.append(color)
            filtered_proportions.append(proportion)

        # 검정색을 제외한 색상의 수가 num_colors에 도달하면 중단
        if len(filtered_palette) >= num_colors:
            break

    # 필터링된 팔레트와 비율을 벡터 값으로 출력
    for i, (color, proportion) in enumerate(zip(filtered_palette, filtered_proportions)):
        print(f'Color #{i+1}: {color}, Proportion: {proportion*100:.2f}%')

    #색상 팔레트와 비율을 벡터 값으로 출력
    palette_list = {color: color.tolist() for color in filtered_palette}
    proportion_list = {proportion: float(proportion) for proportion in filtered_proportions}
    
    total_palette = {
        "palette": palette_list,
        "proportion": proportion_list
    }

    return total_palette


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

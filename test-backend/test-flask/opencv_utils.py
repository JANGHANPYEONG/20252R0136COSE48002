# Data manipulation and analysis
import pandas as pd
import numpy as np

# Image processing and computer vision
import cv2
from PIL import Image
from skimage.segmentation import slic, mark_boundaries
from skimage.util import img_as_float
from skimage.feature import greycomatrix, greycoprops, local_binary_pattern
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from scipy.spatial import KDTree, distance

# Machine learning
from sklearn.metrics import accuracy_score, r2_score
from sklearn.model_selection import StratifiedKFold, train_test_split

# PyTorch
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import timm

# MLflow
import mlflow
import mlflow.pytorch

# Image transformation and plotting
from torchvision import transforms
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize
import matplotlib.pyplot as plt

# Utility and progress bars
from tqdm import tqdm
import io
import random

# IPython for interactive display
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


## ---------------- 단면 도출 ---------------- ##



## ---------------- 단백질, 지방 컬러팔레트 ---------------- ##
palette = Colorpalette()

# 슈퍼픽셀로 컬러팔레트 도출 함수
def create_slic_color_palette(image, num_segments=256, num_colors=12):
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
    unique, counts = np.unique(labels, return_counts=True)
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

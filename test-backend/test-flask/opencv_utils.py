import os
import pprint

from flask import jsonify
import numpy as np
import boto3

import cv2
from PIL import Image
from skimage.segmentation import slic
from skimage.feature import graycomatrix, graycoprops, local_binary_pattern

import torch
from torch.utils.data import Dataset
from torchvision import transforms
from torch.cuda.amp import autocast
from torchvision.transforms import InterpolationMode

import mlflow
import mlflow.pytorch

import io
import gc

from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"


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


## ---------------- 모델 호출 ---------------- ##
def load_local_model(model_path):
    try:
        # 모델 파일이 존재하는지 확인
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model path does not exist: {model_path}")

        # GPU 사용 가능 여부 확인
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        # 모델 로드
        model = torch.load(model_path, map_location=device)
        
        # 메모리 정리
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        return model

    except Exception as e:
        print(f"Error loading model: {e}")
        return None


## ---------------- 단면 도출 ---------------- ##
torch.backends.cudnn.enabled = False
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

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


def extract_section_image(s3_image_object, meat_id, seqno):
    # 데이터셋 및 DataLoader 설정
    transform = SegmentationTransform(output_size=(448, 448))
    
    # 사전 학습된 모델 로드
    model_location = "/home/ubuntu/mlflow/segmentation_model/data/model.pth"
    model = load_local_model(model_location)
    
    model.eval()
    s3_bucket = os.getenv("S3_BUCKET_NAME")
    
    # S3에서 이미지 다운로드
    try:
        s3 = boto3.client(
                service_name="s3",
                region_name=os.getenv("S3_REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
        object_key = s3_image_object

        response = s3.get_object(Bucket=s3_bucket, Key=object_key)
        img = Image.open(io.BytesIO(response['Body'].read())).convert("RGB")
        print("Success to create Image Object")
    except Exception as e:
        raise Exception({"msg": f"Fail to create Image Object From S3. {str(e)}"})
    
    # 이미지 변환
    img_tensor, _ = transform(img, Image.new('L', img.size))
    img_tensor = img_tensor.unsqueeze(0)
    
    img_tensor = img_tensor.to(device)
    
    # 모델에 입력
    with autocast():
        output = model(img_tensor)
    
    # 마스크 생성 (U-Net 출력을 이진 마스크로 변환)
    mask = (output > 0.5).float().to(device)
    
    # 마스크 적용
    masked_img = apply_mask(img_tensor, mask)
    
    # # 224x224로 center crop
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

import cv2
import numpy as np
import matplotlib.pyplot as plt

#지방, 단백질의 기준 색상
red_colors = [
    (202, 89, 72),
    (184, 74, 63),
    (166, 60, 53),
    (152, 47, 46),
    (139, 47, 44)
]
white_colors = [
    (219, 188, 193), 
    (176, 165, 172), 
    (232, 211, 217),
    (217, 191, 192), 
    (243, 221, 221)
]

# 색상에 가장 가까운 색을 찾고 비율을 계산하는 함수
def find_closest_color_and_ratio(color, image):
    color = np.array(color)
    image_reshaped = image.reshape(-1, 3)
    
    # 색상 간 거리 계산
    distances = np.sqrt(np.sum((image_reshaped - color) ** 2, axis=1))
    
    # 최소 거리 색상 선택
    closest_color_idx = np.argmin(distances)
    closest_color = image_reshaped[closest_color_idx]
    
    # 해당 색상과 유사한 픽셀의 수 계산
    threshold = 100
    similar_pixels = np.sum(distances < threshold)
    
    # 전체 픽셀 수
    total_pixels = image_reshaped.shape[0]
    
    # 비율 계산
    ratio = similar_pixels / total_pixels
    return closest_color, ratio

#결과값 : (rgb값 + 비율)의 리스트
def extract_palette_and_ratios(image, colors):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    palette_and_ratios = []
    for color in colors:
        closest_color, ratio = find_closest_color_and_ratio(color, image)
        palette_and_ratios.append((closest_color.tolist(), ratio))
    
    return palette_and_ratios

#총합 비율과 컬러팔레트(리스트)를 구하는 함수
def display_palette_with_ratios(image):
    red_palette_and_ratios = extract_palette_and_ratios(image, red_colors)
    white_palette_and_ratios = extract_palette_and_ratios(image, white_colors)
    total_palette = red_palette_and_ratios + white_palette_and_ratios
    red_proportion = []
    white_proportion = []
    for red_color in total_palette[:5]:
        sum = 0
        sum += red_color[1]
        red_proportion.append(red_color)
    red_ratio = sum
    for white_color in total_palette[5:]:
        sum = 0
        sum += white_color[1]
        white_proportion.append(white_color)
    white_ratio = sum
    result = {
        "protein_rate": red_ratio,
        "fat_rate": white_ratio,
        "protein_palette": [red[0] for red in red_proportion],
        "fat_palette": [white[0] for white in white_proportion],
        "full_palette": total_palette
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

    # ROI가 비어있다면 관심영역을 전체로 판단
    if roi.size == 0:
        roi_reshaped = gray
    else:
        # roi를 2차원으로 변환
        roi_reshaped = np.zeros_like(gray)
        roi_reshaped[mask != 0] = roi

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
    
    lbp_image1 = ndarray_to_image(s3_conn, lbp1, image_name1)
    lbp_image2 = ndarray_to_image(s3_conn, lbp2, image_name2)
    
    lbp_result = {
        "lbp_images" : {
            "lbp1": lbp_image1,
            "lbp2": lbp_image2
        }
    }

    return lbp_result


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
    print("Success to create gabor_texture")
    
    tmp = {}
    final_result = {}
    for i, response in enumerate(responses):
        image_name = f'openCV_images/{id}-{seqno}-garbor-{i+1}.png'
        image_path = ndarray_to_image(s3_conn, response, image_name)
        
        tmp[i+1] = {
            "images": image_path,
            "mean": float(features[i][0]),
            "std_dev": float(features[i][1]),
            "energy": float(features[i][2])
        }
        
    final_result["gabor_images"] = tmp
    return final_result

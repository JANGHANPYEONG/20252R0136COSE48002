import torch
from torch.utils.data import Dataset
from torch.cuda.amp import autocast
from torchvision import transforms
from torchvision.transforms import InterpolationMode

import numpy as np

import boto3
import gc

import mlflow

import io
import os

from PIL import Image

import mlflow
import mlflow.pytorch

torch.backends.cudnn.enabled = False


def serve_mlflow():
    mlflow.set_tracking_uri("http://52.78.235.242:5000")
    print("Success to Set Mlflow Tracking Server")

    try:
        model = mlflow.pytorch.load_model("/home/ubuntu/mlflow/segmentation_model")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model = model.to(device)
        gc.collect()
        torch.cuda.empty_cache()
        print(f"Success to load model")
        return model
    except mlflow.exceptions.MlflowException as e:
        print(f"Error loading model: {e}")
        
        
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


def extract_section_image(s3_image_path, meat_id, seqno):
    # 데이터셋 및 DataLoader 설정
    transform = SegmentationTransform(output_size=(448, 448))
    
    # 사전 학습된 모델 로드
    run_id = "9130ebb6e0044fa7a7da800c786ecf48"
    model = serve_mlflow()
    
    model.eval()
    s3_bucket = "test-deeplant-bucket"
    
    # S3에서 이미지 다운로드
    if s3_bucket:
        s3 = boto3.client(
                service_name="s3",
                region_name=os.getenv("S3_REGION_NAME"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
        bucket_name = s3_bucket
        object_key = s3_image_path

        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        img = Image.open(io.BytesIO(response['Body'].read())).convert("RGB")
        print("Success to create Image Object")
        
    else:
        img = Image.open(s3_image_path).convert("RGB")
    
    # 이미지 변환
    img_tensor, _ = transform(img, Image.new('L', img.size))
    img_tensor = img_tensor.unsqueeze(0)
    print(img_tensor.shape)
    
    img_tensor = img_tensor.to(device)
    
    # 모델에 입력
    with autocast():
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


if __name__ == "__main__":
    s3_image_path = "sensory_evals/330bbd42bb77-0.png"
    result = extract_section_image(s3_image_path, "330bbd42bb77", 0)
    print(result)
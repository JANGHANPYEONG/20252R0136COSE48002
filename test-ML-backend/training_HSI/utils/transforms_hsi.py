import torch
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, List
import random


class HSIRandomCrop:
    """HSI 이미지 랜덤 크롭"""
    
    def __init__(self, size: Tuple[int, int]):
        self.size = size
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (C, H, W) 형태의 HSI 이미지
        """
        c, h, w = x.shape
        th, tw = self.size
        
        if h == th and w == tw:
            return x
        
        # 랜덤 시작점 선택
        i = random.randint(0, h - th)
        j = random.randint(0, w - tw)
        
        return x[:, i:i+th, j:j+tw]


class HSICenterCrop:
    """HSI 이미지 중앙 크롭 (재현성 보장)"""
    
    def __init__(self, size: Tuple[int, int]):
        self.size = size
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (C, H, W) 형태의 HSI 이미지
        """
        c, h, w = x.shape
        th, tw = self.size
        
        if h == th and w == tw:
            return x
        
        # 중앙 시작점 선택 (재현성 보장)
        i = (h - th) // 2
        j = (w - tw) // 2
        
        return x[:, i:i+th, j:j+tw]


class HSIRandomHorizontalFlip:
    """HSI 이미지 랜덤 수평 뒤집기"""
    
    def __init__(self, p: float = 0.5):
        self.p = p
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() < self.p:
            return torch.flip(x, dims=[2])  # W 차원 뒤집기
        return x


class HSIRandomVerticalFlip:
    """HSI 이미지 랜덤 수직 뒤집기"""
    
    def __init__(self, p: float = 0.5):
        self.p = p
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() < self.p:
            return torch.flip(x, dims=[1])  # H 차원 뒤집기
        return x


class HSIRandomRotation:
    """HSI 이미지 랜덤 회전"""
    
    def __init__(self, degrees: float = 10.0):
        self.degrees = degrees
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if self.degrees == 0:
            return x
        
        angle = random.uniform(-self.degrees, self.degrees)
        
        # 회전 행렬 계산
        angle_rad = np.radians(angle)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # 중심점 계산
        c, h, w = x.shape
        center_h, center_w = h // 2, w // 2
        
        # 회전된 좌표 계산
        device = x.device
        y_coords = torch.arange(h, device=device)
        x_coords = torch.arange(w, device=device)
        y_coords, x_coords = torch.meshgrid(y_coords, x_coords)  # indexing='ij' 제거
        
        # 중심점 기준으로 좌표 이동
        y_coords = y_coords - center_h
        x_coords = x_coords - center_w
        
        # 회전 적용
        new_y = cos_a * y_coords - sin_a * x_coords + center_h
        new_x = sin_a * y_coords + cos_a * x_coords + center_w
        
        # 그리드 샘플링을 위한 정규화된 좌표
        new_y = 2.0 * new_y / (h - 1) - 1.0
        new_x = 2.0 * new_x / (w - 1) - 1.0
        
        grid = torch.stack([new_x, new_y], dim=-1).unsqueeze(0)
        
        # (1, C, H, W)로 변환 후 한 번에 회전 적용
        x = x.unsqueeze(0)  # (1, C, H, W)
        rotated = F.grid_sample(
            x, grid, mode='bilinear', 
            padding_mode='reflection', align_corners=True
        )
        return rotated.squeeze(0)  # (C, H, W)


class HSINoise:
    """HSI 이미지에 노이즈 추가"""
    
    def __init__(self, std: float = 0.01):
        self.std = std
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if self.std == 0:
            return x
        
        noise = torch.randn_like(x) * self.std
        return x + noise


class HSIBrightnessContrast:
    """HSI 이미지 밝기/대비 조정"""
    
    def __init__(self, brightness_factor: float = 0.1, contrast_factor: float = 0.1):
        self.brightness_factor = brightness_factor
        self.contrast_factor = contrast_factor
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        # 밝기 조정
        if self.brightness_factor > 0:
            brightness = random.uniform(1 - self.brightness_factor, 1 + self.brightness_factor)
            x = x * brightness
        
        # 대비 조정
        if self.contrast_factor > 0:
            contrast = random.uniform(1 - self.contrast_factor, 1 + self.contrast_factor)
            mean = x.mean()
            x = (x - mean) * contrast + mean
        
        return x


class HSITransformCompose:
    """HSI transform 조합"""
    
    def __init__(self, transforms: List):
        self.transforms = transforms
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        for transform in self.transforms:
            x = transform(x)
        return x


def get_train_transforms(
    crop_size: Optional[Tuple[int, int]] = None,
    use_flip: bool = True,
    use_rotation: bool = True,
    use_noise: bool = True,
    use_brightness_contrast: bool = True
) -> HSITransformCompose:
    """훈련용 transform 생성"""
    
    transforms = []
    
    # 크롭
    if crop_size is not None:
        transforms.append(HSIRandomCrop(crop_size))
    
    # 뒤집기
    if use_flip:
        transforms.extend([
            HSIRandomHorizontalFlip(p=0.5),
            HSIRandomVerticalFlip(p=0.5)
        ])
    
    # 회전
    if use_rotation:
        transforms.append(HSIRandomRotation(degrees=10.0))
    
    # 노이즈
    if use_noise:
        transforms.append(HSINoise(std=0.01))
    
    # 밝기/대비
    if use_brightness_contrast:
        transforms.append(HSIBrightnessContrast(brightness_factor=0.1, contrast_factor=0.1))
    
    return HSITransformCompose(transforms)


def get_val_transforms(image_size: Tuple[int, int] = (256, 256)) -> HSITransformCompose:
    """검증용 transform 생성 (중앙 크롭으로 재현성 보장)"""
    return HSITransformCompose([HSICenterCrop(image_size)])


def get_test_transforms(image_size: Tuple[int, int] = (256, 256)) -> HSITransformCompose:
    """테스트용 transform 생성 (중앙 크롭으로 재현성 보장)"""
    return HSITransformCompose([HSICenterCrop(image_size)]) 
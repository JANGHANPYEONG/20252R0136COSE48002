import torch
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, List
import random
import math


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
    """HSI 이미지 중앙 크롭"""
    
    def __init__(self, size: Tuple[int, int]):
        self.size = size
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        c, h, w = x.shape
        th, tw = self.size
        
        if h == th and w == tw:
            return x
        
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
    
    def __init__(self, degrees: float = 15.0):  # 10도에서 15도로 증가
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
        y_coords, x_coords = torch.meshgrid(y_coords, x_coords, indexing='ij')
        
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
            x, grid, mode='bilinear',  # nearest에서 bilinear로 변경하여 더 부드러운 회전
            padding_mode='reflection', align_corners=True
        )
        return rotated.squeeze(0)  # (C, H, W)


class HSINoise:
    """HSI 이미지에 노이즈 추가"""
    
    def __init__(self, std: float = 0.02):  # 0.01에서 0.02로 증가
        self.std = std
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if self.std == 0:
            return x
        
        noise = torch.randn_like(x) * self.std
        return x + noise


class HSIBrightnessContrast:
    """HSI 이미지 밝기/대비 조정"""
    
    def __init__(self, brightness_factor: float = 0.15, contrast_factor: float = 0.15):  # 0.1에서 0.15로 증가
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


class HSIRandomErasing:
    """HSI 이미지 랜덤 지우기 (Cutout 효과)"""
    
    def __init__(self, p: float = 0.3, scale: Tuple[float, float] = (0.02, 0.33), ratio: Tuple[float, float] = (0.3, 3.3)):
        self.p = p
        self.scale = scale
        self.ratio = ratio
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() > self.p:
            return x
        
        c, h, w = x.shape
        
        # 지울 영역의 크기 계산
        area = h * w
        target_area = random.uniform(self.scale[0], self.scale[1]) * area
        aspect_ratio = random.uniform(self.ratio[0], self.ratio[1])
        
        h_erase = int(round(math.sqrt(target_area * aspect_ratio)))
        w_erase = int(round(math.sqrt(target_area / aspect_ratio)))
        
        if h_erase >= h or w_erase >= w:
            return x
        
        # 지울 위치 선택
        i = random.randint(0, h - h_erase)
        j = random.randint(0, w - w_erase)
        
        # 영역을 0으로 채우기
        x[:, i:i+h_erase, j:j+w_erase] = 0
        
        return x


class HSISpectralAugmentation:
    """HSI 스펙트럼 채널별 증강"""
    
    def __init__(self, p: float = 0.5, std: float = 0.01):
        self.p = p
        self.std = std
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() > self.p:
            return x
        
        c, h, w = x.shape
        # 각 채널에 대해 다른 노이즈 적용
        channel_noise = torch.randn(c, 1, 1) * self.std
        return x + channel_noise


class HSIGaussianBlur:
    """HSI 이미지 가우시안 블러"""
    
    def __init__(self, p: float = 0.3, kernel_size: int = 3, sigma: float = 0.5):
        self.p = p
        self.kernel_size = kernel_size
        self.sigma = sigma
    
    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() > self.p:
            return x
        
        # 가우시안 커널 생성
        kernel = self._get_gaussian_kernel(self.kernel_size, self.sigma)
        kernel = kernel.to(x.device)
        
        # 각 채널에 대해 블러 적용
        c, h, w = x.shape
        x_blurred = torch.zeros_like(x)
        
        for i in range(c):
            x_blurred[i] = F.conv2d(
                x[i:i+1].unsqueeze(0), 
                kernel.unsqueeze(0).unsqueeze(0),
                padding=self.kernel_size // 2
            ).squeeze()
        
        return x_blurred
    
    def _get_gaussian_kernel(self, kernel_size: int, sigma: float) -> torch.Tensor:
        """가우시안 커널 생성"""
        x = torch.arange(-(kernel_size // 2), kernel_size // 2 + 1)
        kernel = torch.exp(-(x ** 2) / (2 * sigma ** 2))
        kernel = kernel / kernel.sum()
        return kernel


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
    use_brightness_contrast: bool = True,
    use_erasing: bool = True,  # 새로운 옵션
    use_spectral_aug: bool = True,  # 새로운 옵션
    use_blur: bool = True  # 새로운 옵션
) -> HSITransformCompose:
    """훈련용 transform 생성 (강화된 버전)"""
    
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
    
    # 회전 (강화됨)
    if use_rotation:
        transforms.append(HSIRandomRotation(degrees=15.0))
    
    # 노이즈 (강화됨)
    if use_noise:
        transforms.append(HSINoise(std=0.02))
    
    # 밝기/대비 (강화됨)
    if use_brightness_contrast:
        transforms.append(HSIBrightnessContrast(brightness_factor=0.15, contrast_factor=0.15))
    
    # 스펙트럼 증강 (새로 추가)
    if use_spectral_aug:
        transforms.append(HSISpectralAugmentation(p=0.5, std=0.01))
    
    # 가우시안 블러 (새로 추가)
    if use_blur:
        transforms.append(HSIGaussianBlur(p=0.3, kernel_size=3, sigma=0.5))
    
    # 랜덤 지우기 (새로 추가)
    if use_erasing:
        transforms.append(HSIRandomErasing(p=0.3, scale=(0.02, 0.33), ratio=(0.3, 3.3)))
    
    return HSITransformCompose(transforms)


def get_val_transforms(image_size: Tuple[int, int] = (256, 256)) -> HSITransformCompose:
    """검증용 transform 생성 (중앙 크롭으로 재현성 보장)"""
    return HSITransformCompose([HSICenterCrop(image_size)])


def get_test_transforms(image_size: Tuple[int, int] = (256, 256)) -> HSITransformCompose:
    """테스트용 transform 생성 (중앙 크롭으로 재현성 보장)"""
    return HSITransformCompose([HSICenterCrop(image_size)]) 
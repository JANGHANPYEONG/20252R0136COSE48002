"""
HSI 전용 데이터 증강/전처리 연산들을 모아둔 모듈.

크롭, 노이즈, 정규화 등 PyTorch 텐서 기반 변환 클래스를 제공한다.
"""

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
            x, grid, mode='nearest', 
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


class HSIChannelShuffle:
    """채널 순서를 랜덤하게 섞기 (파장 채널만)"""

    def __init__(self, p: float = 0.3, rgb_channels: int = 3):
        self.p = p
        self.rgb_channels = rgb_channels

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape
        if c <= self.rgb_channels:  # RGB만 있는 경우는 섞지 않음
            return x

        # 파장 채널과 RGB 채널 분리
        wavelength_channels = c - self.rgb_channels
        wavelength_part = x[:wavelength_channels]  # 파장 채널
        rgb_part = x[wavelength_channels:]  # RGB 채널

        # 파장 채널만 섞기
        indices = torch.randperm(wavelength_channels)
        shuffled_wavelength = wavelength_part[indices]

        # 다시 결합
        return torch.cat([shuffled_wavelength, rgb_part], dim=0)


class HSIChannelDropout:
    """파장 채널을 랜덤하게 제거 (마스킹)"""

    def __init__(self, p: float = 0.1, max_dropout_ratio: float = 0.3, rgb_channels: int = 3):
        self.p = p
        self.max_dropout_ratio = max_dropout_ratio
        self.rgb_channels = rgb_channels

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape
        if c <= self.rgb_channels:  # RGB만 있는 경우는 드롭아웃하지 않음
            return x

        wavelength_channels = c - self.rgb_channels
        max_dropout = max(1, int(wavelength_channels * self.max_dropout_ratio))
        num_dropout = random.randint(1, max_dropout)

        # 드롭아웃할 채널 선택
        dropout_indices = random.sample(range(wavelength_channels), num_dropout)

        # 해당 채널을 0으로 설정
        x_copy = x.clone()
        for idx in dropout_indices:
            x_copy[idx] = 0

        return x_copy


class HSISpectralMixup:
    """인접 파장 채널들을 선형 조합"""

    def __init__(self, p: float = 0.2, alpha: float = 0.3, rgb_channels: int = 3):
        self.p = p
        self.alpha = alpha
        self.rgb_channels = rgb_channels

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape
        wavelength_channels = c - self.rgb_channels

        if wavelength_channels < 2:  # 파장 채널이 2개 미만이면 적용하지 않음
            return x

        # 인접한 두 채널 선택
        idx1 = random.randint(0, wavelength_channels - 2)
        idx2 = idx1 + 1

        # 선형 조합 계수
        lam = np.random.beta(self.alpha, self.alpha)

        # 믹스업 적용
        x_copy = x.clone()
        x_copy[idx1] = lam * x[idx1] + (1 - lam) * x[idx2]
        x_copy[idx2] = lam * x[idx2] + (1 - lam) * x[idx1]

        return x_copy


class HSIElasticDeformation:
    """탄성 변형 (Elastic Deformation)"""

    def __init__(self, p: float = 0.2, alpha: float = 1, sigma: float = 50):
        self.p = p
        self.alpha = alpha
        self.sigma = sigma

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape

        # 이미지 크기에 맞게 알파값 조정
        alpha_scaled = self.alpha * min(h, w) / 224.0  # 224를 기준으로 스케일링

        # 랜덤 변위 생성 (더 작은 크기로)
        displacement_h = max(h // 4, 16)  # 최소 16, 최대 이미지 높이의 1/4
        displacement_w = max(w // 4, 16)  # 최소 16, 최대 이미지 너비의 1/4

        dx = torch.randn(displacement_h, displacement_w) * alpha_scaled
        dy = torch.randn(displacement_h, displacement_w) * alpha_scaled

        # 원본 크기로 업샘플링
        dx = F.interpolate(dx.unsqueeze(0).unsqueeze(0), size=(h, w), mode='bilinear', align_corners=False)
        dy = F.interpolate(dy.unsqueeze(0).unsqueeze(0), size=(h, w), mode='bilinear', align_corners=False)

        dx = dx.squeeze(0).squeeze(0)  # (h, w)
        dy = dy.squeeze(0).squeeze(0)  # (h, w)

        # 시그마도 이미지 크기에 맞게 조정
        sigma_scaled = self.sigma * min(h, w) / 224.0

        # 가우시안 스무딩 (안전한 크기로)
        if sigma_scaled > 1.0:
            kernel = self._gaussian_kernel(sigma_scaled).to(x.device)
            kernel_size = kernel.shape[-1]
            padding = kernel_size // 2

            dx = F.conv2d(dx.unsqueeze(0).unsqueeze(0), kernel, padding=padding)
            dy = F.conv2d(dy.unsqueeze(0).unsqueeze(0), kernel, padding=padding)

            dx = dx.squeeze(0).squeeze(0)
            dy = dy.squeeze(0).squeeze(0)

        # 그리드 생성
        y_coords, x_coords = torch.meshgrid(torch.arange(h, device=x.device),
                                          torch.arange(w, device=x.device), indexing='ij')
        y_coords = y_coords.float() + dy
        x_coords = x_coords.float() + dx

        # 정규화
        x_coords = 2.0 * x_coords / (w - 1) - 1.0
        y_coords = 2.0 * y_coords / (h - 1) - 1.0

        grid = torch.stack([x_coords, y_coords], dim=-1).unsqueeze(0)

        # 변형 적용
        x = x.unsqueeze(0)
        deformed = F.grid_sample(x, grid, mode='bilinear', padding_mode='reflection', align_corners=True)
        return deformed.squeeze(0)

    def _gaussian_kernel(self, sigma):
        size = int(6 * sigma + 1)
        if size % 2 == 0:
            size += 1

        kernel = torch.exp(-0.5 * (torch.arange(-size//2 + 1, size//2 + 1).float() / sigma) ** 2)
        kernel = kernel.unsqueeze(0) * kernel.unsqueeze(1)
        kernel = kernel / kernel.sum()
        return kernel.unsqueeze(0).unsqueeze(0)


class HSIRandomCutout:
    """랜덤 영역을 마스킹하여 모델의 robustness 향상"""

    def __init__(self, p: float = 0.3, max_holes: int = 3, max_h_size: int = 32, max_w_size: int = 32):
        self.p = p
        self.max_holes = max_holes
        self.max_h_size = max_h_size
        self.max_w_size = max_w_size

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape
        x = x.clone()

        num_holes = random.randint(1, self.max_holes)
        for _ in range(num_holes):
            # 구멍 크기 결정 (이미지 크기에 비례)
            hole_h = random.randint(8, min(self.max_h_size, h // 4))
            hole_w = random.randint(8, min(self.max_w_size, w // 4))

            # 구멍 위치 결정
            y = random.randint(0, h - hole_h)
            x_pos = random.randint(0, w - hole_w)

            # 구멍 생성 (평균값으로 채우기)
            mean_val = x[:, y:y+hole_h, x_pos:x_pos+hole_w].mean()
            x[:, y:y+hole_h, x_pos:x_pos+hole_w] = mean_val

        return x


class HSIRandomPatch:
    """랜덤 패치를 다른 위치로 이동시키는 증강"""

    def __init__(self, p: float = 0.25, max_patches: int = 2, patch_size: int = 32):
        self.p = p
        self.max_patches = max_patches
        self.patch_size = patch_size

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape
        x = x.clone()

        num_patches = random.randint(1, self.max_patches)
        for _ in range(num_patches):
            # 패치 크기 조정
            patch_h = min(self.patch_size, h // 6)
            patch_w = min(self.patch_size, w // 6)

            if patch_h < 8 or patch_w < 8:  # 너무 작으면 건너뛰기
                continue

            # 소스 위치
            src_y = random.randint(0, h - patch_h)
            src_x = random.randint(0, w - patch_w)

            # 타겟 위치
            dst_y = random.randint(0, h - patch_h)
            dst_x = random.randint(0, w - patch_w)

            # 패치 복사
            patch = x[:, src_y:src_y+patch_h, src_x:src_x+patch_w].clone()
            x[:, dst_y:dst_y+patch_h, dst_x:dst_x+patch_w] = patch

        return x


class HSIRandomScale:
    """랜덤 스케일 변화 + 크롭/패딩"""

    def __init__(self, p: float = 0.4, scale_range: tuple = (0.8, 1.2)):
        self.p = p
        self.scale_min, self.scale_max = scale_range

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape
        scale = random.uniform(self.scale_min, self.scale_max)

        # 새로운 크기 계산
        new_h = int(h * scale)
        new_w = int(w * scale)

        # 리사이즈
        x_resized = F.interpolate(x.unsqueeze(0), size=(new_h, new_w), mode='bilinear', align_corners=False)
        x_resized = x_resized.squeeze(0)

        # 원본 크기로 맞추기 (크롭 또는 패딩)
        if scale > 1.0:  # 크기가 커진 경우 - 크롭
            start_h = (new_h - h) // 2
            start_w = (new_w - w) // 2
            x_final = x_resized[:, start_h:start_h+h, start_w:start_w+w]
        else:  # 크기가 작아진 경우 - 패딩
            pad_h = (h - new_h) // 2
            pad_w = (w - new_w) // 2
            pad_h_extra = h - new_h - pad_h
            pad_w_extra = w - new_w - pad_w

            # reflection 패딩 사용
            x_final = F.pad(x_resized, (pad_w, pad_w_extra, pad_h, pad_h_extra), mode='reflect')

        return x_final


class HSIMixUp:
    """MixUp 증강 - 두 이미지를 선형 조합"""

    def __init__(self, p: float = 0.2, alpha: float = 0.4):
        self.p = p
        self.alpha = alpha

    def __call__(self, x: torch.Tensor, other_sample=None) -> torch.Tensor:
        # 주의: 이 증강은 배치 레벨에서 처리해야 하므로 일단 패스
        # 추후 trainer에서 구현 가능
        return x


class HSIColorJitter:
    """HSI 이미지를 위한 색상 변화"""

    def __init__(self, p: float = 0.6, hue_factor: float = 0.1, saturation_factor: float = 0.2):
        self.p = p
        self.hue_factor = hue_factor
        self.saturation_factor = saturation_factor

    def __call__(self, x: torch.Tensor) -> torch.Tensor:
        if random.random() >= self.p:
            return x

        c, h, w = x.shape

        # RGB 채널이 있다고 가정 (마지막 3채널)
        if c >= 3:
            # RGB 부분에만 색상 변화 적용
            rgb_channels = x[-3:]  # 마지막 3채널
            other_channels = x[:-3] if c > 3 else torch.empty(0, h, w)

            # 색상 변화 적용
            if self.hue_factor > 0:
                hue_shift = random.uniform(-self.hue_factor, self.hue_factor)
                # 간단한 색상 순환
                rgb_shifted = torch.roll(rgb_channels, shifts=int(hue_shift * 3), dims=0)
            else:
                rgb_shifted = rgb_channels

            if self.saturation_factor > 0:
                saturation = random.uniform(1 - self.saturation_factor, 1 + self.saturation_factor)
                gray = rgb_shifted.mean(dim=0, keepdim=True)
                rgb_shifted = saturation * rgb_shifted + (1 - saturation) * gray

            # 재결합
            if len(other_channels) > 0:
                x = torch.cat([other_channels, rgb_shifted], dim=0)
            else:
                x = rgb_shifted

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
    use_brightness_contrast: bool = True,
    use_advanced_aug: bool = True
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

    # 고급 증강 기법들 (강화된 버전)
    if use_advanced_aug:
        transforms.extend([
            # 기존 스펙트럴 증강
            HSIChannelShuffle(p=0.3, rgb_channels=3),           # 채널 순서 섞기 (확률 증가)
            HSIChannelDropout(p=0.25, max_dropout_ratio=0.3),   # 채널 드롭아웃 (더 강화)
            HSISpectralMixup(p=0.2, alpha=0.4),                 # 스펙트럴 믹스업 (더 강화)

            # 새로운 공간적 증강
            HSIRandomCutout(p=0.4, max_holes=3, max_h_size=40, max_w_size=40),  # 랜덤 마스킹
            HSIRandomPatch(p=0.3, max_patches=2, patch_size=40),                # 패치 이동
            HSIRandomScale(p=0.35, scale_range=(0.75, 1.25)),                  # 스케일 변화

            # 색상 및 기하학적 증강
            HSIColorJitter(p=0.5, hue_factor=0.15, saturation_factor=0.25),    # 색상 변화
            HSIElasticDeformation(p=0.2, alpha=2, sigma=30)                     # 탄성 변형 (수정된 버전)
        ])

    # 노이즈
    if use_noise:
        transforms.append(HSINoise(std=0.01))

    # 밝기/대비
    if use_brightness_contrast:
        transforms.append(HSIBrightnessContrast(brightness_factor=0.15, contrast_factor=0.15))

    return HSITransformCompose(transforms)


def get_val_transforms(image_size: Tuple[int, int] = (256, 256)) -> HSITransformCompose:
    """검증용 transform 생성 (중앙 크롭으로 재현성 보장)"""
    return HSITransformCompose([HSICenterCrop(image_size)])


def get_test_transforms(image_size: Tuple[int, int] = (256, 256)) -> HSITransformCompose:
    """테스트용 transform 생성 (중앙 크롭으로 재현성 보장)"""
    return HSITransformCompose([HSICenterCrop(image_size)]) 

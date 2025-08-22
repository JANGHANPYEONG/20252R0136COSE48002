"""
RGB 이미지 변환 모듈

이 모듈은 RGB 이미지 학습을 위한 변환 함수들을 제공합니다.
ImageNet 정규화를 적용하며, 학습/검증/테스트에 적합한 변환을 제공합니다.
"""

import torch
import torchvision.transforms as transforms
from typing import Tuple, List


def get_train_transforms(image_size: Tuple[int, int], aug: bool = True) -> transforms.Compose:
    """
    학습용 이미지 변환을 생성합니다.
    
    Args:
        image_size: (height, width) 튜플
        aug: 데이터 증강 적용 여부
        
    Returns:
        transforms.Compose: 학습용 변환 파이프라인
    """
    transform_list = []
    
    # 리사이즈 및 크롭
    if aug:
        # 학습 시: 랜덤 크롭 후 리사이즈
        transform_list.extend([
            transforms.RandomResizedCrop(
                size=image_size,
                scale=(0.8, 1.0),
                ratio=(0.75, 1.33)
            )
        ])
    else:
        # 증강 없음: 중앙 크롭 후 리사이즈
        transform_list.extend([
            transforms.Resize(image_size),
            transforms.CenterCrop(image_size)
        ])
    
    # 데이터 증강 (aug=True일 때만)
    if aug:
        transform_list.extend([
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomVerticalFlip(p=0.3),
            transforms.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1
            ),
            transforms.RandomRotation(degrees=15)
        ])
    
    # 텐서 변환 및 정규화
    transform_list.extend([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet 평균
            std=[0.229, 0.224, 0.225]    # ImageNet 표준편차
        )
    ])
    
    return transforms.Compose(transform_list)


def get_val_transforms(image_size: Tuple[int, int]) -> transforms.Compose:
    """
    검증용 이미지 변환을 생성합니다.
    
    Args:
        image_size: (height, width) 튜플
        
    Returns:
        transforms.Compose: 검증용 변환 파이프라인
    """
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet 평균
            std=[0.229, 0.224, 0.225]    # ImageNet 표준편차
        )
    ])


def get_test_transforms(image_size: Tuple[int, int]) -> transforms.Compose:
    """
    테스트용 이미지 변환을 생성합니다.
    
    Args:
        image_size: (height, width) 튜플
        
    Returns:
        transforms.Compose: 테스트용 변환 파이프라인
    """
    return transforms.Compose([
        transforms.Resize(image_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet 평균
            std=[0.229, 0.224, 0.225]    # ImageNet 표준편차
        )
    ])


def denormalize(tensor: torch.Tensor) -> torch.Tensor:
    """
    정규화된 텐서를 원래 값 범위로 되돌립니다.
    
    Args:
        tensor: 정규화된 텐서 (C, H, W)
        
    Returns:
        torch.Tensor: 원래 값 범위의 텐서 (0~1)
    """
    mean = torch.tensor([0.485, 0.456, 0.406]).view(-1, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(-1, 1, 1)
    
    if tensor.device != mean.device:
        mean = mean.to(tensor.device)
        std = std.to(tensor.device)
    
    return tensor * std + mean


def get_inverse_transforms() -> transforms.Compose:
    """
    정규화를 되돌리는 변환을 생성합니다.
    
    Returns:
        transforms.Compose: 역정규화 변환 파이프라인
    """
    return transforms.Compose([
        transforms.Lambda(lambda x: denormalize(x)),
        transforms.Lambda(lambda x: torch.clamp(x, 0, 1))
    ])

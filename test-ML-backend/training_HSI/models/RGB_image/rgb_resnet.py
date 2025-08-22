"""
RGB ResNet 모델 생성 모듈

이 모듈은 RGB 이미지 분류/회귀를 위한 ResNet 모델을 생성합니다.
torchvision의 resnet18을 기반으로 하며, in_channels와 num_classes를 설정할 수 있습니다.
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Dict, Any


def create_model(config: Dict[str, Any]) -> nn.Module:
    """
    설정에 따라 RGB ResNet 모델을 생성합니다.
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        nn.Module: 생성된 ResNet 모델
        
    Raises:
        ValueError: 필수 설정이 누락된 경우
    """
    model_config = config.get('model', {})
    parameters = model_config.get('parameters', {})
    
    # 필수 파라미터 확인
    if 'num_classes' not in model_config:
        raise ValueError("Config에 'model.num_classes'가 지정되지 않았습니다.")
    
    num_classes = model_config['num_classes']
    in_channels = parameters.get('in_channels', 3)
    pretrained = parameters.get('pretrained', True)
    
    # ResNet18 모델 생성
    if pretrained:
        model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    else:
        model = models.resnet18(weights=None)
    
    # in_channels가 3이 아닌 경우 첫 번째 컨볼루션 레이어 교체
    if in_channels != 3:
        original_conv1 = model.conv1
        new_conv1 = nn.Conv2d(
            in_channels, 
            original_conv1.out_channels, 
            kernel_size=original_conv1.kernel_size,
            stride=original_conv1.stride,
            padding=original_conv1.padding,
            bias=original_conv1.bias is not None
        )
        
        # 가중치 초기화 (3채널 가중치를 in_channels로 확장)
        if pretrained:
            with torch.no_grad():
                # 3채널 가중치를 평균하여 새로운 채널에 복사
                original_weight = original_conv1.weight
                new_weight = new_conv1.weight
                
                # 3채널 가중치의 평균을 계산
                avg_weight = original_weight.mean(dim=1, keepdim=True)
                
                # 새로운 채널에 가중치 할당
                for i in range(in_channels):
                    if i < 3:
                        new_weight[:, i] = original_weight[:, i]
                    else:
                        new_weight[:, i] = avg_weight.squeeze(1)
                
                new_conv1.weight.copy_(new_weight)
        
        model.conv1 = new_conv1
    
    # 마지막 fully connected 레이어 교체
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    print(f"RGB ResNet 모델 생성 완료:")
    print(f"  - in_channels: {in_channels}")
    print(f"  - num_classes: {num_classes}")
    print(f"  - pretrained: {pretrained}")
    
    return model


def create_hsi_resnet_model(config: Dict[str, Any]) -> nn.Module:
    """
    기존 HSI 호환성을 위한 함수 (deprecated)
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        nn.Module: 생성된 ResNet 모델
    """
    print("Warning: create_hsi_resnet_model is deprecated. Use create_model instead.")
    return create_model(config)

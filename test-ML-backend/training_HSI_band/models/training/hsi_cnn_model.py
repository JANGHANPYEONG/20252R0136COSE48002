import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any

class HSICNN(nn.Module):
    """HSI 이미지 입력을 위한 CNN 모델"""
    
    def __init__(self, num_bands: int, num_classes: int, image_size: tuple = (256, 256)):
        """
        Args:
            num_bands: 스펙트럴 밴드 수
            num_classes: 분류할 클래스 수
            image_size: 이미지 크기 (H, W)
        """
        super(HSICNN, self).__init__()
        
        self.num_bands = num_bands
        self.num_classes = num_classes
        self.image_size = image_size
        
        # 입력: [batch_size, num_bands, H, W]
        
        # 첫 번째 컨볼루션 블록
        self.conv1 = nn.Conv2d(num_bands, 32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        # 두 번째 컨볼루션 블록
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        # 세 번째 컨볼루션 블록
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        # 네 번째 컨볼루션 블록
        self.conv4 = nn.Conv2d(128, 256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.pool4 = nn.MaxPool2d(2, 2)
        
        # 풀링 후 특징 맵 크기 계산
        h_out = image_size[0] // 16  # 4번의 풀링 (2^4 = 16)
        w_out = image_size[1] // 16
        
        # 전역 평균 풀링
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # 분류기
        self.classifier = nn.Sequential(
            nn.Linear(256, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
            nn.Sigmoid()  # 멀티라벨 분류를 위해 Sigmoid 사용
        )
        
    def forward(self, x):
        """
        Args:
            x: 입력 이미지 [batch_size, num_bands, H, W]
            
        Returns:
            output: 분류 결과 [batch_size, num_classes]
        """
        # 컨볼루션 블록들
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = self.pool4(F.relu(self.bn4(self.conv4(x))))
        
        # 전역 평균 풀링
        x = self.global_pool(x)
        
        # 평탄화
        x = x.view(x.size(0), -1)
        
        # 분류
        x = self.classifier(x)
        
        return x

class HSICNNResNet(nn.Module):
    """ResNet 스타일의 HSI CNN 모델"""
    
    def __init__(self, num_bands: int, num_classes: int, image_size: tuple = (256, 256)):
        """
        Args:
            num_bands: 스펙트럴 밴드 수
            num_classes: 분류할 클래스 수
            image_size: 이미지 크기 (H, W)
        """
        super(HSICNNResNet, self).__init__()
        
        self.num_bands = num_bands
        self.num_classes = num_classes
        self.image_size = image_size
        
        # 초기 컨볼루션
        self.conv1 = nn.Conv2d(num_bands, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.pool1 = nn.MaxPool2d(3, stride=2, padding=1)
        
        # ResNet 블록들
        self.layer1 = self._make_layer(64, 64, 2)
        self.layer2 = self._make_layer(64, 128, 2, stride=2)
        self.layer3 = self._make_layer(128, 256, 2, stride=2)
        self.layer4 = self._make_layer(256, 512, 2, stride=2)
        
        # 전역 평균 풀링
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        
        # 분류기
        self.classifier = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes),
            nn.Sigmoid()
        )
        
    def _make_layer(self, in_channels, out_channels, blocks, stride=1):
        """ResNet 블록 생성"""
        layers = []
        
        # 첫 번째 블록 (stride 적용)
        layers.append(ResBlock(in_channels, out_channels, stride))
        
        # 나머지 블록들
        for _ in range(1, blocks):
            layers.append(ResBlock(out_channels, out_channels))
            
        return nn.Sequential(*layers)
    
    def forward(self, x):
        """
        Args:
            x: 입력 이미지 [batch_size, num_bands, H, W]
            
        Returns:
            output: 분류 결과 [batch_size, num_classes]
        """
        # 초기 컨볼루션
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        
        # ResNet 블록들
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        # 전역 평균 풀링
        x = self.global_pool(x)
        
        # 평탄화
        x = x.view(x.size(0), -1)
        
        # 분류
        x = self.classifier(x)
        
        return x

class ResBlock(nn.Module):
    """ResNet 블록"""
    
    def __init__(self, in_channels, out_channels, stride=1):
        super(ResBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                              stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                              stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        # shortcut connection
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1,
                         stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
    
    def forward(self, x):
        residual = x
        
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        
        out += self.shortcut(residual)
        out = F.relu(out)
        
        return out

def create_model(model_name: str, config: Dict) -> nn.Module:
    """모델을 생성합니다."""
    
    # 데이터셋 정보
    num_bands = len(config.get('wavelengths', [10, 60, 70, 100, 110]))
    num_classes = len(config.get('label_columns', []))
    image_size = tuple(config.get('image_size', [256, 256]))
    
    if model_name == 'hsi_cnn':
        model = HSICNN(num_bands, num_classes, image_size)
    elif model_name == 'hsi_cnn_resnet':
        model = HSICNNResNet(num_bands, num_classes, image_size)
    else:
        raise ValueError(f"Unknown model name: {model_name}")
    
    return model 
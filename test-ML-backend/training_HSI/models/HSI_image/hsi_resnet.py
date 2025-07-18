import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, Any


class BasicBlock(nn.Module):
    """ResNet 기본 블록"""
    
    def __init__(self, in_channels, out_channels, stride=1, downsample=None):
        super(BasicBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.downsample = downsample
        
    def forward(self, x):
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        if self.downsample is not None:
            identity = self.downsample(x)
        
        out += identity
        out = self.relu(out)
        
        return out


class HSIResNet(nn.Module):
    """HSI용 ResNet 모델"""
    
    def __init__(self, in_channels, num_classes, block=BasicBlock, layers=[2, 2, 2, 2]):
        """
        Args:
            in_channels: 입력 채널 수 (파장 수)
            num_classes: 출력 클래스 수
            block: 사용할 블록 타입
            layers: 각 레이어의 블록 수
        """
        super(HSIResNet, self).__init__()
        
        self.in_channels = in_channels
        self.num_classes = num_classes
        
        # 초기 컨볼루션 레이어
        self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        
        # ResNet 레이어들
        self.layer1 = self._make_layer(block, 64, 64, layers[0])
        self.layer2 = self._make_layer(block, 64, 128, layers[1], stride=2)
        self.layer3 = self._make_layer(block, 128, 256, layers[2], stride=2)
        self.layer4 = self._make_layer(block, 256, 512, layers[3], stride=2)
        
        # 분류 헤드
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc = nn.Linear(512, num_classes)
        
        # 가중치 초기화
        self._initialize_weights()
    
    def _make_layer(self, block, in_channels, out_channels, blocks, stride=1):
        """ResNet 레이어를 생성합니다."""
        downsample = None
        if stride != 1 or in_channels != out_channels:
            downsample = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        
        layers = []
        layers.append(block(in_channels, out_channels, stride, downsample))
        for _ in range(1, blocks):
            layers.append(block(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def _initialize_weights(self):
        """가중치를 초기화합니다."""
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        # 초기 레이어
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        # ResNet 레이어들
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        # 분류 헤드
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.fc(x)
        
        return x


def create_hsi_resnet_model(config: Dict[str, Any]) -> HSIResNet:
    """
    설정에 따라 HSI ResNet 모델을 생성합니다.
    
    Args:
        config: 설정 딕셔너리
    
    Returns:
        HSIResNet 모델
    """
    # 컬럼 설정에서 파장 수 추출
    column_config_path = config['data']['column_config']
    with open(column_config_path, 'r') as f:
        import json
        column_config = json.load(f)
    
    in_channels = len(column_config['wavelengths'])
    num_classes = config['model']['num_classes']
    
    print(f"Creating HSI ResNet model:")
    print(f"  Input channels (wavelengths): {in_channels}")
    print(f"  Number of classes: {num_classes}")
    
    model = HSIResNet(in_channels=in_channels, num_classes=num_classes)
    
    return model


def get_model_info(model: HSIResNet) -> Dict[str, Any]:
    """모델 정보를 반환합니다."""
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        'total_parameters': total_params,
        'trainable_parameters': trainable_params,
        'input_channels': model.in_channels,
        'num_classes': model.num_classes
    } 
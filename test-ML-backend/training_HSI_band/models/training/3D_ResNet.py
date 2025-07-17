import torch
import torch.nn as nn
import torch.nn.functional as F

class BasicBlock3D(nn.Module):
    """
    3D ResNet의 기본 블록 (논문의 BasicBlock 구조)
    
    구조:
    Conv3×3×3 → BN → ReLU → Conv3×3×3 → BN → +skip connection → ReLU
    """
    expansion = 1
    
    def __init__(self, in_planes, planes, stride=1, downsample=None):
        super(BasicBlock3D, self).__init__()
        
        # 첫 번째 3D Convolution
        self.conv1 = nn.Conv3d(
            in_planes, planes, 
            kernel_size=3, stride=stride, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm3d(planes)
        
        # 두 번째 3D Convolution
        self.conv2 = nn.Conv3d(
            planes, planes,
            kernel_size=3, stride=1, padding=1, bias=False
        )
        self.bn2 = nn.BatchNorm3d(planes)
        
        # Skip connection을 위한 downsample
        self.downsample = downsample
        self.stride = stride
        
    def forward(self, x):
        # 입력을 skip connection을 위해 저장
        identity = x
        
        # 첫 번째 conv block
        out = self.conv1(x)
        out = self.bn1(out)
        out = F.relu(out)
        
        # 두 번째 conv block
        out = self.conv2(out)
        out = self.bn2(out)
        
        # Skip connection
        if self.downsample is not None:
            identity = self.downsample(x)
            
        out += identity
        out = F.relu(out)
        
        return out


class ResNet3D(nn.Module):
    """
    논문에서 사용한 18층 3D ResNet 구조
    
    네트워크 구조:
    1. 초기 Conv3D → BatchNorm → ReLU → MaxPool
    2. 4개의 residual layer (각각 2개의 BasicBlock)
    3. Global Average Pooling
    4. Fully Connected Layer (회귀: 1, 분류: num_classes)
    """
    
    def __init__(self, config: dict):
        super(ResNet3D, self).__init__()
        
        # 설정 파라미터
        self.num_classes = config.get('num_classes', 1)  # 회귀: 1, 분류: 클래스 수
        self.input_bands = config.get('input_bands', 140)  # 입력 밴드 수
        self.task_type = config.get('task_type', 'regression')  # 'regression' or 'classification'
        
        # ResNet-18 구조: [2, 2, 2, 2] (각 layer당 block 수)
        self.layers = [2, 2, 2, 2]
        self.in_planes = 64
        
        # 논문의 초기 처리: Conv3D → BatchNorm → ReLU → MaxPool
        self.initial_conv = nn.Conv3d(
            1, 64,  # 입력: 1채널 (HSI cube), 출력: 64채널
            kernel_size=(7, 7, 7), stride=(2, 2, 2), padding=(3, 3, 3), bias=False
        )
        self.initial_bn = nn.BatchNorm3d(64)
        self.initial_relu = nn.ReLU(inplace=True)
        self.initial_maxpool = nn.MaxPool3d(
            kernel_size=(3, 3, 3), stride=(2, 2, 2), padding=(1, 1, 1)
        )
        
        # ResNet Layers (논문의 Residual Blocks)
        self.layer1 = self._make_layer(BasicBlock3D, 64, self.layers[0], stride=1)
        self.layer2 = self._make_layer(BasicBlock3D, 128, self.layers[1], stride=2)
        self.layer3 = self._make_layer(BasicBlock3D, 256, self.layers[2], stride=2)
        self.layer4 = self._make_layer(BasicBlock3D, 512, self.layers[3], stride=2)
        
        # 논문의 평균 풀링: 전체 피처를 압축하여 벡터화
        self.avgpool = nn.AdaptiveAvgPool3d((1, 1, 1))
        
        # 논문의 출력 계층
        if self.task_type == 'regression':
            # 회귀: 출력 크기 1 (SPAD 값 예측)
            self.fc = nn.Linear(512 * BasicBlock3D.expansion, 1)
        else:
            # 분류: 출력 크기 = 클래스 수 (가뭄 스트레스 분류)
            self.fc = nn.Linear(512 * BasicBlock3D.expansion, self.num_classes)
        
        # 가중치 초기화
        self._initialize_weights()
    
    def _make_layer(self, block, planes, blocks, stride=1):
        """
        ResNet layer 생성 (여러 개의 BasicBlock으로 구성)
        """
        downsample = None
        
        # Stride가 1이 아니거나 입력/출력 채널이 다른 경우 downsample 필요
        if stride != 1 or self.in_planes != planes * block.expansion:
            downsample = nn.Sequential(
                nn.Conv3d(
                    self.in_planes, planes * block.expansion,
                    kernel_size=1, stride=stride, bias=False
                ),
                nn.BatchNorm3d(planes * block.expansion)
            )
        
        layers = []
        # 첫 번째 블록 (stride 적용)
        layers.append(block(self.in_planes, planes, stride, downsample))
        self.in_planes = planes * block.expansion
        
        # 나머지 블록들 (stride=1)
        for _ in range(1, blocks):
            layers.append(block(self.in_planes, planes))
            
        return nn.Sequential(*layers)
    
    def _initialize_weights(self):
        """
        논문에서 사용한 가중치 초기화 방식
        """
        for m in self.modules():
            if isinstance(m, nn.Conv3d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm3d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
    
    def forward(self, x):
        """
        순전파 과정
        
        Args:
            x: Band attention이 적용된 HSI 데이터 (B, H, W, D)
        Returns:
            output: 예측 결과 (회귀: (B, 1), 분류: (B, num_classes))
        """
        # 입력 데이터 형태 변환: (B, H, W, D) → (B, 1, H, W, D)
        # 3D CNN을 위해 채널 차원 추가
        if x.dim() == 4:
            x = x.unsqueeze(1)  # (B, H, W, D) → (B, 1, H, W, D)
        
        # 논문의 초기 처리
        x = self.initial_conv(x)       # Conv3D
        x = self.initial_bn(x)         # BatchNorm
        x = self.initial_relu(x)       # ReLU
        x = self.initial_maxpool(x)    # MaxPooling
        
        # 논문의 Residual Blocks
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        # 논문의 평균 풀링
        x = self.avgpool(x)            # Global Average Pooling
        
        # 논문의 Flatten (view)
        x = torch.flatten(x, 1)        # (B, 512, 1, 1, 1) → (B, 512)
        
        # 논문의 출력 (Prediction)
        x = self.fc(x)
        
        return x
    
    def get_feature_maps(self, x):
        """
        중간 feature map들을 반환 (디버깅 및 분석용)
        """
        features = {}
        
        if x.dim() == 4:
            x = x.unsqueeze(1)
        
        # 초기 처리
        x = self.initial_conv(x)
        x = self.initial_bn(x)
        x = self.initial_relu(x)
        features['initial'] = x.clone()
        x = self.initial_maxpool(x)
        
        # Residual layers
        x = self.layer1(x)
        features['layer1'] = x.clone()
        
        x = self.layer2(x)
        features['layer2'] = x.clone()
        
        x = self.layer3(x)
        features['layer3'] = x.clone()
        
        x = self.layer4(x)
        features['layer4'] = x.clone()
        
        return features


def create_resnet3d_18(config):
    """
    논문에서 사용한 3D ResNet-18 모델 생성
    
    Args:
        config: 모델 설정
            - num_classes: 출력 클래스 수 (회귀: 1, 분류: 클래스 수)
            - input_bands: 입력 밴드 수
            - task_type: 'regression' 또는 'classification'
    Returns:
        ResNet3D: 생성된 모델
    """
    return ResNet3D(config)


def get_model_info(model):
    """
    모델 정보 출력
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print("=" * 60)
    print("3D ResNet-18 Model Information")
    print("=" * 60)
    print(f"Task Type: {model.task_type}")
    print(f"Number of Classes: {model.num_classes}")
    print(f"Input Bands: {model.input_bands}")
    print(f"Total Parameters: {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,}")
    print("=" * 60)
    
    return {
        'total_params': total_params,
        'trainable_params': trainable_params,
        'task_type': model.task_type,
        'num_classes': model.num_classes
    }

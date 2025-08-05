import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN_2D(nn.Module):
    def __init__(self, input_channels, num_classes, dropout=0.0):
        super().__init__()
        # 입력 텐서 크기 : (배치 사이즈, input_channels, H, W)
        self.backbone = nn.Sequential( # 특징 추출 부분
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(), # 입력 채널 -> 32채널로 출력, 커널 크기 3x3, padding=1로 출력 크기 유지 
            
            # 최대 풀링 :  이미지 크기를 1/2로 줄임
            nn.MaxPool2d(kernel_size=2, stride=2),

            # 32 -> 64 채널로 확장 
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.MaxPool2d(kernel_size=2, stride=2), # 이미지 크기는 1/2로 

            # 64 -> 128 채널로 확장 
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),

            # 출력 크기를 (1, 1)로 자동 조정
            # feature map의 공간 정보 모두 평균내어 벡터로 변환 준비
            nn.AdaptiveAvgPool2d((1, 1))  # Output shape: (B, 128, 1, 1)
        )

        self.head = nn.Sequential(
            nn.Flatten(),                # (B, 128, 1, 1) → (B, 128) : 4차원을 1차원으로 펼쳐 요약된 특징 벡터 얻기
            nn.Linear(128, 512), # FC : 128 -> 512 : 128개를 512차원으로 변환
            nn.ReLU(), # 비선형성 추가로 더 복잡한 패턴 학습
            nn.Dropout(p=dropout), # config로 dropout 제어
            nn.Linear(512, num_classes) # FC : 512 -> 클래스 수만큼 출력 
        ) # CNN은 특징을 추출하고, FC Layer는 그 특징을 이용해 최종 예측
        # FC Layer는 모든 정보를 종합해 복잡한 분류 기준을 학습할 수 있도록 해줌 
        # 마지막 Linear의 출력은 클래스 개수와 같아야 하며, 손실 계산에 사용

        self.apply(self._init_weights) # 전체 레이어에 대해 weight 초기화 수행 (초기 가중치 잘못 설정되지 않도록)

    def _init_weights(self, m): # weight 초기화 함수
        if isinstance(m, (nn.Conv2d, nn.Linear)): # Conv2d 또는 Linear 레이어에만 적용
            nn.init.kaiming_normal_(m.weight) # Kaiming 초기화 : ReLU 계열 함수에 맞게 weight를 정규분포로 랜덤 초기화
            if m.bias is not None:
                nn.init.constant_(m.bias, 0) # bias 존재하면 전부 0으로 설정해 불필요한 랜덤성 제거

    def forward(self, x):
        x = self.backbone(x)  # shape: (B, 128, 1, 1)
        x = self.head(x)      # shape: (B, num_classes)
        return x


def create_model(config):
    k = config["model"]["num_classes"]
    n = config["model"]["hsi_channels"]
    d = config["model"].get("dropout", 0.0)

    return CNN_2D(input_channels=n, num_classes=k)
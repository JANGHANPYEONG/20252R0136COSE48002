# PyTorch의 기본 모듈 import (신경망, 손실함수, 최적화 등)
import torch
import torch.nn as nn
import torch.optim as optim

#  2-Branch 구조 회귀 모델 정의
class CustomHSICNN(nn.Module):
    def __init__(self, input_channels, vector_size, num_classes, num_regression_targets=0):
        super().__init__()  # nn.Module 상속 초기화

        # [Branch 2] 공간 이미지 입력 (6×H×W 이미지 처리)
        self.image_branch = nn.Sequential(
            nn.Conv2d(input_channels, 32, 3, padding=1),  # 채널 입력 → 32채널로
            nn.BatchNorm2d(32),    # 학습 안정화를 위한 정규화
            nn.ReLU(),             # 비선형 활성화 함수
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 32채널 → 64채널
            nn.BatchNorm2d(64),    # 정규화
            nn.ReLU(),

            nn.AdaptiveAvgPool2d((1, 1)),  # 출력 크기를 (1×1)로 평균풀링 → (B, 64, 1, 1)
            nn.Flatten()                   # 차원 펼치기 → (B, 64)
        )

        # [Branch 1] 평균 스펙트럼 벡터 입력 (1D 입력) 처리용 MLP
        self.vector_branch = nn.Sequential(
            nn.Linear(vector_size, 32),  # 입력: 6차원 → 32차원으로 확장
            nn.ReLU(),                  # 활성화 함수 (비선형성 추가)
            nn.Linear(32, 16)           # 차원 축소 
        )

        # [병합 후] 두 브랜치의 특징을 합쳐서 회귀값 출력
        self.regression_head = nn.Sequential(
            nn.Linear(64 + 16, 64),  # 64 (이미지) + 16 (벡터) → 64차원
            nn.ReLU(),
            nn.Linear(64, num_regression_targets)  # 최종 출력: 수분, 지방 등 6개 연속값 예측
        )

    def forward(self, x_img, x_vec):
        feat_img = self.image_branch(x_img)  # 평균 스펙트럼 벡터 처리 → (B, 16)
        feat_vec = self.vector_branch(x_vec)      # 이미지 처리 → (B, 64)
        combined = torch.cat([feat_img, feat_vec], dim=1)  # 두 feature 합치기 → (B, 80)
        regression_output = self.regression_head(combined)  # 회귀값 출력

        return {
            "classification": torch.empty(x_img.size(0), 0),  # 분류는 사용하지 않음
            "regression": regression_output  # 회귀값 출력
        }

def create_model(num_classes=0, num_regression_targets=6, **kwargs):
    """
    2-Branch HSI 회귀 모델 (이미지 + 벡터)

    Args:
        num_classes (int): 분류 클래스 수 (사용 안 함)
        num_regression_targets (int): 회귀 타겟 수 (예: 6)
        kwargs:
            - hsi_channels (int): 이미지 채널 수 (밴드 수)
            - vector_size (int): 벡터 입력 차원 수
    """
    hsi_channels = kwargs.get('hsi_channels', 6)
    vector_size = kwargs.get('vector_size', 6)

    return CustomHSICNN(
        input_channels=hsi_channels,
        vector_size=vector_size,
        num_classes=num_classes,
        num_regression_targets=num_regression_targets
    )

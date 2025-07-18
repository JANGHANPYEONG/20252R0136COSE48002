# PyTorch의 기본 모듈 import (신경망, 손실함수, 최적화 등)
import torch
import torch.nn as nn
import torch.optim as optim

#  2-Branch 구조 회귀 모델 정의
class DualInputRegressionModel(nn.Module):
    def __init__(self, band_count=6, spatial_size=32, num_outputs=6):
        super().__init__()  # nn.Module 상속 초기화

        # [Branch 1] 평균 스펙트럼 벡터 입력 (1D 입력) 처리용 MLP
        self.spectral_branch = nn.Sequential(
            nn.Linear(band_count, 32),  # 입력: 6차원 → 32차원으로 확장
            nn.ReLU(),                  # 활성화 함수 (비선형성 추가)
            nn.Linear(32, 16)           # 32차원 → 16차원으로 축소 (최종 feature)
        )

        # [Branch 2] 공간 이미지 입력 (6×H×W 이미지 처리)
        self.spatial_branch = nn.Sequential(
            nn.Conv2d(band_count, 32, kernel_size=3, padding=1),  # 6채널 입력 → 32채널로
            nn.BatchNorm2d(32),    # 학습 안정화를 위한 정규화
            nn.ReLU(),             # 비선형 활성화 함수

            nn.Conv2d(32, 64, kernel_size=3, padding=1),  # 32채널 → 64채널
            nn.ReLU(),

            nn.AdaptiveAvgPool2d((1, 1)),  # 출력 크기를 (1×1)로 평균풀링 → (B, 64, 1, 1)
            nn.Flatten()                   # 차원 펼치기 → (B, 64)
        )

        # [병합 후] 두 브랜치의 특징을 합쳐서 회귀값 출력
        self.fc = nn.Sequential(
            nn.Linear(64 + 16, 64),  # 64 (이미지) + 16 (벡터) → 64차원
            nn.ReLU(),
            nn.Linear(64, num_outputs)  # 최종 출력: 수분, 지방 등 6개 연속값 예측
        )

    def forward(self, x_image, x_spectral):
        feat1 = self.spectral_branch(x_spectral)  # 평균 스펙트럼 벡터 처리 → (B, 16)
        feat2 = self.spatial_branch(x_image)      # 이미지 처리 → (B, 64)
        combined = torch.cat([feat1, feat2], dim=1)  # 두 feature 합치기 → (B, 80)
        return self.fc(combined)                  # 합쳐진 feature로 회귀값 출력

#  학습 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # GPU 사용 여부 확인
print("학습 장치:", device)


batch_size = 8
band_count = 6
H, W = 32, 32
epochs = 20  # 에폭 수: 전체 데이터셋을 몇 번 반복할 것인가
num_outputs = 6

# 모델, 손실함수, 옵티마이저 정의
model = DualInputRegressionModel(band_count=band_count).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 더미 데이터셋 전체 (예: 100개 샘플)
num_samples = 100
X_img = torch.randn(num_samples, band_count, H, W)
X_vec = torch.randn(num_samples, band_count)
Y_true = torch.randn(num_samples, num_outputs)

# 에폭 학습 루프 시작
model.train()
for epoch in range(epochs):
    epoch_loss = 0.0
    num_batches = num_samples // batch_size

    for i in range(num_batches):
        # 🔹 배치 구성 (슬라이싱으로 나눔)
        start = i * batch_size
        end = start + batch_size

        x_img_batch = X_img[start:end].to(device)
        x_vec_batch = X_vec[start:end].to(device)
        y_batch = Y_true[start:end].to(device)

        # 🔹 forward + backward + optimize
        optimizer.zero_grad()
        y_pred = model(x_img_batch, x_vec_batch)
        loss = criterion(y_pred, y_batch)
        loss.backward()
        optimizer.step()

        epoch_loss += loss.item()

    avg_loss = epoch_loss / num_batches
    print(f"[Epoch {epoch+1}/{epochs}] 평균 Loss: {avg_loss:.4f}")
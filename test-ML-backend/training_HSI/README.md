# HSI 2D CNN 학습 파이프라인

이 프로젝트는 HSI(Hyperspectral Imaging) 데이터를 사용하여 2D CNN 모델을 훈련하는 파이프라인입니다.

## 🗂️ 프로젝트 구조

```
training_HSI/
├── configs/
│   └── HSI_image/
│       └── hsi_resnet.json          # ResNet 모델 설정
├── models/
│   └── HSI_image/
│       └── hsi_resnet.py            # HSI ResNet 모델 구현
├── utils/
│   ├── dataset_hsi.py               # HSI 데이터셋 로딩 및 전처리
│   ├── logger.py                    # MLflow 로깅 유틸리티
│   └── trainer.py                   # 훈련 로직
├── train_HSI_2d.py                  # 메인 훈련 스크립트
└── requirements.txt                 # 필요한 패키지 목록
```

## 🚀 사용법

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 데이터 준비

데이터는 다음 구조로 준비해야 합니다:

```
datasets_HSI/
├── label/
│   ├── label.csv                    # 라벨 데이터 (CSV)
│   └── column_config.json           # 컬럼 설정
└── image/                           # HSI 이미지 파일들
```

### 3. 설정 파일 수정

`configs/HSI_image/hsi_resnet.json` 파일에서 다음을 설정하세요:

- **데이터 경로**: CSV 파일 및 컬럼 설정 파일 경로
- **모델 설정**: 클래스 수, 모델 타입
- **훈련 설정**: 에포크, 배치 크기, 학습률 등
- **MLflow 설정**: 실험 이름, 추적 URI

### 4. 훈련 실행

```bash
# 기본 훈련 (MLflow 로깅 포함)
python train_HSI_2d.py --config configs/HSI_image/hsi_resnet.json

# MLflow 로깅 없이 훈련
python train_HSI_2d.py --config configs/HSI_image/hsi_resnet.json --no-mlflow
```

## 📊 주요 기능

### 멀티태스크 학습

- **분류 태스크**: `label_types.classification`에 정의된 라벨들 (BCE 손실)
- **회귀 태스크**: `label_types.regression`에 정의된 라벨들 (MSE 손실)
- **자동 가중치 조정**: MultiTaskLossWrapper로 태스크 간 균형 조정

### 데이터 누출 방지

- **스케일러 fit**: 훈련 데이터로만 StandardScaler fit
- **메모리 최적화**: 무작위 픽셀 샘플링으로 스케일러 학습

### 데이터 증강

- **랜덤 크롭**: 지정된 크기로 이미지 크롭
- **랜덤 뒤집기**: 수평/수직 뒤집기
- **랜덤 회전**: ±10도 회전
- **노이즈 추가**: 가우시안 노이즈
- **밝기/대비 조정**: 랜덤 밝기/대비 변화

### MLflow 통합

- 실험 추적 및 메트릭 로깅
- 모델 및 스케일러 저장
- 훈련 곡선 시각화

### Early Stopping

- 검증 손실 기반 early stopping
- 설정 가능한 patience 파라미터
- 최고 성능 모델 자동 저장

## 🔧 설정 파일 예시

### column_config.json

```json
{
  "column_order": {
    "id_column_index": 0,
    "label_start_index": 1,
    "vector_start_index": 14,
    "image_path_start_index": 19
  },
  "label_columns": [
    "disease_1",
    "disease_2",
    "disease_3",
    "disease_4",
    "disease_5",
    "disease_6",
    "disease_7",
    "disease_8",
    "disease_9",
    "disease_10",
    "disease_11",
    "disease_12",
    "disease_13"
  ],
  "label_types": {
    "classification": [
      "disease_1",
      "disease_2",
      "disease_3",
      "disease_4",
      "disease_5",
      "disease_6",
      "disease_7",
      "disease_8",
      "disease_9",
      "disease_10",
      "disease_11",
      "disease_12",
      "disease_13"
    ],
    "regression": []
  },
  "wavelengths": [10, 60, 70, 100, 110],
  "image_size": [256, 256]
}
```

### hsi_resnet.json

```json
{
  "experiment": "hsi_resnet_baseline",
  "model": {
    "file": "hsi_resnet",
    "num_classes": 13
  },
  "data": {
    "csv": "datasets_HSI/label/label.csv",
    "column_config": "datasets_HSI/label/column_config.json",
    "val_split": 0.1,
    "test_split": 0.1,
    "batch_size": 8,
    "num_workers": 4,
    "crop_size": [224, 224],
    "use_flip": true,
    "use_rotation": true,
    "use_noise": true,
    "use_brightness_contrast": true
  },
  "train": {
    "epochs": 50,
    "early_stopping_patience": 10,
    "optimizer": "AdamW",
    "lr": 3e-4,
    "scheduler": "ReduceLROnPlateau"
  },
  "mlflow": {
    "tracking_uri": "http://127.0.0.1:5000",
    "experiment_name": "HSI_2D_CNN"
  },
  "seed": 42
}
```

## 📈 평가 메트릭

### 분류 메트릭 (Classification)

- **Accuracy**: 전체 정확도
- **Precision**: 정밀도 (macro average)
- **Recall**: 재현율 (macro average)
- **F1-Score**: F1 점수 (macro average)
- **AUC**: ROC AUC (macro average)

### 회귀 메트릭 (Regression)

- **MSE**: Mean Squared Error
- **MAE**: Mean Absolute Error
- **R²**: 결정 계수 (Coefficient of Determination)

### 통합 메트릭

- **Combined Score**: 분류 F1과 회귀 R²의 평균

## 🔍 모니터링

### MLflow UI

```bash
# MLflow 서버 시작
mlflow ui --port 5000

# 브라우저에서 http://localhost:5000 접속
```

### 훈련 로그

- 실시간 훈련/검증 손실 및 메트릭 출력
- 진행률 바로 배치별 진행 상황 표시
- 최고 성능 모델 자동 저장 알림

## 🛠️ 커스터마이징

### 새로운 모델 추가

1. `models/HSI_image/` 디렉토리에 새 모델 파일 생성
2. `create_model()` 함수 구현
3. 설정 파일에서 모델 파일명 지정

### 새로운 데이터셋 사용

1. `column_config.json`에서 컬럼 구조 정의
2. CSV 파일에서 이미지 경로 및 라벨 매핑
3. 설정 파일에서 데이터 경로 업데이트

## 🤖 모델 개발 가이드

### 모델 파일 구조

모델 파일은 `models/HSI_image/` 디렉토리에 위치하며, 다음 구조를 따라야 합니다:

```python
import torch
import torch.nn as nn
from torchvision import models

def create_model(num_classes, **kwargs):
    """
    모델 생성 함수

    Args:
        num_classes (int): 분류 클래스 수
        **kwargs: 추가 모델 파라미터

    Returns:
        nn.Module: 생성된 모델
    """
    # 모델 구현
    pass
```

### 입력 데이터 사양

**중요**: 파이프라인에서 이미 모든 전처리가 완료된 상태로 모델에 입력됩니다.

#### 입력 텐서 형태

- **Shape**: `(batch_size, num_channels, height, width)`
- **Data Type**: `torch.float32`
- **Normalization**: 이미 StandardScaler로 정규화됨 (평균=0, 표준편차=1)
- **Device**: 모델과 동일한 디바이스 (CPU/GPU)

#### 채널 정보

- **채널 수**: `column_config.json`의 `wavelengths` 리스트 길이
- **채널 순서**: `wavelengths` 리스트 순서대로 정렬됨
- **예시**: `wavelengths: [10, 60, 70, 100, 110]` → 5채널 입력

### 출력 요구사항

#### 멀티태스크 출력

모델은 분류와 회귀 태스크를 동시에 처리해야 합니다:

```python
class MultiTaskModel(nn.Module):
    def __init__(self, num_classes, num_regression_targets):
        super().__init__()
        # 공통 백본
        self.backbone = nn.Sequential(...)

        # 분류 헤드
        self.classification_head = nn.Linear(feature_dim, num_classes)

        # 회귀 헤드
        self.regression_head = nn.Linear(feature_dim, num_regression_targets)

    def forward(self, x):
        features = self.backbone(x)

        # 분류 출력 (sigmoid 적용)
        classification_output = torch.sigmoid(self.classification_head(features))

        # 회귀 출력 (선형)
        regression_output = self.regression_head(features)

        return {
            'classification': classification_output,
            'regression': regression_output
        }
```

#### 출력 형태

- **분류**: `(batch_size, num_classification_labels)` - sigmoid 적용
- **회귀**: `(batch_size, num_regression_labels)` - 선형 출력
- **반환 형식**: 딕셔너리 형태로 반환

### 모델 구현 예시

#### 1. ResNet 기반 모델

```python
import torch
import torch.nn as nn
from torchvision import models

def create_model(num_classes, num_regression_targets=0, **kwargs):
    """
    ResNet 기반 HSI 분류/회귀 모델

    Args:
        num_classes (int): 분류 클래스 수
        num_regression_targets (int): 회귀 타겟 수
        **kwargs: 추가 파라미터
    """
    # ResNet 백본 (첫 번째 conv 레이어 수정)
    model = models.resnet50(pretrained=False)

    # 첫 번째 conv 레이어를 HSI 채널에 맞게 수정
    # 원본: 3채널 → HSI 채널 수로 변경
    hsi_channels = kwargs.get('hsi_channels', 5)
    model.conv1 = nn.Conv2d(hsi_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)

    # 분류 헤드 수정
    feature_dim = model.fc.in_features
    model.fc = nn.Identity()  # 기존 fc 제거

    # 멀티태스크 헤드 추가
    classification_head = nn.Linear(feature_dim, num_classes)
    regression_head = nn.Linear(feature_dim, num_regression_targets) if num_regression_targets > 0 else None

    return MultiTaskResNet(
        backbone=model,
        classification_head=classification_head,
        regression_head=regression_head
    )

class MultiTaskResNet(nn.Module):
    def __init__(self, backbone, classification_head, regression_head=None):
        super().__init__()
        self.backbone = backbone
        self.classification_head = classification_head
        self.regression_head = regression_head

    def forward(self, x):
        # 백본 특징 추출
        features = self.backbone(x)

        # 분류 출력
        classification_output = torch.sigmoid(self.classification_head(features))

        # 회귀 출력 (있는 경우만)
        if self.regression_head is not None:
            regression_output = self.regression_head(features)
            return {
                'classification': classification_output,
                'regression': regression_output
            }
        else:
            return {
                'classification': classification_output,
                'regression': torch.empty(classification_output.shape[0], 0)
            }
```

#### 2. 커스텀 CNN 모델

```python
import torch
import torch.nn as nn

def create_model(num_classes, num_regression_targets=0, **kwargs):
    """
    커스텀 CNN 모델

    Args:
        num_classes (int): 분류 클래스 수
        num_regression_targets (int): 회귀 타겟 수
        **kwargs: 추가 파라미터
    """
    hsi_channels = kwargs.get('hsi_channels', 5)

    return CustomHSICNN(
        input_channels=hsi_channels,
        num_classes=num_classes,
        num_regression_targets=num_regression_targets
    )

class CustomHSICNN(nn.Module):
    def __init__(self, input_channels, num_classes, num_regression_targets=0):
        super().__init__()

        # 특징 추출기
        self.features = nn.Sequential(
            # 첫 번째 블록
            nn.Conv2d(input_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # 두 번째 블록
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # 세 번째 블록
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),

            # 네 번째 블록
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1))
        )

        # 분류 헤드
        self.classification_head = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

        # 회귀 헤드
        if num_regression_targets > 0:
            self.regression_head = nn.Sequential(
                nn.Dropout(0.5),
                nn.Linear(256, num_regression_targets)
            )
        else:
            self.regression_head = None

    def forward(self, x):
        # 특징 추출
        features = self.features(x)
        features = features.view(features.size(0), -1)  # Flatten

        # 분류 출력
        classification_output = torch.sigmoid(self.classification_head(features))

        # 회귀 출력
        if self.regression_head is not None:
            regression_output = self.regression_head(features)
            return {
                'classification': classification_output,
                'regression': regression_output
            }
        else:
            return {
                'classification': classification_output,
                'regression': torch.empty(classification_output.shape[0], 0)
            }
```

### 모델 등록 및 사용

#### 1. 모델 파일 생성

`models/HSI_image/my_model.py` 파일 생성

#### 2. 설정 파일 수정

```json
{
  "model": {
    "file": "my_model",
    "num_classes": 13,
    "num_regression_targets": 2,
    "hsi_channels": 5
  }
}
```

#### 3. 훈련 실행

```bash
python train_HSI_2d.py --config configs/HSI_image/my_model.json
```

### 주의사항

#### 모델 개발 시 고려사항

1. **전처리 불필요**: 입력 데이터는 이미 정규화되어 있으므로 모델 내에서 추가 정규화 불필요
2. **채널 수 확인**: `column_config.json`의 `wavelengths` 길이와 일치하는지 확인
3. **출력 형태**: 반드시 딕셔너리 형태로 분류/회귀 출력 반환
4. **메모리 효율성**: HSI 데이터는 메모리를 많이 사용하므로 효율적인 아키텍처 설계
5. **배치 정규화**: 훈련 안정성을 위해 BatchNorm 사용 권장

#### 디버깅 팁

```python
# 모델 입력 형태 확인
print(f"Input shape: {x.shape}")
print(f"Input dtype: {x.dtype}")
print(f"Input device: {x.device}")
print(f"Input range: [{x.min():.3f}, {x.max():.3f}]")

# 모델 출력 형태 확인
outputs = model(x)
print(f"Classification output shape: {outputs['classification'].shape}")
print(f"Regression output shape: {outputs['regression'].shape}")
```

## 📝 주의사항

1. **메모리 사용량**: HSI 데이터는 메모리를 많이 사용하므로 배치 크기를 적절히 조정하세요.
2. **GPU 메모리**: CUDA out of memory 오류 시 배치 크기를 줄이거나 이미지 크기를 조정하세요.
3. **데이터 경로**: 상대 경로를 사용할 때는 스크립트 실행 위치를 확인하세요.
4. **MLflow 서버**: MLflow 로깅을 사용하려면 MLflow 서버가 실행 중이어야 합니다.

## 🤝 문제 해결

### 일반적인 오류

1. **ImportError**: `sys.path.append()`로 경로가 올바르게 추가되었는지 확인
2. **FileNotFoundError**: 데이터 파일 경로가 올바른지 확인
3. **CUDA out of memory**: 배치 크기 줄이기 또는 이미지 크기 조정
4. **MLflow 연결 오류**: MLflow 서버가 실행 중인지 확인

### 디버깅 팁

- `--no-mlflow` 옵션으로 MLflow 없이 훈련 테스트
- 작은 데이터셋으로 먼저 테스트
- 로그 출력을 통해 데이터 로딩 확인

# HSI/RGB/Vector 학습 파이프라인

이 프로젝트는 HSI(Hyperspectral Imaging), RGB 이미지, 그리고 Vector 데이터를 사용하여 AI 모델을 훈련하는 통합 파이프라인입니다.
분류(Classification)와 회귀(Regression)를 동시에 수행하는 멀티태스크 학습을 지원합니다.

## 🗂️ 프로젝트 구조

```
training_HSI/
├── configs/                 # 학습 설정 파일들
│   ├── HSI_image/           # HSI 모델용 설정 (예: hsi_resnet.json)
│   ├── RGB_image/           # RGB 모델용 설정 (예: rgb_resnet.json)
│   ├── HSI_vector/          # Vector 모델용 설정 (예: vector_randomforest.json)
│   └── column_config.json   # 데이터 컬럼 및 경로 설정 (공통)
├── models/                  # 모델 구현체
│   ├── HSI_image/           # HSI 2D/3D 모델
│   ├── RGB_image/           # RGB 모델
│   └── HSI_vector/          # Vector ML 모델 (RandomForest, SVM 등)
├── utils/                   # 유틸리티 (데이터셋, 로거, 트레이너 등)
├── train_HSI_2d.py          # HSI 2D 모델 학습 스크립트
├── train_RGB.py             # RGB 모델 학습 스크립트
├── train_vector.py          # Vector 모델 학습 스크립트
└── requirements.txt         # 의존성 패키지 목록
```

## 🚀 사용법

### 1. 환경 설정

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 2. 데이터 준비

데이터셋은 `configs/column_config.json`에 정의된 구조를 따라야 합니다.
CSV 파일에는 이미지 경로, 벡터 데이터, 그리고 라벨 정보가 포함되어야 합니다.

**`configs/column_config.json` 예시:**

```json
{
  "column_order": {
    "id_column_index": 0,
    "label_start_index": 1,
    "rgb_image_path_start_index": 11
  },
  "label_columns": ["Marbling", "Grade"],
  "label_types": {
    "classification": ["Grade"],
    "regression": ["Marbling"]
  },
  "base_dirs": {
    "hsi_image_dir": "/path/to/hsi_images",
    "rgb_image_dir": "/path/to/rgb_images",
    "rgb_mask_dir": "/path/to/masks"
  }
}
```

### 3. 학습 실행

각 모달리티별로 전용 학습 스크립트를 사용합니다.

#### HSI 2D 모델 학습

```bash
python3 train_HSI_2d.py --config configs/HSI_image/hsi_resnet.json
```

#### RGB 모델 학습 (Segmentation 지원)

```bash
python3 train_RGB.py --config configs/RGB_image/rgb_resnet.json
```

#### Vector 모델 학습 (Hyperparameter Search)

```bash
python3 train_vector.py --config configs/HSI_vector/vector_randomforest.json
```

## ⚙️ 설정 파일 가이드

### HSI 설정 (`configs/HSI_image/*.json`)

```json
{
  "model": {
    "file": "hsi_resnet",      # models/HSI_image/hsi_resnet.py 사용
    "num_classes": 13
  },
  "data": {
    "scaler_mode": "normalized", # "normalized", "raw", "off"
    "use_flip": true,            # 데이터 증강 옵션
    "use_rotation": true
  },
  "train": {
    "loss_fn": "uncertainty",    # 멀티태스크 손실 함수 (uncertainty weighting)
    "use_amp": true              # Mixed Precision 학습 사용
  }
}
```

### RGB 설정 (`configs/RGB_image/*.json`)

RGB 모델은 세그멘테이션 마스크 적용 옵션을 추가로 지원합니다.

```json
{
  "seg": {
    "enabled": true,
    "mode": "precomputed",       # 미리 계산된 마스크 사용
    "apply": "mul",              # 원본 이미지에 마스크 곱하기 (배경 제거)
    "threshold": 0.5
  }
}
```

### Vector 설정 (`configs/HSI_vector/*.json`)

Vector 모델은 Scikit-learn 기반의 모델과 하이퍼파라미터 탐색을 지원합니다.

```json
{
  "train": {
    "method": "bayessearchcv",   # 베이지안 최적화 사용
    "param_grid": {              # 탐색할 파라미터 범위
      "n_estimators": [10, 100],
      "max_depth": [2, 20]
    }
  }
}
```

## 📊 주요 기능

### 멀티태스크 학습 (Multi-task Learning)
- **분류(Classification)**와 **회귀(Regression)**를 하나의 모델에서 동시에 학습합니다.
- `uncertainty` loss function을 사용하여 태스크 간의 손실 가중치를 자동으로 조정합니다.

### MLflow 통합
- 모든 학습 과정(손실, 메트릭, 파라미터)이 MLflow에 자동으로 기록됩니다.
- `mlflow ui` 명령어로 학습 결과를 시각적으로 확인할 수 있습니다.

### 데이터 증강 (Data Augmentation)
- **HSI/RGB**: Random Crop, Flip, Rotation, Noise, Brightness/Contrast 조정 등을 지원합니다.
- 설정 파일에서 각 증강 기법의 사용 여부를 제어할 수 있습니다.

### Automatic Mixed Precision (AMP)
- GPU 메모리 사용량을 줄이고 학습 속도를 높이기 위해 AMP를 지원합니다.
- `config["train"]["use_amp"]: true`로 설정하여 활성화할 수 있습니다.


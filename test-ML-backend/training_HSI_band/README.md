# HSI Band Selection Pipeline

이 프로젝트는 Hyperspectral Imaging (HSI) 데이터의 밴드 선택을 위한 통합 파이프라인입니다. 벡터 데이터와 이미지 데이터 모두를 지원합니다.

## 구조

### 설정 파일 구조 (3개 설정 파일)

1. **메인 파이프라인 설정** (`configs/vector_pipeline_config.json`)

   - 전체 파이프라인 설정
   - 데이터 경로, 출력 디렉토리, MLflow 설정
   - 전처리/본처리 설정 파일 경로

2. **전처리 설정** (`configs/pre/vector_pre_config.json`)

   - 통계적 밴드 선택 방법 설정
   - MRMR, PCA, CARS 등

3. **본처리 설정** (`configs/training/vector_training_config.json`)
   - 학습 기반 밴드 선택 방법 설정
   - GPR+ARD, Random Frog, SHAP 등

### 데이터 타입 지원

#### 1. 벡터 데이터 (기존)

- 반사율 벡터를 입력으로 사용
- CSV 파일에서 스펙트럼 데이터를 직접 읽어옴

#### 2. 이미지 데이터 (신규)

- 각 밴드별 이미지 파일을 입력으로 사용
- CSV 파일에 이미지 경로 정보 포함

### 메인 파이프라인 설정 예시

```json
{
  "train_type": "default",
  "experiment": "hsi_band_selection",
  "run": "vector_pipeline",
  "hyperparameters": {
    "seed": 42
  },
  "data": {
    "csv_path": "./datasets_HSI/label/label.csv",
    "wavelength_info_path": "./datasets_HSI/wavelength_info.txt",
    "label_column": "label",
    "spectral_start_col": 1,
    "spectral_end_col": 204
  },
  "output": {
    "output_dir": "./results",
    "save_results": true,
    "save_model": false,
    "save_metrics": true,
    "save_band_info": true
  },
  "mlflow": {
    "tracking_uri": "http://0.0.0.0:5000",
    "port": 5000,
    "log_artifacts": true,
    "log_parameters": true,
    "log_metrics": true
  },
  "preprocessing": {
    "config_path": "configs/pre/vector_pre_config.json",
    "target_bands": 50
  },
  "training": {
    "config_path": "configs/training/vector_training_config.json",
    "target_bands": 10
  }
}
```

### 전처리 설정 예시 (`configs/pre/vector_pre_config.json`)

```json
{
  "preprocessing": {
    "model_name": "mrmr",
    "method": "statistical",
    "parameters": {
      "criterion": "MID",
      "k": 50,
      "random_state": 42
    }
  }
}
```

### 본처리 설정 예시 (`configs/training/vector_training_config.json`)

```json
{
  "training": {
    "model_name": "gpr_ard",
    "method": "learning_based",
    "parameters": {
      "kernel_type": "rbf",
      "alpha": 1e-6,
      "random_state": 42,
      "n_restarts_optimizer": 10
    }
  }
}
```

### HSI 이미지 설정 예시 (`configs/training/hsi_cnn_config.json`)

```json
{
  "training": {
    "model_name": "hsi_cnn",
    "model_file": "hsi_cnn_model",
    "method": "learning_based",
    "parameters": {
      "learning_rate": 0.001,
      "batch_size": 16,
      "epochs": 100,
      "early_stopping_patience": 10,
      "optimizer": "adam",
      "scheduler": "reduce_lr_on_plateau",
      "scheduler_patience": 5,
      "scheduler_factor": 0.5,
      "weight_decay": 0.0001,
      "label_type": "multilabel_classification"
    }
  }
}
```

### 이미지 파이프라인 설정 예시 (`configs/image_pipeline_config.json`)

```json
{
  "train_type": "image",
  "experiment": "hsi_image_classification",
  "run": "image_pipeline",
  "hyperparameters": {
    "seed": 42
  },
  "data_split": {
    "train_ratio": 0.8,
    "val_ratio": 0.1,
    "test_ratio": 0.1
  },
  "data": {
    "csv_path": "./datasets_HSI/label.csv",
    "num_workers": 4,
    "pin_memory": true
  },
  "output": {
    "output_dir": "./results",
    "save_results": true,
    "save_model": true,
    "save_metrics": true,
    "save_band_info": true
  },
  "mlflow": {
    "tracking_uri": "http://127.0.0.1:5000",
    "port": 5000,
    "log_artifacts": true,
    "log_parameters": true,
    "log_metrics": true
  },
  "training": {
    "config_path": "configs/training/hsi_cnn_config.json"
  }
}
```

### 다른 밴드 선택 방법 설정 예시

#### MRMR (전처리)

```json
{
  "preprocessing": {
    "model_name": "mrmr",
    "method": "statistical",
    "parameters": {
      "criterion": "MID",
      "k": 50,
      "random_state": 42
    }
  }
}
```

#### PCA (전처리)

```json
{
  "preprocessing": {
    "model_name": "pca",
    "method": "statistical",
    "parameters": {
      "n_components": 50,
      "random_state": 42
    }
  }
}
```

#### CARS (전처리)

```json
{
  "preprocessing": {
    "model_name": "cars",
    "method": "statistical",
    "parameters": {
      "n_samples": 50,
      "n_iterations": 1000,
      "random_state": 42
    }
  }
}
```

#### GPR+ARD (본처리)

```json
{
  "training": {
    "model_name": "gpr_ard",
    "method": "learning_based",
    "parameters": {
      "kernel_type": "rbf",
      "alpha": 1e-6,
      "random_state": 42,
      "n_restarts_optimizer": 10
    }
  }
}
```

#### Random Frog (본처리)

```json
{
  "training": {
    "model_name": "random_frog",
    "method": "learning_based",
    "parameters": {
      "n_iterations": 1000,
      "n_samples": 50,
      "random_state": 42
    }
  }
}
```

#### SHAP (본처리)

```json
{
  "training": {
    "model_name": "shap",
    "method": "learning_based",
    "parameters": {
      "background_samples": 100,
      "nsamples": 100,
      "random_state": 42
    }
  }
}
```

## 사용법

### 벡터 데이터 훈련 (기존)

```bash
python train_vector.py --config configs/vector_pipeline_config.json
```

### 이미지 데이터 훈련 (신규)

```bash
python train_multilabel_HSI_image.py configs/image_pipeline_config.json
```

### 커맨드 라인 인자로 설정 오버라이드

```bash
python train_vector.py \
  --config configs/vector_pipeline_config.json \
  --csv_path ./custom_data.csv \
  --output_dir ./custom_results \
  --pre_target_bands 30 \
  --final_target_bands 5 \
  --experiment custom_experiment \
  --run custom_run
```

## 데이터 형식

### 벡터 데이터 CSV 파일 구조

- 첫 번째 열: 라벨 (기본값: 'label')
- 나머지 열: 스펙트럼 데이터 (기본값: 1-204열)

### 이미지 데이터 CSV 파일 구조

```
ID,disease_1,disease_2,...,disease_13,band_10,band_60,band_70,band_100,band_110,band_10_path,band_60_path,band_70_path,band_100_path,band_110_path
O0015_R01_N112,0,1,1,0,0,0,0,0,0,0,0,0,0,170.35,167.78,135.63,161.77,187.22,/path/to/band_10.png,/path/to/band_60.png,/path/to/band_70.png,/path/to/band_100.png,/path/to/band_110.png
```

### 컬럼 설정 파일 (`datasets_HSI/column_config.json`)

```json
{
  "column_order": {
    "id_column_index": 0,
    "label_start_index": 1,
    "vector_start_index": 14,
    "image_path_start_index": 19
  },
  "label_columns": ["disease_1", "disease_2", ..., "disease_13"],
  "wavelengths": [10, 60, 70, 100, 110],
  "image_size": [256, 256]
}
```

### 설정 예시

```json
{
  "data": {
    "csv_path": "./datasets_HSI/label/label.csv",
    "label_column": "label",
    "spectral_start_col": 1,
    "spectral_end_col": 204
  }
}
```

## 모델

### 벡터 데이터 모델

- GPR+ARD, Random Frog, SHAP 등

### 이미지 데이터 모델

- **HSICNN**: 기본 CNN 모델
- **HSICNNResNet**: ResNet 스타일 CNN 모델

## 출력

### MLflow 기록

- 모든 설정 파일
- 선택된 밴드 정보
- 성능 메트릭
- 실행 파라미터

### 로컬 파일 저장 (옵션)

- `results.json`: 전체 결과
- `band_info.json`: 밴드 선택 정보

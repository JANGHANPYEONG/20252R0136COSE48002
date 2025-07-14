# HSI Band Selection Pipeline

이 프로젝트는 Hyperspectral Imaging (HSI) 데이터의 밴드 선택을 위한 통합 파이프라인입니다.

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

### 기본 실행

```bash
python train_vector.py --config configs/vector_pipeline_config.json
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

### CSV 파일 구조

- 첫 번째 열: 라벨 (기본값: 'label')
- 나머지 열: 스펙트럼 데이터 (기본값: 1-204열)

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

## 출력

### MLflow 기록

- 모든 설정 파일
- 선택된 밴드 정보
- 성능 메트릭
- 실행 파라미터

### 로컬 파일 저장 (옵션)

- `results.json`: 전체 결과
- `band_info.json`: 밴드 선택 정보
- `metrics.csv`: 성능 메트릭

## MLflow 사용 가이드라인

### 모델 개발자를 위한 가이드라인

1. **메인 파이프라인에서만 MLflow 사용**

   - 개별 모델에서는 MLflow를 직접 사용하지 마세요
   - 대신 파라미터로 전달받은 MLflow 정보를 활용하세요

2. **중첩 실행 사용**

   ```python
   # 모델 내부에서 중첩 실행 사용
   if 'mlflow_info' in config:
       with mlflow.start_run(
           experiment_name=config['mlflow_info']['experiment_name'],
           run_id=config['mlflow_info']['parent_run_id'],
           nested=True
       ):
           # 모델 학습 및 로깅
   ```

3. **설정 구조**

   ```python
   # 전처리 모델 예시
   class MRMRBandSelector:
       def __init__(self, config):
           self.config = config
           self.mlflow_info = config.get('mlflow_info', {})

       def select_bands(self, spectral_data, labels, target_bands):
           # 중첩 MLflow 실행
           if self.mlflow_info:
               with mlflow.start_run(
                   experiment_name=self.mlflow_info['experiment_name'],
                   run_id=self.mlflow_info['parent_run_id'],
                   nested=True
               ):
                   # 밴드 선택 로직
                   mlflow.log_param("mrmr_target_bands", target_bands)
                   # ...
   ```

## 설정 우선순위

1. 커맨드 라인 인자 (최우선)
2. 메인 파이프라인 설정
3. 기본값

## 지원하는 밴드 선택 방법

### 전처리 (통계적 방법)

- MRMR (Minimum Redundancy Maximum Relevance)
- PCA (Principal Component Analysis)
- CARS (Competitive Adaptive Reweighted Sampling)

### 본처리 (학습 기반 방법)

- GPR+ARD (Gaussian Process Regression with Automatic Relevance Determination)
- Random Frog
- SHAP (SHapley Additive exPlanations)

## 파일 구조

```
training_HSI_band/
├── configs/
│   ├── vector_pipeline_config.json    # 메인 파이프라인 설정
│   ├── pre/
│   │   └── vector_pre_config.json     # 전처리 설정
│   └── training/
│       └── vector_training_config.json # 본처리 설정
├── models/
│   ├── preprocessing/                  # 전처리 모델들
│   └── training/                      # 본처리 모델들
├── utils/
│   ├── dataset.py                     # 데이터 로딩
│   ├── evaluation.py                  # 평가 메트릭
│   ├── add_param.py                   # 파라미터 파싱
│   └── model_loader.py                # 모델 로딩
├── train_vector.py                    # 메인 훈련 스크립트
└── README.md
```

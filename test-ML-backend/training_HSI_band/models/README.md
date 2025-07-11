# HSI Band Selection Models

## 모델 개발 가이드라인

### 1. 전처리 모델 (models/pre/)

#### 파일 구조

```
models/pre/
├── mrmr_model.py
├── pca_model.py
├── cars_model.py
└── __init__.py
```

#### 모델 클래스 구조

```python
class PreprocessingModel:
    def __init__(self, config):
        self.config = config
        # 모델 초기화

    def select_bands(self, spectral_data, labels, target_bands):
        """
        밴드 선택을 수행합니다.

        Args:
            spectral_data: np.ndarray (n_samples, n_bands)
            labels: np.ndarray (n_samples, n_labels)
            target_bands: int (목표 밴드 수)

        Returns:
            selected_bands: List[int] (선택된 밴드 인덱스)
        """
        # 밴드 선택 로직 구현
        return selected_bands
```

#### create_model 함수

```python
def create_model(model_name: str, config: Dict) -> PreprocessingModel:
    """모델을 생성합니다."""
    return PreprocessingModel(config)
```

### 2. 본처리 모델 (models/training/)

#### 파일 구조

```
models/training/
├── gpr_ard_model.py
├── random_frog_model.py
├── shap_model.py
└── __init__.py
```

#### 모델 클래스 구조

```python
class TrainingModel:
    def __init__(self, config):
        self.config = config
        # MLflow 정보 추출
        self.mlflow_info = config.get('mlflow_info', {})
        # 모델 초기화

    def select_bands_with_scores(self, spectral_data, labels, pre_selected_bands, target_bands):
        """
        밴드 선택과 스코어를 반환합니다.

        Args:
            spectral_data: np.ndarray (n_samples, n_bands)
            labels: np.ndarray (n_samples, n_labels)
            pre_selected_bands: List[int] (전처리에서 선택된 밴드)
            target_bands: int (목표 밴드 수)

        Returns:
            selected_bands: List[int] (선택된 밴드 인덱스)
            band_scores: List[float] (각 밴드의 스코어, 0-1 범위로 정규화)
        """
        # 밴드 선택 및 스코어 계산 로직 구현
        return selected_bands, band_scores
```

#### create_model 함수

```python
def create_model(model_name: str, config: Dict) -> TrainingModel:
    """모델을 생성합니다."""
    return TrainingModel(config)
```

### 3. MLflow 사용 가이드라인

#### ✅ 권장사항: 상위 파이프라인의 MLflow 환경 사용

본처리 모델에서 실제 학습이 발생하는 경우, 상위 파이프라인에서 전달받은 MLflow 정보를 사용하여 같은 환경에서 로깅할 수 있습니다.

```python
import mlflow

class GPRARDModel:
    def __init__(self, config):
        self.config = config
        # MLflow 정보 추출
        self.mlflow_info = config.get('mlflow_info', {})

    def select_bands_with_scores(self, spectral_data, labels, pre_selected_bands, target_bands):
        # 상위 파이프라인의 MLflow 환경 사용
        if self.mlflow_info:
            # 기존 MLflow 환경 설정
            mlflow.set_experiment(self.mlflow_info['experiment_name'])

            # 중첩된 run 생성
            with mlflow.start_run(nested=True, run_name="gpr_ard_training") as run:
                # 학습 파라미터 기록
                mlflow.log_param("kernel_type", self.config['training']['parameters']['kernel_type'])
                mlflow.log_param("alpha", self.config['training']['parameters']['alpha'])

                # 학습 과정
                for epoch in range(self.config['training']['parameters']['num_epochs']):
                    loss = self.train_step()
                    mlflow.log_metric("loss", loss, step=epoch)

                # 최종 결과
                selected_bands = self.select_final_bands(pre_selected_bands, target_bands)
                band_scores = self.calculate_scores(selected_bands)

                # 결과 기록
                mlflow.log_dict({"selected_bands": selected_bands}, "final_selection.json")
                mlflow.log_dict({"band_scores": band_scores}, "band_scores.json")

                return selected_bands, band_scores
        else:
            # MLflow 정보가 없는 경우 (테스트 등)
            selected_bands = self.select_final_bands(pre_selected_bands, target_bands)
            band_scores = self.calculate_scores(selected_bands)
            return selected_bands, band_scores
```

#### MLflow 정보 구조

```python
mlflow_info = {
    "experiment_name": "hsi_band_selection",
    "parent_run_id": "abc123def456"
}
```

#### ❌ 금지사항: 독립적인 MLflow run

- 상위 파이프라인과 별개의 MLflow run을 만들지 마세요
- `nested=True`를 사용하여 중첩된 run으로 기록하세요
- 상위 파이프라인의 experiment 환경을 그대로 사용하세요

### 4. Config 구조

#### 전처리 Config

```json
{
  "preprocessing": {
    "model_name": "mrmr",
    "model_file": "mrmr_model",
    "parameters": {
      "threshold": 0.8,
      "method": "mutual_info"
    }
  },
  "mlflow_info": {
    "experiment_name": "hsi_band_selection",
    "parent_run_id": "abc123def456"
  }
}
```

#### 본처리 Config

```json
{
  "training": {
    "model_name": "gpr_ard",
    "model_file": "gpr_ard_model",
    "parameters": {
      "kernel_type": "rbf",
      "alpha": 1e-6,
      "num_epochs": 100,
      "learning_rate": 0.01
    }
  },
  "mlflow_info": {
    "experiment_name": "hsi_band_selection",
    "parent_run_id": "abc123def456"
  }
}
```

### 5. 반환값 형식

#### 전처리 모델

- **반환값**: `List[int]` (밴드 인덱스만)
- **예시**: `[10, 25, 42, 67, 89, 120, 145, 178, 201, 234]`

#### 본처리 모델

- **반환값**: `Tuple[List[int], List[float]]` (밴드 인덱스 + 스코어)
- **예시**: `([25, 42, 89, 145, 201], [0.95, 0.87, 0.82, 0.78, 0.75])`

### 6. 스코어 정규화

- 본처리 모델의 스코어는 0-1 범위로 정규화하세요
- 높은 스코어 = 더 중요한 밴드
- 예: `[0.95, 0.87, 0.82, 0.78, 0.75]`

### 7. 예시 모델

#### MRMR 모델 예시

```python
import numpy as np
from sklearn.feature_selection import mutual_info_regression

class MRMRModel:
    def __init__(self, config):
        self.config = config

    def select_bands(self, spectral_data, labels, target_bands):
        # MRMR 알고리즘 구현
        mi_scores = mutual_info_regression(spectral_data, labels.mean(axis=1))
        selected_indices = np.argsort(mi_scores)[-target_bands:]
        return selected_indices.tolist()
```

#### GPR+ARD 모델 예시 (MLflow 환경 공유)

```python
import mlflow
import GPy
import numpy as np

class GPRARDModel:
    def __init__(self, config):
        self.config = config
        self.mlflow_info = config.get('mlflow_info', {})

    def select_bands_with_scores(self, spectral_data, labels, pre_selected_bands, target_bands):
        if self.mlflow_info:
            # 상위 파이프라인의 MLflow 환경 사용
            mlflow.set_experiment(self.mlflow_info['experiment_name'])

            with mlflow.start_run(nested=True, run_name="gpr_ard_training") as run:
                # 학습 파라미터 기록
                mlflow.log_param("kernel_type", self.config['training']['parameters']['kernel_type'])
                mlflow.log_param("alpha", self.config['training']['parameters']['alpha'])
                mlflow.log_param("num_epochs", self.config['training']['parameters']['num_epochs'])

                # GPy를 사용한 GPR+ARD 학습
                kernel = GPy.kern.RBF(input_dim=len(pre_selected_bands))
                m = GPy.models.GPRegression(
                    spectral_data[:, pre_selected_bands],
                    labels.reshape(-1, 1),
                    kernel
                )

                # 학습 과정 기록
                for epoch in range(self.config['training']['parameters']['num_epochs']):
                    m.optimize(messages=False, max_iters=1)
                    loss = m.log_likelihood()
                    mlflow.log_metric("log_likelihood", loss, step=epoch)

                # ARD 가중치를 기반으로 밴드 중요도 계산
                ard_weights = np.abs(m.kern.lengthscale.values[0])
                importance_scores = ard_weights / np.max(ard_weights)  # 0-1 정규화

                # 상위 target_bands개 선택
                top_indices = np.argsort(importance_scores)[-target_bands:]
                selected_bands = [pre_selected_bands[i] for i in top_indices]
                band_scores = [importance_scores[i] for i in top_indices]

                # 결과 기록
                mlflow.log_dict({"selected_bands": selected_bands}, "final_selection.json")
                mlflow.log_dict({"band_scores": band_scores}, "band_scores.json")
                mlflow.log_dict({"ard_weights": ard_weights.tolist()}, "ard_weights.json")

                return selected_bands, band_scores
        else:
            # MLflow 정보가 없는 경우
            selected_bands = pre_selected_bands[:target_bands]
            band_scores = [0.9, 0.8, 0.7, 0.6, 0.5]  # 기본값
            return selected_bands, band_scores
```

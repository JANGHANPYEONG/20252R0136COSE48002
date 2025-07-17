import numpy as np
import mlflow
from typing import Dict, Any, Tuple, List
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, Matern
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

class GPRARDBandSelector:
    """GPR+ARD 기반 밴드 선택기"""
    def __init__(self, config: Dict[str, Any], label_type: str = 'regression'):
        """
        GPR+ARD 밴드 선택기 초기화
        Args:
            config: 설정 딕셔너리
            label_type: 분류/회귀 타입 ('classification' 또는 'regression')
        """
        self.config = config
        self.mlflow_info = config.get('mlflow_info', {})
        self.parameters = config.get('training', {}).get('parameters', {})
        self.kernel_type = self.parameters.get('kernel_type', 'rbf')
        self.alpha = self.parameters.get('alpha', 1e-6)
        self.random_state = self.parameters.get('random_state', 42)
        self.n_restarts_optimizer = self.parameters.get('n_restarts_optimizer', 10)
        self.label_type = label_type
        # 결과 저장
        self.selected_bands = None
        self.band_scores = None
        self.feature_names = None
        self.model = None
        print(f"GPR+ARD Band Selector initialized with kernel: {self.kernel_type}, alpha: {self.alpha}, label_type: {self.label_type}")

    def select_bands_with_scores(self, spectral_data: np.ndarray, labels: np.ndarray, pre_selected_bands: List[int], target_bands: int) -> Tuple[List[int], List[float]]:
        """
        GPR+ARD를 사용하여 밴드 선택 수행
        Args:
            spectral_data: (n_samples, n_features)
            labels: (n_samples,)
            pre_selected_bands: 전처리된 밴드 인덱스
            target_bands: 선택할 밴드 수
        Returns:
            selected_bands: 선택된 밴드 인덱스
            selected_scores: 선택된 밴드의 중요도(1/length_scale)
        """
        if self.mlflow_info:
            with mlflow.start_run(nested=True):
                return self._select_bands_internal(spectral_data, labels, pre_selected_bands, target_bands)
        else:
            return self._select_bands_internal(spectral_data, labels, pre_selected_bands, target_bands)

    def _select_bands_internal(self, spectral_data: np.ndarray, labels: np.ndarray, pre_selected_bands: List[int], target_bands: int) -> Tuple[List[int], List[float]]:
        print(f"Starting GPR+ARD band selection with {target_bands} target bands...")
        # 전처리된 데이터 사용
        if pre_selected_bands is not None and len(pre_selected_bands) > 0:
            X = spectral_data[:, pre_selected_bands]
            print(f"Using {len(pre_selected_bands)} pre-selected bands")
        else:
            X = spectral_data
            pre_selected_bands = list(range(X.shape[1]))
            print(f"Using all {X.shape[1]} original bands")
        feature_names = [f'band_{i}' for i in pre_selected_bands]
        # 데이터 분할 (회귀만 지원)
        stratify = None
        try:
            X_train, X_test, y_train, y_test = train_test_split(
                X, labels, test_size=0.2, random_state=self.random_state, stratify=stratify
            )
        except Exception as e:
            print(f"Warning: Data split failed ({e}), using all data for training")
            X_train, y_train = X, labels
        # 커널 정의 (ARD)
        if self.kernel_type.lower() == 'rbf':
            kernel = RBF(length_scale=np.ones(X_train.shape[1]), length_scale_bounds=(1e-2, 1e3))
        elif self.kernel_type.lower() == 'matern':
            kernel = Matern(length_scale=np.ones(X_train.shape[1]), length_scale_bounds=(1e-2, 1e3), nu=2.5)
        else:
            raise ValueError(f"Unsupported kernel_type: {self.kernel_type}")
        # GPR 모델 학습
        self.model = GaussianProcessRegressor(
            kernel=kernel,
            alpha=self.alpha,
            n_restarts_optimizer=self.n_restarts_optimizer,
            random_state=self.random_state,
            normalize_y=True
        )
        self.model.fit(X_train, y_train)
        # ARD length_scale 추출 (작을수록 중요)
        length_scales = self.model.kernel_.length_scale
        importance = 1.0 / (length_scales + 1e-8)  # 값이 작을수록 중요하므로 역수
        # 상위 target_bands 선택
        top_indices = np.argsort(importance)[-target_bands:][::-1]
        selected_bands = [pre_selected_bands[i] for i in top_indices]
        selected_scores = importance[top_indices].tolist()
        # 결과 저장
        self.selected_bands = selected_bands
        self.band_scores = selected_scores
        self.feature_names = feature_names
        # MLflow 로깅
        if self.mlflow_info:
            label_name = self.mlflow_info.get('current_label', 'unknown')
            mlflow.log_param("gpr_kernel_type", self.kernel_type)
            mlflow.log_param("gpr_alpha", self.alpha)
            mlflow.log_param("gpr_n_restarts_optimizer", self.n_restarts_optimizer)
            mlflow.log_param("gpr_target_bands", target_bands)
            mlflow.log_param(f"gpr_selected_bands_{label_name}", len(selected_bands))
            mlflow.log_param(f"gpr_selected_indices_{label_name}", selected_bands)
            gpr_info = {
                'selected_bands': selected_bands,
                'selected_scores': selected_scores,
                'original_features': len(pre_selected_bands),
                'reduction_ratio': len(selected_bands) / len(pre_selected_bands),
                'method': 'gpr_ard',
                'kernel_type': self.kernel_type
            }
            mlflow.log_dict(gpr_info, "gpr_ard_selection_info.json")
            # length_scale 통계
            stats = {
                'mean_length_scale': float(np.mean(length_scales)),
                'std_length_scale': float(np.std(length_scales)),
                'min_length_scale': float(np.min(length_scales)),
                'max_length_scale': float(np.max(length_scales))
            }
            mlflow.log_dict(stats, "gpr_ard_length_scale_stats.json")
            # 모델 성능 로깅
            train_score = self.model.score(X_train, y_train)
            mlflow.log_metric("gpr_train_score", train_score)
        print(f"GPR+ARD band selection completed. Selected {len(selected_bands)} bands from {len(pre_selected_bands)} pre-selected bands.")
        return selected_bands, selected_scores

    def get_selected_bands(self) -> List[int]:
        return self.selected_bands if self.selected_bands is not None else []

    def get_band_scores(self) -> List[float]:
        return self.band_scores if self.band_scores is not None else []

    def get_feature_names(self) -> List[str]:
        return self.feature_names if self.feature_names is not None else []

def create_model(model_name: str, config: Dict[str, Any], label_type: str = 'regression') -> GPRARDBandSelector:
    """
    GPR+ARD 모델 생성 함수
    Args:
        model_name: 모델 이름
        config: 설정 딕셔너리
        label_type: 분류/회귀 타입 ('classification' 또는 'regression')
    Returns:
        GPRARDBandSelector 인스턴스
    """
    return GPRARDBandSelector(config, label_type) 
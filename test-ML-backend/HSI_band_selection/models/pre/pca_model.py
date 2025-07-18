import numpy as np
from sklearn.decomposition import PCA
from typing import List, Dict
import mlflow

class PreprocessingModel:
    def __init__(self, config):
        self.config = config
        # config를 필요에 따라 저장 (예: PCA 차원 등)
        """
        Args:
            config (dict): {
                "model_name": "pca",
                "method": "statistical",
                "parameters": {
                    "n_components": int, # PCA 성분 개수
                    "random_state": int  # 랜덤 시드
                }
            }
        """
        self.config = config
        self.mlflow_info = config.get("mlflow_info", {})
        self.n_components = config.get("parameters", {}).get("n_components", 1) # 주성분 개수
        self.random_state = config.get("parameters", {}).get("random_state", None) # 랜덤 시드
        self.device = config.get('device', 'cpu')

    def select_bands(self, spectral_data: np.ndarray, labels: np.ndarray, target_bands: int) -> List[int]:
        """
        밴드 선택을 수행합니다.

        Args:
            spectral_data: np.ndarray (n_samples, n_bands)
            labels: np.ndarray (n_samples, n_labels)
            target_bands: int (목표 밴드 수)

        Returns:
            selected_bands: List[int] (선택된 밴드 인덱스)
        """

        label_name = self.mlflow_info.get("current_label", "unknown")
        label_idx = self.mlflow_info.get("current_label_idx", -1)

        # 1. PCA 수행
        pca = PCA(n_components=target_bands)
        transformed = pca.fit_transform(spectral_data)

        # 2. 로딩 벡터 기반 기여도 분석
        loading_vectors = np.abs(pca.components_)
        mean_loading = loading_vectors.mean(axis=0)

        # 3. 상위 기여도 순으로 밴드 선택
        band_indices = np.argsort(mean_loading)[::-1][:target_bands]
        band_indices = sorted(band_indices.tolist())

        # 4. PCA 설명력 기록
        explained_variance = pca.explained_variance_ratio_
        explained_variance_sum = explained_variance.sum()

        mlflow.log_metric(f"pca_explained_variance_sum_{label_name}", explained_variance_sum)
        mlflow.log_dict(
            {
                "explained_variance_ratio": explained_variance.tolist(),
                "selected_band_indices": band_indices
            },
            f"preprocessing/pca_summary_{label_name}.json"
        )

        # 5. 복원 오차 계산
        reconstructed = pca.inverse_transform(transformed)
        reconstruction_error = np.mean((spectral_data - reconstructed) ** 2)

        mlflow.log_metric(f"pca_reconstruction_error_{label_name}", reconstruction_error)

        print(f"[{label_name}] PCA explained variance sum: {explained_variance_sum:.4f}")
        print(f"[{label_name}] PCA reconstruction error: {reconstruction_error:.6f}")
        print(f"[{label_name}] Selected Bands: {band_indices}")

        return band_indices

def create_model(model_name: str, config: Dict, label_type: str = None):
    if model_name == "pca":
        return PreprocessingModel(config)
    else:
        raise ValueError(f"Unknown model name: {model_name}")
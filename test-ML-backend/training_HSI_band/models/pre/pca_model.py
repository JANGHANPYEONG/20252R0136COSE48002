import numpy as np
from sklearn.decomposition import PCA
from typing import List, Dict

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
        # 1. PCA 수행
        pca = PCA(n_components=1)
        pca.fit(spectral_data)

        # 2. 첫 번째 주성분 로딩 벡터 가져오기
        pc1 = pca.components_[0]  # shape: (n_bands,)

        # 3. 절댓값 기준 상위 밴드 인덱스 선택
        top_indices = np.argsort(np.abs(pc1))[::-1][:target_bands]

        # 4. 반환값은 리스트 형태로
        selected_bands = top_indices.tolist()
        return selected_bands


def create_model(model_name: str, config: Dict) -> PreprocessingModel:
    return PreprocessingModel(config)
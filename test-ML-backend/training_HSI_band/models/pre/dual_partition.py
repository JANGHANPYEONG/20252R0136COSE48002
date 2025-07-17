import numpy as np
import pywt
from sklearn.cluster import AgglomerativeClustering
from typing import List, Dict

class PreprocessingModel:
    def __init__(self, config: Dict, full_hsi_data: np.ndarray):
        """
        Args:
            config: 설정 딕셔너리, key "preprocessing" -> "parameters"에 n_clusters, top_k, k_neighbors 포함
            full_hsi_data: 원본 HSI 데이터, shape = (n_samples, H, W, n_bands)
        """
        params = config["preprocessing"]["parameters"]
        self.n_clusters = params.get("n_clusters")
        self.top_k = params.get("top_k")
        self.k_neighbors = params.get("k_neighbors")
        self.full_hsi_data = full_hsi_data  # (N, H, W, B_full)

    def select_bands(self, target_bands: int) -> List[int]:
        """
        Dual Partitioning & Wavelet 에너지 기반 밴드 우선순위화

        Args:
            target_bands: 최종 선택할 밴드 수
        Returns:
            List[int]: 선택된 밴드 인덱스
        """
        # full_hsi_data: (N, H, W, B_full)
        N, H, W, B_full = self.full_hsi_data.shape
        # 공간 픽셀별 스펙트럼(flatten)
        flat = self.full_hsi_data.reshape(N * H * W, B_full)

        # 밴드 상관관계 및 계층적 클러스터링
        corr = np.corrcoef(flat.T)
        hc = AgglomerativeClustering(n_clusters=self.n_clusters,
                                     metric='precomputed', linkage='average')
        labels_cluster = hc.fit_predict(1 - np.abs(corr))

        # 서브클러스터 재구성
        subclusters: Dict[int, List[np.ndarray]] = {}
        for cl in range(self.n_clusters):
            idx = np.where(labels_cluster == cl)[0]
            if len(idx) <= self.k_neighbors:
                subclusters[cl] = [idx]
            else:
                sub_corr = np.corrcoef(flat[:, idx].T)
                graph = 1 - np.abs(sub_corr)
                sub_hc = AgglomerativeClustering(
                    n_clusters=self.k_neighbors,
                    metric='precomputed', linkage='average'
                )
                sub_labels = sub_hc.fit_predict(graph)
                subclusters[cl] = [idx[sub_labels == sc] for sc in np.unique(sub_labels)]

        # Wavelet 에너지 순위화
        selected: List[int] = []
        for groups in subclusters.values():
            for grp in groups:
                energy_list: List[Tuple[int, float]] = []
                for b in grp:
                    coeffs = pywt.wavedec(flat[:, b], wavelet='db1', level=2)
                    energy = sum((c ** 2).sum() for c in coeffs)
                    energy_list.append((b, energy))
                # 에너지 내림차순
                energy_list.sort(key=lambda x: x[1], reverse=True)
                # 그룹별 top_k 밴드 추가
                selected.extend([b for b, _ in energy_list[: self.top_k]])

        # 최종 target_bands 반환
        return selected[:target_bands]


def create_model(model_name: str,
                 config: Dict,
                 full_hsi_data: np.ndarray) -> PreprocessingModel:
    if model_name == "dual_partition":
        return PreprocessingModel(config, full_hsi_data)
    raise ValueError(f"Unknown model name: {model_name}")

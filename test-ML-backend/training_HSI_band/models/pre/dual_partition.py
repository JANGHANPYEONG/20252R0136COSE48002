import numpy as np
import pywt
from sklearn.cluster import AgglomerativeClustering
from typing import List, Dict
import torch
import torch.nn as nn
from sklearn.neighbors import NearestNeighbors


class PreprocessingModel:
    def __init__(self, config: Dict):
        params = config["preprocessing"]["parameters"]
        self.n_clusters = params.get("n_clusters")
        self.top_k = params.get("top_k")
        self.k_neighbors = params.get("k_neighbors")
        params = config["preprocessing"]["parameters"]
        self.n_clusters = params.get("n_clusters")
        self.top_k = params.get("top_k")
        self.k_neighbors = params.get("k_neighbors")

    def select_bands(self, spectral_data: np.ndarray, labels: np.ndarray, target_bands: int) -> List[int]:
        """
        이중 분할(Dual Partitioning) 및 웨이브릿 기반 밴드 우선순위화

        Args:
            spectral_data: np.ndarray (n_samples, n_bands)
            labels: np.ndarray (n_samples, n_labels)  # 사용하지 않음
            target_bands: int (목표 밴드 수)

        Returns:
            selected_bands: List[int] (선택된 밴드 인덱스)
        """
        # 1차 분할: 밴드 간 상관관계 기반 클러스터링
        corr = np.corrcoef(spectral_data.T)
        clusterer = AgglomerativeClustering(n_clusters=self.n_clusters, metric='precomputed', linkage='average')
        cluster_labels = clusterer.fit_predict(1 - np.abs(corr))

        # 2차 분할: 밴드 내 이웃 기반 neighborhood 재구성
        subclusters = {}
        for cl in range(self.n_clusters):
            idx = np.where(cluster_labels == cl)[0]
            if len(idx) < self.k_neighbors:
                subclusters[cl] = [idx]
                continue
            sub_corr = np.corrcoef(spectral_data[:, idx].T)
            nn_graph = 1 - np.abs(sub_corr)
            sub_clusterer = AgglomerativeClustering(n_clusters=min(len(idx), self.k_neighbors), metric='precomputed', linkage='average')
            sub_labels = sub_clusterer.fit_predict(nn_graph)
            subclusters[cl] = [idx[np.where(sub_labels == sub_cl)[0]] for sub_cl in np.unique(sub_labels)]

        # 웨이브릿 에너지 기반 우선순위화
        selected_bands = []
        for cl in subclusters:
            for group in subclusters[cl]:
                energies = []
                for b in group:
                    coeffs = pywt.wavedec(spectral_data[:, b], wavelet='db1', level=2)
                    energy = sum((c ** 2).sum() for c in coeffs)
                    energies.append((b, energy))
                energies.sort(key=lambda x: x[1], reverse=True)
                selected_bands.extend([b for b, _ in energies[:self.top_k]])

        return selected_bands[:target_bands]


# __init__.py 내부에서 호출되는 factory 함수

def create_model(model_name, config):
    if model_name == "dual_partition":
        return PreprocessingModel(config)
    else:
        raise ValueError(f"Unknown model name: {model_name}")

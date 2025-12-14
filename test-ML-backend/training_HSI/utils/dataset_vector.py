"""
분광 벡터 특징을 로딩해 학습/평가에 사용할 Dataset 헬퍼를 제공하는 모듈.

CSV/컬럼 설정을 기반으로 스펙트럴 밴드를 분리하고 라벨 정보를 구성한다.
"""

import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, Subset
from typing import Dict, List, Tuple, Optional
import os
from sklearn.model_selection import train_test_split

class VectorDataset(Dataset):
    """반사율 벡터 데이터를 로딩하는 Dataset 클래스"""
    
    def __init__(self, csv_path, column_config_path, indices=None):
        """
        Args:
            csv_path: CSV 파일 경로
            column_config_path: 컬럼 설정 파일 경로
            indices: 사용할 데이터 인덱스 리스트 (None이면 전체 사용)
        """
        self.csv_path = csv_path
        self.column_config_path = column_config_path
        self.indices = indices
        
        # CSV 로딩
        self.data = self._load_csv()
        self.column_config = self._load_column_config(self.column_config_path)

        if self.indices is not None:
            self.data = self.data.iloc[self.indices].reset_index(drop=True)
        
        # 반사율 벡터와 라벨 분리 (컬럼 순서 기반)
        self.spectral_data = self._extract_spectral_data()
        self.labels = self._extract_labels()
        
        print(f"Loaded {len(self.data)} samples")
        print(f"Spectral bands: {self.spectral_data.shape[1]}")
    
    def _load_csv(self) -> pd.DataFrame:
        """CSV 파일을 로딩합니다."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        # 첫 번째 행을 헤더로 사용
        data = pd.read_csv(self.csv_path, header=0)
        
        # 컬럼 수 검증 (최소 컬럼 수 확인)
        min_columns = 7  # ID(1) + 라벨(5) + 벡터(최소 1)
        if len(data.columns) < min_columns:
            raise ValueError(f"CSV must have at least {min_columns} columns, got {len(data.columns)}")

        return data
    
    def _load_column_config(self, config_path: str) -> Dict:
        """컬럼 설정 파일을 로드합니다."""
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Column config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config
    
    def _extract_labels(self) -> np.ndarray:
        """반사율 벡터 데이터를 추출합니다 (컬럼 순서 기반)."""
        start_idx = self.column_config['column_order']['label_start_index']
        end_idx = self.column_config['column_order']['vector_start_index']

        spectral_data = self.data.iloc[:, start_idx:end_idx].values.astype(np.float32)
        
        # NaN 값 처리
        if np.isnan(spectral_data).any():
            print("Warning: NaN values found in spectral data. Replacing with 0.")
            spectral_data = np.nan_to_num(spectral_data, nan=0.0)
        
        return spectral_data

    def _extract_spectral_data(self) -> np.ndarray:
        """라벨 데이터를 추출합니다 (컬럼 순서 기반)."""
        start_idx = self.column_config['column_order']['vector_start_index']
        end_idx = self.column_config['column_order']['image_path_start_index']

        labels = self.data.iloc[:, start_idx:end_idx].values.astype(np.float32)
        
        # NaN 값 처리
        if np.isnan(labels).any():
            print("Warning: NaN values found in labels. Replacing with 0.")
            labels = np.nan_to_num(labels, nan=0.0)
        
        return labels
    
    def __len__(self) -> int:
        return len(self.data)
    

def load_vector_data(csv_path, column_config_path, indices=None):
    """
    Vector 데이터를 로딩하고, 각 라벨별 pos_weight 정보를 함께 반환합니다.

    Returns:
        dataset: VectorDataset
        pos_weight_info: dict with keys
            - 'pos_weight': [neg/pos 비율 리스트]
            - 'pos_counts' : [positive 샘플 수 리스트]
            - 'neg_counts' : [negative 샘플 수 리스트]
    """
    # 1) 기존 로직으로 데이터셋 생성
    dataset = VectorDataset(csv_path, column_config_path, indices=indices)

    # 2) labels 배열 가져오기 (shape: [n_samples, n_labels])
    labels = dataset.labels
    n_samples = labels.shape[0]

    # 3) positive/negative 개수 계산
    pos_counts = labels.sum(axis=0)  # 각 라벨당 positive 샘플 수
    neg_counts = n_samples - pos_counts

    # 4) pos_weight 계산 (neg/pos)
    eps = 1e-6
    pos_weight = (neg_counts / (pos_counts + eps)).tolist()

    pos_weight_info = {
        'pos_weight': pos_weight,
        'pos_counts' : pos_counts.tolist(),
        'neg_counts' : neg_counts.tolist()
    }

    return dataset, pos_weight_info


def get_label_info(column_config_path):
    """라벨 정보를 반환합니다."""
    with open(column_config_path, 'r') as f:
        config = json.load(f)
    
    return {
        'label_columns': config['label_columns'],
        'label_types': config['label_types'],
        'num_classes': len(config['label_columns'])
    } 

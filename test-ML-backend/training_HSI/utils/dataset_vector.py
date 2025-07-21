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
    

def load_vector_data(csv_path, column_config_path, indices=None) -> VectorDataset:
    """Vector 데이터를 로딩하는 편의 함수"""
    return VectorDataset(csv_path, column_config_path, indices=indices)

def split_vector_data(dataset: VectorDataset, train_ratio: float = 0.8, 
                     val_ratio: float = 0.1, test_ratio: float = 0.1,
                     random_state: int = 42) -> Tuple[VectorDataset, VectorDataset, VectorDataset]:
    """
    데이터셋을 train/val/test로 분할합니다.
    
    Args:
        dataset: 분할할 데이터셋
        train_ratio: 학습 데이터 비율 (기본값: 0.8)
        val_ratio: 검증 데이터 비율 (기본값: 0.1)
        test_ratio: 테스트 데이터 비율 (기본값: 0.1)
        random_state: 랜덤 시드 (기본값: 42)
        
    Returns:
        train_dataset, val_dataset, test_dataset: 분할된 데이터셋들
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
    
    total_size = len(dataset)
    indices = np.arange(total_size)
    
    # 첫 번째 분할: train + (val + test)
    train_size = int(total_size * train_ratio)
    remaining_size = total_size - train_size
    
    # stratify를 위한 라벨 정보 준비 (멀티라벨의 경우 첫 번째 라벨 사용)
    labels_for_stratify = dataset.labels[:, 0] if dataset.labels.shape[1] > 0 else None
    
    # train과 나머지로 분할
    train_indices, remaining_indices = train_test_split(
        indices,
        train_size=train_size,
        random_state=random_state,
        stratify=labels_for_stratify
    )
    
    # 나머지를 val과 test로 분할
    val_size = int(remaining_size * (val_ratio / (val_ratio + test_ratio)))
    
    # val/test 분할을 위한 라벨 정보
    remaining_labels = labels_for_stratify[remaining_indices] if labels_for_stratify is not None else None
    
    val_indices, test_indices = train_test_split(
        remaining_indices,
        train_size=val_size,
        random_state=random_state,
        stratify=remaining_labels
    )
    
    # Subset을 사용하여 데이터셋 분할
    train_dataset = Subset(dataset, train_indices)
    val_dataset = Subset(dataset, val_indices)
    test_dataset = Subset(dataset, test_indices)
    
    print(f"Dataset split: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")
    
    # 분할 결과 검증 (라벨 분포 확인)
    if dataset.labels.shape[1] > 0:
        print("Label distribution check:")
        for i, (name, subset) in enumerate([("Train", train_indices), ("Val", val_indices), ("Test", test_indices)]):
            subset_labels = dataset.labels[subset]
            print(f"  {name}: {len(subset)} samples")
            for j in range(dataset.labels.shape[1]):
                positive_ratio = np.mean(subset_labels[:, j])
                print(f"    Label {j}: {positive_ratio:.3f} positive ratio")
    
    return train_dataset, val_dataset, test_dataset

def get_label_info(column_config_path):
    """라벨 정보를 반환합니다."""
    with open(column_config_path, 'r') as f:
        config = json.load(f)
    
    return {
        'label_columns': config['label_columns'],
        'label_types': config['label_types'],
        'num_classes': len(config['label_columns'])
    } 
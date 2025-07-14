import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, Subset
from typing import Dict, List, Tuple, Optional
import os

from utils.column_info import (
    get_csv_structure, get_spectral_columns, 
    get_id_column, get_label_columns, get_vector_columns
)

class VectorDataset(Dataset):
    """반사율 벡터 데이터를 로딩하는 Dataset 클래스"""
    
    def __init__(self, csv_path: str, config: Dict, is_train: bool = True):
        """
        Args:
            csv_path: CSV 파일 경로
            config: 설정 딕셔너리
            is_train: 학습용 데이터인지 여부
        """
        self.csv_path = csv_path
        self.config = config
        self.is_train = is_train
        
        # CSV 로딩
        self.data = self._load_csv()
        
        # 컬럼 정보 가져오기
        self.column_info = get_csv_structure()
        
        # 반사율 벡터와 라벨 분리 (컬럼 순서 기반)
        self.spectral_data = self._extract_spectral_data()
        self.labels = self._extract_labels()
        
        print(f"Loaded {len(self.data)} samples")
        print(f"Spectral bands: {self.spectral_data.shape[1]}")
        print(f"Labels: {len(self.column_info['label_columns'])}")
    
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
    
    def _extract_spectral_data(self) -> np.ndarray:
        """반사율 벡터 데이터를 추출합니다 (컬럼 순서 기반)."""
        spectral_data = get_vector_columns(self.data).values.astype(np.float32)
        
        # NaN 값 처리
        if np.isnan(spectral_data).any():
            print("Warning: NaN values found in spectral data. Replacing with 0.")
            spectral_data = np.nan_to_num(spectral_data, nan=0.0)
        
        return spectral_data
    
    def _extract_labels(self) -> np.ndarray:
        """라벨 데이터를 추출합니다 (컬럼 순서 기반)."""
        labels = get_label_columns(self.data).values.astype(np.float32)
        
        # NaN 값 처리
        if np.isnan(labels).any():
            print("Warning: NaN values found in labels. Replacing with 0.")
            labels = np.nan_to_num(labels, nan=0.0)
        
        return labels
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str]:
        """
        Args:
            idx: 샘플 인덱스
            
        Returns:
            spectral_vector: 반사율 벡터 (torch.Tensor)
            labels: 라벨 벡터 (torch.Tensor)
            sample_id: 샘플 ID (str)
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        # 반사율 벡터
        spectral_vector = torch.tensor(self.spectral_data[idx], dtype=torch.float32)
        
        # 라벨
        labels = torch.tensor(self.labels[idx], dtype=torch.float32)
        
        # 샘플 ID (컬럼 순서 기반)
        sample_id = str(get_id_column(self.data).iloc[idx])
        
        return spectral_vector, labels, sample_id
    
    def get_spectral_info(self) -> Dict:
        """반사율 데이터 정보를 반환합니다."""
        return {
            "num_samples": len(self.data),
            "num_bands": self.spectral_data.shape[1],
            "num_labels": len(self.column_info['label_columns']),
            "spectral_range": f"{get_spectral_columns()[0]} to {get_spectral_columns()[-1]}",
            "label_columns": self.column_info['label_columns']
        }

def load_vector_data(csv_path: str, config: Dict, is_train: bool = True) -> VectorDataset:
    """Vector 데이터를 로딩하는 편의 함수"""
    return VectorDataset(csv_path, config, is_train)

def split_vector_data(dataset: VectorDataset, train_ratio: float = 0.8, 
                     val_ratio: float = 0.1, test_ratio: float = 0.1) -> Tuple[VectorDataset, VectorDataset, VectorDataset]:
    """데이터셋을 train/val/test로 분할합니다."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1.0"
    
    total_size = len(dataset)
    train_size = int(total_size * train_ratio)
    val_size = int(total_size * val_ratio)
    
    # 인덱스 분할
    indices = list(range(total_size))
    train_indices = indices[:train_size]
    val_indices = indices[train_size:train_size + val_size]
    test_indices = indices[train_size + val_size:]
    
    # Subset을 사용하여 데이터셋 분할
    train_dataset = Subset(dataset, train_indices)
    val_dataset = Subset(dataset, val_indices)
    test_dataset = Subset(dataset, test_indices)
    
    print(f"Dataset split: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")
    
    return train_dataset, val_dataset, test_dataset 
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, Subset
from typing import Dict, List, Tuple, Optional
import os
from sklearn.model_selection import train_test_split
from PIL import Image
import torchvision.transforms as transforms

from utils.column_info import (
    get_csv_structure, get_spectral_columns, 
    get_id_column, get_label_columns, get_vector_columns,
    get_image_path_columns_data
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

class ImageDataset(Dataset):
    """HSI 이미지 데이터를 로딩하는 Dataset 클래스"""
    
    def __init__(self, csv_path: str, config: Dict, is_train: bool = True, 
                 transform: Optional[transforms.Compose] = None):
        """
        Args:
            csv_path: CSV 파일 경로
            config: 설정 딕셔너리
            is_train: 학습용 데이터인지 여부
            transform: 이미지 변환 (기본값: None)
        """
        self.csv_path = csv_path
        self.config = config
        self.is_train = is_train
        self.transform = transform
        
        # CSV 로딩
        self.data = self._load_csv()
        
        # 컬럼 정보 가져오기
        self.column_info = get_csv_structure()
        
        # 이미지 경로와 라벨 분리
        self.image_paths = self._extract_image_paths()
        self.labels = self._extract_labels()
        
        # 이미지 크기 확인
        self.image_size = self.column_info.get('image_size', [256, 256])
        
        print(f"Loaded {len(self.data)} samples")
        print(f"Number of spectral bands: {len(self.image_paths[0]) if self.image_paths else 0}")
        print(f"Labels: {len(self.column_info['label_columns'])}")
        print(f"Image size: {self.image_size}")
    
    def _load_csv(self) -> pd.DataFrame:
        """CSV 파일을 로딩합니다."""
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        
        # 첫 번째 행을 헤더로 사용
        data = pd.read_csv(self.csv_path, header=0)
        
        return data
    
    def _extract_image_paths(self) -> List[List[str]]:
        """이미지 경로들을 추출합니다."""
        image_path_data = get_image_path_columns_data(self.data)
        
        # 각 샘플의 이미지 경로들을 리스트로 변환
        image_paths = []
        for _, row in image_path_data.iterrows():
            sample_paths = []
            for path in row:
                if pd.isna(path) or path == '':
                    raise ValueError(f"Empty or missing image path found: {path}")
                sample_paths.append(str(path))
            image_paths.append(sample_paths)
        
        return image_paths
    
    def _extract_labels(self) -> np.ndarray:
        """라벨 데이터를 추출합니다."""
        labels = get_label_columns(self.data).values.astype(np.float32)
        
        # NaN 값 처리
        if np.isnan(labels).any():
            print("Warning: NaN values found in labels. Replacing with 0.")
            labels = np.nan_to_num(labels, nan=0.0)
        
        return labels
    
    def _load_image(self, image_path: str) -> torch.Tensor:
        """단일 이미지를 로딩합니다."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # PIL로 이미지 로딩 (그레이스케일)
        image = Image.open(image_path).convert('L')
        
        # 기본 변환 (크기 조정 및 텐서 변환)
        if self.transform is None:
            transform = transforms.Compose([
                transforms.Resize(self.image_size),
                transforms.ToTensor(),
            ])
        else:
            transform = self.transform
        
        return transform(image)
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, str]:
        """
        Args:
            idx: 샘플 인덱스
            
        Returns:
            spectral_images: 스펙트럴 이미지들 (torch.Tensor, shape: [num_bands, H, W])
            labels: 라벨 벡터 (torch.Tensor)
            sample_id: 샘플 ID (str)
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()
        
        # 모든 밴드의 이미지 로딩
        spectral_images = []
        for image_path in self.image_paths[idx]:
            image = self._load_image(image_path)
            spectral_images.append(image)
        
        # [num_bands, H, W] 형태로 스택
        spectral_images = torch.stack(spectral_images, dim=0)
        
        # 라벨
        labels = torch.tensor(self.labels[idx], dtype=torch.float32)
        
        # 샘플 ID
        sample_id = str(get_id_column(self.data).iloc[idx])
        
        return spectral_images, labels, sample_id
    
    def get_image_info(self) -> Dict:
        """이미지 데이터 정보를 반환합니다."""
        return {
            "num_samples": len(self.data),
            "num_bands": len(self.image_paths[0]) if self.image_paths else 0,
            "num_labels": len(self.column_info['label_columns']),
            "image_size": self.image_size,
            "label_columns": self.column_info['label_columns']
        }

def load_vector_data(csv_path: str, config: Dict, is_train: bool = True) -> VectorDataset:
    """Vector 데이터를 로딩하는 편의 함수"""
    return VectorDataset(csv_path, config, is_train)

def load_image_data(csv_path: str, config: Dict, is_train: bool = True, 
                   transform: Optional[transforms.Compose] = None) -> ImageDataset:
    """Image 데이터를 로딩하는 편의 함수"""
    return ImageDataset(csv_path, config, is_train, transform)

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

def split_image_data(dataset: ImageDataset, train_ratio: float = 0.8, 
                    val_ratio: float = 0.1, test_ratio: float = 0.1,
                    random_state: int = 42) -> Tuple[ImageDataset, ImageDataset, ImageDataset]:
    """
    이미지 데이터셋을 train/val/test로 분할합니다.
    
    Args:
        dataset: 분할할 이미지 데이터셋
        train_ratio: 학습 데이터 비율 (기본값: 0.8)
        val_ratio: 검증 데이터 비율 (기본값: 0.1)
        test_ratio: 테스트 데이터 비율 (기본값: 0.1)
        random_state: 랜덤 시드 (기본값: 42)
        
    Returns:
        train_dataset, val_dataset, test_dataset: 분할된 이미지 데이터셋들
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
    
    print(f"Image dataset split: Train={len(train_dataset)}, Val={len(val_dataset)}, Test={len(test_dataset)}")
    
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
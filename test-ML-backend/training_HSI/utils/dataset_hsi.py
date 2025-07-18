import os
import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from PIL import Image
import warnings
warnings.filterwarnings('ignore')


class HSIDataset(Dataset):
    """HSI 데이터셋 클래스"""
    
    def __init__(self, csv_path, column_config_path, transform=None, scaler=None, fit_scaler=True, indices=None):
        """
        Args:
            csv_path: CSV 파일 경로
            column_config_path: 컬럼 설정 파일 경로
            transform: 이미지 변환
            scaler: StandardScaler 객체 (None이면 새로 생성)
            fit_scaler: 스케일러를 fit할지 여부
            indices: 사용할 데이터 인덱스 리스트 (None이면 전체 사용)
        """
        self.csv_path = csv_path
        self.column_config_path = column_config_path
        self.transform = transform
        self.indices = indices
        
        # 설정 로드
        self.column_config = self._load_column_config()
        self.data = self._load_data()
        
        # 인덱스 필터링 적용
        if self.indices is not None:
            self.data = self.data.iloc[self.indices].reset_index(drop=True)
        
        # 스케일러 설정
        if scaler is None:
            self.scaler = StandardScaler()
        else:
            self.scaler = scaler
            
        if fit_scaler:
            self._fit_scaler()
        
        # 캐시 텐서 생성 (메모리 최적화) - 안전한 초기화
        if hasattr(self.scaler, "mean_") and hasattr(self.scaler, "scale_"):
            self._mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
            self._scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
        else:
            self._mean_tensor = None
            self._scale_tensor = None
        # 정규화 텐서를 한 번만 디바이스로 이동 (삭제)
    
    def _load_column_config(self):
        """컬럼 설정을 로드합니다."""
        with open(self.column_config_path, 'r') as f:
            return json.load(f)
    
    def _load_data(self):
        """CSV 데이터를 로드합니다."""
        return pd.read_csv(self.csv_path)
    
    def _fit_scaler(self, sample_ratio=0.05, max_samples=50, max_pixels_per_sample=1000):
        """스케일러를 학습 데이터로 fit합니다."""
        print("Fitting StandardScaler...")
        
        # 무작위 샘플 인덱스 선택
        num_samples = min(max_samples, len(self.data))
        if num_samples > 0:
            sample_indices = np.random.choice(self.data.index, num_samples, replace=False)
        else:
            sample_indices = []
        all_image_data = []
        for idx in sample_indices:
            image_cube = self._load_image_cube(idx)
            if image_cube is not None:
                h, w, c = image_cube.shape
                total_pixels = h * w
                pixels_to_sample = max(1, int(sample_ratio * total_pixels))
                pixels_to_sample = min(pixels_to_sample, max_pixels_per_sample)
                if total_pixels > pixels_to_sample:
                    pixel_indices = np.random.choice(total_pixels, pixels_to_sample, replace=False)
                    sampled_pixels = image_cube.reshape(-1, c)[pixel_indices]
                    all_image_data.append(sampled_pixels)
                else:
                    all_image_data.append(image_cube.reshape(-1, c))
        if all_image_data:
            all_image_data = np.concatenate(all_image_data, axis=0)
            self.scaler.fit(all_image_data)
            print(f"Scaler fitted with {len(all_image_data)} pixels from {num_samples} samples (ratio: {sample_ratio})")
            self._mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
            self._scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
    
    def _load_image_cube(self, idx):
        """인덱스에 해당하는 이미지 큐브를 로드합니다."""
        row = self.data.iloc[idx]
        wavelengths = self.column_config['wavelengths']
        image_size = self.column_config['image_size']
        image_path_start = self.column_config['column_order']['image_path_start_index']
        image_paths = []
        for i, wavelength in enumerate(wavelengths):
            col_idx = image_path_start + i
            if col_idx < len(row):
                image_path = row.iloc[col_idx]
                if pd.notna(image_path) and image_path != '':
                    image_paths.append(image_path)
                else:
                    return None
            else:
                return None
        image_cube = []
        for image_path in image_paths:
            try:
                if not os.path.isabs(image_path):
                    from pathlib import Path
                    base_dir = Path(self.csv_path).parent
                    image_path = str(base_dir.parent / 'image' / image_path)
                if os.path.exists(image_path):
                    img = Image.open(image_path).convert('L')
                    img = img.resize(image_size, resample=Image.NEAREST)
                    img_array = np.array(img, dtype=np.float32) / 255.0
                    image_cube.append(img_array)
                else:
                    print(f"[Missing Image] row_id={idx} | path={image_path} | wavelength_idx={i}")
                    return None
            except Exception as e:
                print(f"[Error Loading] row_id={idx} | path={image_path} | wavelength_idx={i} | error={e}")
                return None
        if len(image_cube) == len(wavelengths):
            image_cube = np.stack(image_cube, axis=-1)
            return image_cube
        else:
            return None
    
    def _get_labels(self, idx):
        """인덱스에 해당하는 라벨을 추출합니다."""
        row = self.data.iloc[idx]
        label_start = self.column_config['column_order']['label_start_index']
        label_columns = self.column_config['label_columns']
        
        labels = []
        for i, label_col in enumerate(label_columns):
            col_idx = label_start + i
            if col_idx < len(row):
                label_value = row.iloc[col_idx]
                if pd.notna(label_value):
                    labels.append(float(label_value))
                else:
                    labels.append(0.0)  # 기본값
            else:
                labels.append(0.0)
        
        return np.array(labels, dtype=np.float32)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        # 이미지 큐브 로드
        image_cube = self._load_image_cube(idx)
        if image_cube is None:
            # 에러 시 더미 데이터 반환
            image_cube = np.zeros((*self.column_config['image_size'], len(self.column_config['wavelengths'])), dtype=np.float32)
        
        # NaN/Inf 값 처리 (정규화 전에 적용)
        image_cube = np.nan_to_num(image_cube, nan=0.0, posinf=1.0, neginf=0.0)
        
        # 라벨 추출
        labels = self._get_labels(idx)
        
        # 텐서로 변환 (GPU 친화적 정규화를 위해 먼저 텐서로 변환)
        image_tensor = torch.from_numpy(image_cube).permute(2, 0, 1)  # (C, H, W)
        label_tensor = torch.from_numpy(labels)
        
        # 캐시된 텐서 사용하여 정규화 (dtype 일치 보장) - 안전한 정규화
        if self._mean_tensor is None or self._scale_tensor is None:
            # Lazy 텐서 생성 (fit_scaler=False인 경우)
            if hasattr(self.scaler, "mean_") and hasattr(self.scaler, "scale_"):
                self._mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
                self._scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
            else:
                # 스케일러가 아직 fit되지 않은 경우 정규화 없이 반환
                if self.transform:
                    image_tensor = self.transform(image_tensor)
                return image_tensor, label_tensor, idx
        
        mean = self._mean_tensor
        scale = self._scale_tensor
        
        # scale 값이 0일 경우 NaN 방지
        eps = 1e-6
        scale = torch.clamp(scale, min=eps)
        
        # 변환(transform) 먼저 적용
        if self.transform:
            image_tensor = self.transform(image_tensor)
        image_tensor = (image_tensor - mean) / scale
        
        return image_tensor, label_tensor, idx


def create_hsi_data_loaders(csv_path, column_config_path, batch_size=8, num_workers=4, 
                           val_split=0.1, test_split=0.1, random_state=42, 
                           train_transform=None, val_transform=None, test_transform=None):
    """
    HSI 데이터 로더를 생성합니다.
    
    Args:
        csv_path: CSV 파일 경로
        column_config_path: 컬럼 설정 파일 경로
        batch_size: 배치 크기
        num_workers: 워커 수
        val_split: 검증 데이터 비율
        test_split: 테스트 데이터 비율
        random_state: 랜덤 시드
        train_transform: 훈련용 transform
        val_transform: 검증용 transform
        test_transform: 테스트용 transform
    
    Returns:
        train_loader, val_loader, test_loader, scaler
    """
    # 1. 전체 데이터 로드 (스케일러 fit 없이)
    full_dataset = HSIDataset(csv_path, column_config_path, fit_scaler=False)
    
    # 2. 인덱스 분할
    total_size = len(full_dataset)
    val_size = int(total_size * val_split)
    test_size = int(total_size * test_split)
    train_size = total_size - val_size - test_size
    
    # sklearn의 train_test_split 사용하여 인덱스 분할
    from sklearn.model_selection import train_test_split
    
    all_indices = list(range(total_size))
    train_indices, temp_indices = train_test_split(
        all_indices, test_size=val_size + test_size, 
        random_state=random_state, shuffle=True
    )
    
    val_prop = val_split / (val_split + test_split)
    val_indices, test_indices = train_test_split(
        temp_indices, test_size=1 - val_prop, random_state=random_state, shuffle=True
    )
    
    # 3. 각 subset에 대해 별도의 Dataset 생성
    # Train dataset (스케일러 fit)
    train_dataset = HSIDataset(
        csv_path, column_config_path, 
        transform=train_transform, 
        fit_scaler=True, 
        indices=train_indices
    )
    scaler = train_dataset.scaler
    
    # Val dataset (스케일러 fit 없음)
    val_dataset = HSIDataset(
        csv_path, column_config_path, 
        transform=val_transform, 
        scaler=scaler, 
        fit_scaler=False, 
        indices=val_indices
    )
    
    # Test dataset (스케일러 fit 없음)
    test_dataset = HSIDataset(
        csv_path, column_config_path, 
        transform=test_transform, 
        scaler=scaler, 
        fit_scaler=False, 
        indices=test_indices
    )
    
    # 데이터 로더 생성
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True
    )
    
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True
    )
    
    print(f"Data loaders created:")
    print(f"  Train: {len(train_dataset)} samples")
    print(f"  Val: {len(val_dataset)} samples")
    print(f"  Test: {len(test_dataset)} samples")
    
    return train_loader, val_loader, test_loader, scaler


def get_label_info(column_config_path):
    """라벨 정보를 반환합니다."""
    with open(column_config_path, 'r') as f:
        config = json.load(f)
    
    return {
        'label_columns': config['label_columns'],
        'label_types': config['label_types'],
        'num_classes': len(config['label_columns'])
    } 
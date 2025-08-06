import os
import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split, Subset
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from PIL import Image
import warnings
warnings.filterwarnings('ignore')


class HSIDataset(Dataset):
    """HSI 데이터셋 클래스 (scaler_mode: 'normalized', 'raw', 'off' 지원)"""
    
    def __init__(self, csv_path, column_config_path, transform=None, scaler=None, fit_scaler=True, indices=None, scaler_mode="normalized"):
        """
        Args:
            csv_path: CSV 파일 경로
            column_config_path: 컬럼 설정 파일 경로
            transform: 이미지 변환
            scaler: StandardScaler 객체 (None이면 새로 생성)
            fit_scaler: 스케일러를 fit할지 여부
            indices: 사용할 데이터 인덱스 리스트 (None이면 전체 사용)
            scaler_mode: 'normalized' | 'raw' | 'off' (config["data"]["scaler_mode"]에서만 설정)
        """
        self.csv_path = csv_path
        self.column_config_path = column_config_path
        self.transform = transform
        self.indices = indices
        self.scaler_mode = scaler_mode
        assert self.scaler_mode in {"normalized", "raw", "off"}, f"Invalid scaler_mode: {self.scaler_mode}"
        
        # 설정 로드
        self.column_config = self._load_column_config()
        self.data = self._load_data()
        
        # 인덱스 필터링 적용
        if self.indices is not None:
            self.data = self.data.iloc[self.indices].reset_index(drop=True)
        
        # 스케일러 설정
        if self.scaler_mode != "off":
            if scaler is None:
                self.scaler = StandardScaler()
            else:
                self.scaler = scaler
            if fit_scaler:
                self._fit_scaler()
            if hasattr(self.scaler, "mean_") and hasattr(self.scaler, "scale_"):
                self._mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
                self._scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
            else:
                self._mean_tensor = None
                self._scale_tensor = None
        else:
            self.scaler = None
            self._mean_tensor = None
            self._scale_tensor = None
    
    def _load_column_config(self):
        """컬럼 설정을 로드합니다."""
        with open(self.column_config_path, 'r') as f:
            return json.load(f)
    
    def _load_data(self):
        """CSV 데이터를 로드합니다."""
        return pd.read_csv(self.csv_path)
    
    def _fit_scaler(self, sample_ratio=0.05, max_samples=50, max_pixels_per_sample=1000):
        """스케일러를 학습 데이터로 fit합니다 (off 모드에서는 호출되지 않음)."""
        if self.scaler_mode == "off":
            return
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
                    img_array = np.array(img, dtype=np.float32)
                    # 0-1 scaling only for normalized mode
                    if self.scaler_mode == 'normalized':
                        img_array = img_array / 255.0
                    # raw: use as is (0-255)
                    # off: same as raw (handled later)
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
            return None
        image_cube = np.nan_to_num(image_cube, nan=0.0, posinf=1.0, neginf=0.0)
        labels = self._get_labels(idx)
        image_tensor = torch.from_numpy(image_cube).permute(2, 0, 1)  # (C, H, W)
        label_tensor = torch.from_numpy(labels)
        # StandardScaler transform (skip if off)
        if self.scaler_mode != "off":
            if self._mean_tensor is None or self._scale_tensor is None:
                if hasattr(self.scaler, "mean_") and hasattr(self.scaler, "scale_"):
                    self._mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
                    self._scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
                else:
                    if self.transform:
                        image_tensor = self.transform(image_tensor)
                    return image_tensor, label_tensor, idx
            mean = self._mean_tensor
            scale = self._scale_tensor
            eps = 1e-6
            scale = torch.clamp(scale, min=eps)
            image_tensor = (image_tensor - mean) / scale
        # Always apply augmentation
        if self.transform:
            image_tensor = self.transform(image_tensor)
        return image_tensor, label_tensor, idx

# collate_fn: None 샘플 필터링 및 빈 배치 방지
from torch.utils.data.dataloader import default_collate
import torch

def skip_invalid_collate(batch):
    batch = [b for b in batch if b is not None]
    if len(batch) == 0:
        # 빈 배치는 unpack 오류 방지용으로 empty tensor 반환
        return torch.empty(0), torch.empty(0), []
    return default_collate(batch)


def create_hsi_data_loaders(csv_path, column_config_path, batch_size=8, num_workers=4, 
                           val_split=0.1, test_split=0.1, random_state=42, 
                           train_transform=None, val_transform=None, test_transform=None, scaler_mode="normalized"):
    """
    HSI 데이터 로더를 생성합니다.
    scaler_mode: 'normalized' | 'raw' | 'off' (config["data"]["scaler_mode"]에서만 설정)
    """
    from torch.utils.data import Subset
    print("Creating full dataset and fitting scaler...")
    full_dataset = HSIDataset(csv_path, column_config_path, fit_scaler=True, scaler_mode=scaler_mode)
    scaler = full_dataset.scaler
    
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
    
    # 3. Subset으로 분할 (중복 생성 방지)
    train_dataset = Subset(full_dataset, train_indices)
    val_dataset = Subset(full_dataset, val_indices)
    test_dataset = Subset(full_dataset, test_indices)
    
    # 4. pos_weight 계산을 위한 train 라벨 통계 미리 계산
    print("Calculating pos_weight statistics...")
    pos_weight_info = _calculate_pos_weight_info(full_dataset, train_indices)
    
    # 5. Transform 적용을 위한 wrapper 클래스
    class TransformWrapper:
        def __init__(self, dataset, transform):
            self.dataset = dataset
            self.transform = transform
        
        def __getitem__(self, idx):
            item = self.dataset[idx]
            if item is None:
                return None
            images, labels, sample_idx = item
            if self.transform:
                images = self.transform(images)
            return images, labels, sample_idx
        
        def __len__(self):
            return len(self.dataset)
    
    # Transform 적용
    train_dataset = TransformWrapper(train_dataset, train_transform)
    val_dataset = TransformWrapper(val_dataset, val_transform)
    test_dataset = TransformWrapper(test_dataset, test_transform)
    
    # DataLoader worker 시드 고정 함수
    def seed_worker(worker_id):
        import torch
        import numpy as np
        import random
        worker_seed = random_state + worker_id
        np.random.seed(worker_seed)
        torch.manual_seed(worker_seed)
        random.seed(worker_seed)
    
    generator = torch.Generator()
    generator.manual_seed(random_state)

    # Celery 환경에서는 num_workers를 0으로 설정 (데몬 프로세스 충돌 방지)
    import multiprocessing
    import os
    current_process = multiprocessing.current_process()
    if current_process.daemon or 'celery' in os.environ.get('_', '').lower():
        print(f"Detected Celery/daemon environment. Setting num_workers=0 (was {num_workers})")
        num_workers = 0
    
    # DataLoader 생성 시 collate_fn 인자로 전달
    train_loader = DataLoader(
        train_dataset, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=True,
        worker_init_fn=seed_worker, generator=generator,
        collate_fn=skip_invalid_collate
    )
    
    val_loader = DataLoader(
        val_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True,
        worker_init_fn=seed_worker, generator=generator,
        collate_fn=skip_invalid_collate
    )
    
    test_loader = DataLoader(
        test_dataset, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=True,
        worker_init_fn=seed_worker, generator=generator,
        collate_fn=skip_invalid_collate
    )
    
    print(f"Data loaders created:")
    print(f"  Train: {len(train_dataset)} samples")
    print(f"  Val: {len(val_dataset)} samples")
    print(f"  Test: {len(test_dataset)} samples")
    
    return train_loader, val_loader, test_loader, scaler, pos_weight_info


def _calculate_pos_weight_info(dataset, train_indices):
    """train set의 라벨 통계를 계산하여 pos_weight 정보를 반환합니다."""
    label_start = dataset.column_config['column_order']['label_start_index']
    label_columns = dataset.column_config['label_columns']
    
    # train set의 라벨만 추출
    train_labels = []
    for idx in train_indices:
        row = dataset.data.iloc[idx]
        labels = []
        for i, label_col in enumerate(label_columns):
            col_idx = label_start + i
            if col_idx < len(row):
                label_value = row.iloc[col_idx]
                if pd.notna(label_value):
                    labels.append(float(label_value))
                else:
                    labels.append(0.0)
            else:
                labels.append(0.0)
        train_labels.append(labels)
    
    train_labels = np.array(train_labels, dtype=np.float32)
    
    # 분류 라벨 인덱스 찾기 (label_types['classification']에서 직접 가져오기)
    cls_names = dataset.column_config['label_types'].get('classification', [])
    cls_indices = []
    for i, name in enumerate(label_columns):
        if name in cls_names:
            cls_indices.append(i)
    
    if cls_indices:
        # pos_weight 계산
        cls_labels = train_labels[:, cls_indices]
        pos_counts = cls_labels.sum(axis=0)
        neg_counts = np.clip(cls_labels.shape[0] - pos_counts, a_min=1, a_max=None)
        pos_weight = (neg_counts / (pos_counts + 1e-6)).tolist()
        
        return {
            'cls_indices': cls_indices,
            'pos_weight': pos_weight,
            'pos_counts': pos_counts.tolist(),
            'neg_counts': neg_counts.tolist()
        }
    else:
        return {
            'cls_indices': [],
            'pos_weight': [],
            'pos_counts': [],
            'neg_counts': []
        }


def get_label_info(column_config_path):
    """라벨 정보를 반환합니다."""
    with open(column_config_path, 'r') as f:
        config = json.load(f)
    
    return {
        'label_columns': config['label_columns'],
        'label_types': config['label_types'],
        'num_classes': len(config['label_columns'])
    } 
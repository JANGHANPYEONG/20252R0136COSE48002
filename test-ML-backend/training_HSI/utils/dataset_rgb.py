"""
RGB 이미지 데이터셋 모듈

이 모듈은 RGB 이미지 분류/회귀 학습을 위한 데이터셋 클래스를 제공합니다.
세그멘테이션 마스크를 선택적으로 적용할 수 있으며, HSI 파이프라인과 호환됩니다.
"""

import os
import json
import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split, Subset
from PIL import Image
import warnings
from sklearn.model_selection import train_test_split
warnings.filterwarnings('ignore')


class RGBDataset(Dataset):
    """RGB 이미지 데이터셋 클래스"""
    
    def __init__(self, csv_path: str, column_config_path: str, 
                 transform=None, seg_config: dict = None, indices: list = None):
        """
        Args:
            csv_path: CSV 파일 경로
            column_config_path: 컬럼 설정 파일 경로
            transform: 이미지 변환
            seg_config: 세그멘테이션 설정 (None이면 세그멘테이션 비활성화)
            indices: 사용할 데이터 인덱스 리스트 (None이면 전체 사용)
        """
        self.csv_path = csv_path
        self.column_config_path = column_config_path
        self.transform = transform
        self.seg_config = seg_config or {}
        self.indices = indices
        
        # 설정 로드
        self.column_config = self._load_column_config()
        self.data = self._load_data()
        
        # 인덱스 필터링 적용
        if self.indices is not None:
            self.data = self.data.iloc[self.indices].reset_index(drop=True)
        
        # 세그멘테이션 설정 확인
        self.seg_enabled = self.seg_config.get('enabled', False)
        self.seg_mode = self.seg_config.get('mode', 'precomputed')
        self.seg_apply = self.seg_config.get('apply', 'mul')
        self.seg_threshold = self.seg_config.get('threshold', 0.5)
        
        if self.seg_enabled and self.seg_mode != 'precomputed':
            warnings.warn(
                f"Segmentation mode '{self.seg_mode}' is not yet implemented. "
                "Falling back to precomputed mode."
            )
            self.seg_mode = 'precomputed'
    
    def _load_column_config(self):
        """컬럼 설정을 로드합니다."""
        with open(self.column_config_path, 'r') as f:
            return json.load(f)
    
    def _load_data(self):
        """CSV 데이터를 로드합니다."""
        return pd.read_csv(self.csv_path)
    
    def _get_image_path(self, idx: int) -> str:
        """이미지 경로를 반환합니다."""
        rgb_start_idx = self.column_config['column_order']['rgb_image_path_start_index']
        image_path = self.data.iloc[idx, rgb_start_idx]
        
        # 상대경로를 절대경로로 변환
        if not os.path.isabs(image_path):
            base_dir = self.column_config['base_dirs']['rgb_image_dir']
            image_path = os.path.join(base_dir, image_path)
        
        return image_path
    
    def _get_mask_path(self, idx: int) -> str:
        """마스크 경로를 반환합니다."""
        if not self.seg_enabled or self.seg_mode != 'precomputed':
            return None
        
        mask_idx = self.column_config['column_order']['rgb_mask_path_index']
        mask_path = self.data.iloc[idx, mask_idx]
        # 빈값/NaN 가드
        if pd.isna(mask_path) or str(mask_path).strip() == "":
            return None
        
        # 상대경로를 절대경로로 변환
        if not os.path.isabs(mask_path):
            base_dir = self.column_config['base_dirs']['rgb_mask_dir']
            mask_path = os.path.join(base_dir, mask_path)
        
        return mask_path
    
    def _load_image(self, image_path: str) -> Image.Image:
        """이미지를 로드합니다."""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = Image.open(image_path).convert('RGB')
        return image
    
    def _load_mask(self, mask_path: str) -> np.ndarray:
        """마스크를 로드합니다."""
        if (not mask_path) or (not os.path.isfile(mask_path)):
            warnings.warn(f"Mask not found: {mask_path}")
            return None
        
        mask = Image.open(mask_path).convert('L')
        mask_array = np.array(mask, dtype=np.float32) / 255.0  # 0~1 범위로 정규화
        
        # 임계값 적용
        mask_array = (mask_array > self.seg_threshold).astype(np.float32)
        
        return mask_array
    
    def _apply_mask(self, image: torch.Tensor, mask: np.ndarray) -> torch.Tensor:
        """마스크를 이미지에 적용합니다."""
        if mask is None:
            return image
        
        # 마스크를 텐서로 변환하고 차원 맞추기
        mask_tensor = torch.from_numpy(mask).float()
        if mask_tensor.dim() == 2:
            mask_tensor = mask_tensor.unsqueeze(0)  # (H, W) -> (1, H, W)
        
        # 이미지와 마스크 차원 맞추기
        if image.size(0) == 3 and mask_tensor.size(0) == 1:
            mask_tensor = mask_tensor.expand(3, -1, -1)  # (1, H, W) -> (3, H, W)
        
        if self.seg_apply == "mul":
            # 마스크로 픽셀값 조정
            return image * mask_tensor
        elif self.seg_apply == "crop":
            # 마스크 bbox로 타이트 크롭 (구현 예정)
            warnings.warn("Crop mode not yet implemented. Using mul mode instead.")
            return image * mask_tensor
        elif self.seg_apply == "concat":
            # 4채널 결합 (구현 예정)
            warnings.warn("Concat mode not yet implemented. Using mul mode instead.")
            return image * mask_tensor
        else:
            warnings.warn(f"Unknown seg.apply mode: {self.seg_apply}. Using mul mode instead.")
            return image * mask_tensor
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int):
        """데이터셋에서 하나의 샘플을 가져옵니다."""
        try:
            image_path = self._get_image_path(idx)
            image = self._load_image(image_path)  # PIL
            mask = None
            if self.seg_enabled and self.seg_mode == 'precomputed':
                mp = self._get_mask_path(idx)
                if mp is not None:
                    mask = self._load_mask(mp)  # np.ndarray(H,W) in [0,1]

            # ✅ 변환 전에 마스크 적용 (mul 우선). 현재는 PIL→NumPy로 곱해 미리 반영.
            if mask is not None and self.seg_apply in ("mul", "crop", "concat"):
                np_img = np.array(image).astype(np.float32) / 255.0  # H,W,3
                np_img = np_img * mask[..., None]
                image = Image.fromarray(np.clip(np_img*255, 0, 255).astype(np.uint8)).convert('RGB')

            if self.transform:
                image = self.transform(image)

            # 라벨 추출(기존 로직 유지)
            label_start_idx = self.column_config['column_order']['label_start_index']
            label_columns = self.column_config['label_columns']
            labels = []
            for i, _ in enumerate(label_columns):
                col_idx = label_start_idx + i
                v = self.data.iloc[idx, col_idx] if col_idx < len(self.data.columns) else 0.0
                labels.append(0.0 if pd.isna(v) else float(v))
            label_tensor = torch.tensor(labels, dtype=torch.float32)

            return image, label_tensor, idx
        except Exception as e:
            print(f"Error loading sample {idx}: {e}")
            # 변환 파이프라인과 호환되는 PIL 더미 생성
            H, W = tuple(self.column_config.get('rgb_image_size', [224, 224]))
            from PIL import Image as _Image
            dummy_pil = _Image.new("RGB", (W, H), color=0)  # PIL은 (W,H)
            dummy_labels = torch.zeros(len(self.column_config['label_columns']), dtype=torch.float32)
            return dummy_pil, dummy_labels, idx


def skip_invalid_collate(batch):
    """유효하지 않은 샘플을 건너뛰는 collate 함수"""
    valid_batch = []
    for sample in batch:
        if sample is not None:
            valid_batch.append(sample)
    
    if not valid_batch:
        return None
    
    return torch.utils.data.dataloader.default_collate(valid_batch)


def create_rgb_data_loaders(csv_path: str, column_config_path: str, 
                           seg_config: dict = None, transform_config: dict = None,
                           batch_size: int = 32, num_workers: int = 4,
                           val_split: float = 0.1, test_split: float = 0.1,
                           seed: int = 42) -> tuple:
    """
    RGB 데이터 로더를 생성합니다.
    
    Args:
        csv_path: CSV 파일 경로
        column_config_path: 컬럼 설정 파일 경로
        seg_config: 세그멘테이션 설정
        transform_config: 변환 설정
        batch_size: 배치 크기
        num_workers: 워커 수
        val_split: 검증 데이터 비율
        test_split: 테스트 데이터 비율
        seed: 랜덤 시드
        
    Returns:
        tuple: (train_loader, val_loader, test_loader, label_info)
    """
    # 전체 데이터셋 생성
    full_dataset = RGBDataset(
        csv_path=csv_path,
        column_config_path=column_config_path,
        transform=None,  # 나중에 설정
        seg_config=seg_config
    )
    
    # 데이터 분할 - sklearn 사용
    total = len(full_dataset)
    val_size = int(total * val_split)
    test_size = int(total * test_split)
    all_idx = list(range(total))
    train_idx, temp_idx = train_test_split(all_idx, test_size=val_size+test_size, random_state=seed, shuffle=True)
    val_prop = val_split/(val_split+test_split) if (val_split+test_split)>0 else 0.5
    val_idx, test_idx = train_test_split(temp_idx, test_size=1-val_prop, random_state=seed, shuffle=True)

    # Subset + TransformWrapper
    class TW:
        def __init__(self, base, tf): self.base, self.tf = base, tf
        def __len__(self): return len(self.base)
        def __getitem__(self, i):
            x, y, idx = self.base[i]
            if x is None: return None
            return (self.tf(x) if self.tf else x), y, idx

    tr = Subset(full_dataset, train_idx)
    va = Subset(full_dataset, val_idx)
    te = Subset(full_dataset, test_idx)

    if transform_config:
        tr = TW(tr, transform_config.get('train'))
        va = TW(va, transform_config.get('val'))
        te = TW(te, transform_config.get('test'))

    g = torch.Generator(); g.manual_seed(seed)
    persistent = num_workers > 0
    train_loader = DataLoader(
        tr, batch_size=batch_size, shuffle=True, num_workers=num_workers,
        pin_memory=True, persistent_workers=persistent,
        generator=g, collate_fn=skip_invalid_collate
    )
    val_loader = DataLoader(
        va, batch_size=batch_size, shuffle=False, num_workers=num_workers,
        pin_memory=True, persistent_workers=persistent,
        generator=g, collate_fn=skip_invalid_collate
    )
    test_loader = DataLoader(
        te, batch_size=batch_size, shuffle=False, num_workers=num_workers,
        pin_memory=True, persistent_workers=persistent,
        generator=g, collate_fn=skip_invalid_collate
    )

    # ✅ pos_weight 계산 (로컬 구현)
    pos_weight_info = _calculate_pos_weight_info_rgb(full_dataset, train_idx)

    print(f"RGB 데이터 로더 생성 완료: total={total}, train={len(tr)}, val={len(va)}, test={len(te)}")
    return train_loader, val_loader, test_loader, pos_weight_info


def _calculate_pos_weight_info_rgb(dataset, train_indices):
    """RGB 데이터셋의 pos_weight 정보를 계산합니다 (HSI와 동일 인터페이스)."""
    label_columns = dataset.column_config['label_columns']
    label_start_idx = dataset.column_config['column_order']['label_start_index']
    cls_set = set(dataset.column_config['label_types']['classification'])

    cls_indices, pos_weights = [], []
    for i, col in enumerate(label_columns):
        if col not in cls_set:
            continue
        cls_indices.append(i)
        col_idx = label_start_idx + i
        total = pos = 0
        for idx in train_indices:
            if col_idx < len(dataset.data.columns):
                v = dataset.data.iloc[idx, col_idx]
                if not pd.isna(v):
                    total += 1
                    pos += float(v) > 0
        if pos == 0 or (total - pos) == 0:
            pos_weights.append(1.0)
        else:
            pos_weights.append((total - pos) / max(pos, 1))
    return {"cls_indices": cls_indices, "pos_weight": pos_weights}


def _calculate_label_info(dataset: RGBDataset) -> dict:
    """라벨 정보를 계산합니다."""
    label_columns = dataset.column_config['label_columns']
    label_start_idx = dataset.column_config['column_order']['label_start_index']
    
    # 각 라벨 컬럼의 통계 계산
    label_stats = {}
    for i, col in enumerate(label_columns):
        col_idx = label_start_idx + i
        values = []
        
        for idx in range(len(dataset.data)):
            if col_idx < len(dataset.data.columns):
                value = dataset.data.iloc[idx, col_idx]
                if not pd.isna(value):
                    values.append(float(value))
        
        if values:
            values = np.array(values)
            label_stats[col] = {
                'mean': float(np.mean(values)),
                'std': float(np.std(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'pos_weight': float(np.sum(values > 0) / len(values))
            }
        else:
            label_stats[col] = {
                'mean': 0.0,
                'std': 1.0,
                'min': 0.0,
                'max': 0.0,
                'pos_weight': 0.5
            }
    
    return label_stats

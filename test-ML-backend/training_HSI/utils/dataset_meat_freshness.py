"""
Meat Freshness 데이터셋 모듈

Kaggle Meat Freshness 데이터셋을 위한 PyTorch Dataset 클래스
ImageFolder 스타일의 구조 (train/, valid/)를 지원합니다.
"""

import os
from typing import Tuple, List
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import warnings
warnings.filterwarnings('ignore')


class MeatFreshnessDataset(Dataset):
    """
    Meat Freshness 이미지 분류 데이터셋
    
    디렉토리 구조:
        train/
            FRESH-*.jpg
            HALF-FRESH-*.jpg
            SPOILED-*.jpg
        valid/
            FRESH-*.jpg
            HALF-FRESH-*.jpg
            SPOILED-*.jpg
    
    Args:
        data_dir (str): 데이터 디렉토리 경로 (train/ 또는 valid/)
        transform: 이미지 변환
        class_names (List[str]): 클래스 이름 리스트 (기본값: ["FRESH", "HALF-FRESH", "SPOILED"])
    """
    
    def __init__(self, 
                 data_dir: str, 
                 transform=None, 
                 class_names: List[str] = None):
        self.data_dir = data_dir
        self.transform = transform
        self.class_names = class_names or ["FRESH", "HALF-FRESH", "SPOILED"]
        
        # 이미지 경로와 라벨 수집
        self.image_paths = []
        self.labels = []
        
        self._load_data()
        
        print(f"Loaded {len(self.image_paths)} images from {data_dir}")
        print(f"Class distribution: {self._get_class_distribution()}")
    
    def _load_data(self):
        """데이터 디렉토리에서 이미지 경로와 라벨을 로드합니다."""
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        
        # 디렉토리 내의 모든 .jpg 파일 스캔
        for filename in sorted(os.listdir(self.data_dir)):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue
            
            # 파일명에서 클래스 추출 (예: "FRESH-123-_JPG.rf.abc.jpg" → "FRESH")
            class_name = self._extract_class_from_filename(filename)
            
            if class_name in self.class_names:
                image_path = os.path.join(self.data_dir, filename)
                label = self.class_names.index(class_name)
                
                self.image_paths.append(image_path)
                self.labels.append(label)
    
    def _extract_class_from_filename(self, filename: str) -> str:
        """
        파일명에서 클래스 이름을 추출합니다.
        
        예시:
            "FRESH-842-_JPG.rf.1e4bd15f99a5d855b8ffb57aedc10af7.jpg" → "FRESH"
            "HALF-FRESH-736-_JPG.rf.1e82748aa05325eba33f95a1cb38732d.jpg" → "HALF-FRESH"
            "SPOILED-1010-_JPG.rf.1e1905bbb8f96c19b7c6d71cf8e3fdee.jpg" → "SPOILED"
        """
        for class_name in self.class_names:
            if filename.startswith(class_name):
                return class_name
        return None
    
    def _get_class_distribution(self) -> dict:
        """클래스별 샘플 수를 반환합니다."""
        from collections import Counter
        label_counts = Counter(self.labels)
        return {self.class_names[label]: count for label, count in sorted(label_counts.items())}
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, None]:
        """
        Returns:
            image (torch.Tensor): 변환된 이미지 텐서 [C, H, W]
            label (torch.Tensor): One-hot encoded 라벨 텐서 [num_classes] (HSITrainer 호환)
            kde_features (None): KDE 특성 없음 (HSITrainer 호환용)
        """
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        # 이미지 로드
        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            print(f"Error loading image {image_path}: {e}")
            # 더미 이미지 반환
            image = Image.new('RGB', (224, 224), color=(0, 0, 0))
        
        # 변환 적용
        if self.transform:
            image = self.transform(image)
        
        # One-hot encoding (HSITrainer는 multi-label을 기대)
        num_classes = len(self.class_names)
        label_tensor = torch.zeros(num_classes, dtype=torch.float32)
        label_tensor[label] = 1.0
        
        # HSITrainer는 (image, label, kde_features) 형태를 기대
        return image, label_tensor, None


def custom_collate_fn(batch):
    """
    Custom collate function to handle (image, label, None) format.
    HSITrainer expects (images, labels, kde_features) but we don't use KDE.
    """
    images = []
    labels = []
    
    for item in batch:
        if item is not None:
            image, label, _ = item  # kde_features는 None이므로 무시
            images.append(image)
            labels.append(label)
    
    if len(images) == 0:
        return None
    
    # Stack tensors
    images = torch.stack(images, dim=0)
    labels = torch.stack(labels, dim=0)
    
    # Return None for kde_features (HSITrainer will handle this)
    return images, labels, None


def create_meat_freshness_data_loaders(
    train_dir: str,
    valid_dir: str,
    class_names: List[str],
    image_size: Tuple[int, int] = (224, 224),
    batch_size: int = 32,
    num_workers: int = 4,
    use_augmentation: bool = True
) -> Tuple[DataLoader, DataLoader]:
    """
    Meat Freshness 데이터 로더를 생성합니다.
    
    Args:
        train_dir: 학습 데이터 디렉토리
        valid_dir: 검증 데이터 디렉토리
        class_names: 클래스 이름 리스트
        image_size: 이미지 크기 (height, width)
        batch_size: 배치 크기
        num_workers: DataLoader worker 수
        use_augmentation: 데이터 증강 사용 여부
    
    Returns:
        train_loader, valid_loader
    """
    # 변환 정의
    if use_augmentation:
        train_transform = transforms.Compose([
            transforms.Resize((image_size[0] + 32, image_size[1] + 32)),
            transforms.RandomCrop(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.RandomRotation(degrees=15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    else:
        train_transform = transforms.Compose([
            transforms.Resize(image_size),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    valid_transform = transforms.Compose([
        transforms.Resize(image_size),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # 데이터셋 생성
    train_dataset = MeatFreshnessDataset(
        data_dir=train_dir,
        transform=train_transform,
        class_names=class_names
    )
    
    valid_dataset = MeatFreshnessDataset(
        data_dir=valid_dir,
        transform=valid_transform,
        class_names=class_names
    )
    
    # 데이터 로더 생성
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True,
        collate_fn=custom_collate_fn
    )
    
    valid_loader = DataLoader(
        valid_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
        collate_fn=custom_collate_fn
    )
    
    print(f"\nDataLoader Summary:")
    print(f"  Train: {len(train_dataset)} samples, {len(train_loader)} batches")
    print(f"  Valid: {len(valid_dataset)} samples, {len(valid_loader)} batches")
    
    return train_loader, valid_loader


if __name__ == "__main__":
    # 테스트 코드
    train_dir = "/Users/potato/Desktop/Proj-Deeplant/dataset/meat_freshness/train"
    valid_dir = "/Users/potato/Desktop/Proj-Deeplant/dataset/meat_freshness/valid"
    class_names = ["FRESH", "HALF-FRESH", "SPOILED"]
    
    train_loader, valid_loader = create_meat_freshness_data_loaders(
        train_dir=train_dir,
        valid_dir=valid_dir,
        class_names=class_names,
        batch_size=8,
        num_workers=0
    )
    
    # 첫 번째 배치 확인
    images, labels = next(iter(train_loader))
    print(f"\nFirst batch:")
    print(f"  Images shape: {images.shape}")
    print(f"  Labels: {labels}")
    print(f"  Label distribution: {[class_names[l.item()] for l in labels]}")

import os
import glob
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

from .wavelength_detector import WavelengthDetector


class ViTRegressionDataset(Dataset):
    """ViT Regression용 HSI 데이터셋 클래스"""

    def __init__(self, root_dir, transform=None, scaler=None, fit_scaler=True,
                 scaler_mode="normalized", wavelengths=None, wavelength_strategy='auto',
                 use_rgb=True, target_size=(224, 224), missing_wavelength_strategy='skip'):
        """
        Args:
            root_dir: 데이터셋 루트 디렉토리 (C:/sanhak/manage-dataset/result)
            transform: 이미지 변환
            scaler: StandardScaler 객체
            fit_scaler: 스케일러를 fit할지 여부
            scaler_mode: 'normalized', 'raw', 'off'
            wavelengths: 사용할 파장 리스트 (None이면 자동 검출)
            wavelength_strategy: 'auto', 'max_coverage', 'common_only', 'all_available'
            use_rgb: RGB 이미지 사용 여부
            target_size: 출력 이미지 크기
            missing_wavelength_strategy: 'skip', 'zero_fill', 'interpolate', 'nearest'
        """
        self.root_dir = root_dir
        self.transform = transform
        self.scaler_mode = scaler_mode
        self.wavelength_strategy = wavelength_strategy
        self.use_rgb = use_rgb
        self.target_size = target_size
        self.missing_wavelength_strategy = missing_wavelength_strategy

        # 동적 파장 검출
        print("Detecting available wavelengths...")
        self.wavelength_detector = WavelengthDetector(root_dir)

        # 파장 결정
        if wavelengths is None:
            if wavelength_strategy == 'auto':
                self.wavelengths = self.wavelength_detector.get_optimal_wavelength_set('max_coverage')
            else:
                self.wavelengths = self.wavelength_detector.get_optimal_wavelength_set(wavelength_strategy)
            print(f"Auto-selected wavelengths: {self.wavelengths}")
        else:
            self.wavelengths = wavelengths
            print(f"Using specified wavelengths: {self.wavelengths}")

        # 데이터 로드
        self.samples = self._load_samples()
        print(f"Total samples loaded: {len(self.samples)}")

        # 채널 수 계산
        self.n_channels = len(self.wavelengths)
        if use_rgb:
            self.n_channels += 3  # RGB 추가

        print(f"Total channels: {self.n_channels} (wavelengths: {len(self.wavelengths)}, RGB: {3 if use_rgb else 0})")

        # 스케일러 설정
        if self.scaler_mode != "off":
            if scaler is None:
                self.scaler = StandardScaler()
            else:
                self.scaler = scaler
            if fit_scaler and len(self.samples) > 0:
                self._fit_scaler()

    def _load_samples(self):
        """모든 샘플을 로드"""
        samples = []

        # 모든 Excel 파일 찾기
        excel_files = glob.glob(os.path.join(self.root_dir, '*', '*.xlsx'))

        for excel_path in excel_files:
            try:
                # Excel 파일 읽기
                df = pd.read_excel(excel_path)

                # Total 컬럼이 있는지 확인
                if 'Total' not in df.columns:
                    continue

                # 각 행에 대해 처리
                for _, row in df.iterrows():
                    # 폴더명과 샘플 번호 추출
                    folder_name = os.path.basename(os.path.dirname(excel_path))
                    sample_num = row.iloc[1] if len(row) > 1 else 's1'  # 샘플번호 컬럼

                    # 파일명에 사용할 기본 폴더명 (day7 제거)
                    base_folder_name = folder_name.replace('_day7', '')

                    # 이미지 경로 구성
                    base_image_dir = os.path.join(os.path.dirname(excel_path), folder_name, sample_num)

                    # 이미지 파일 확인 (유연한 처리)
                    image_paths = {}
                    missing_wavelengths = []

                    # 파장별 이미지 경로 확인
                    for wl in self.wavelengths:
                        # 완전히 표준화된 파일명 패턴
                        if '_day7' in folder_name:
                            # Day7 폴더: _day7 접미사 사용
                            pattern = f"{base_folder_name}_{sample_num}_{wl}_day7.png"
                        else:
                            # Non-day7 폴더: 기본 패턴 사용
                            pattern = f"{base_folder_name}_{sample_num}_{wl}.png"

                        possible_patterns = [pattern]

                        found = False
                        for pattern in possible_patterns:
                            img_path = os.path.join(base_image_dir, pattern)
                            if os.path.exists(img_path):
                                image_paths[wl] = img_path
                                found = True
                                break

                        if not found:
                            missing_wavelengths.append(wl)

                    # RGB 이미지 경로 확인
                    if self.use_rgb:
                        if '_day7' in folder_name:
                            # Day7 폴더: _day7 접미사 사용
                            rgb_pattern = f"{base_folder_name}_{sample_num}_rgb_day7.png"
                        else:
                            # Non-day7 폴더: 기본 패턴 사용
                            rgb_pattern = f"{base_folder_name}_{sample_num}_rgb.png"

                        rgb_path = os.path.join(base_image_dir, rgb_pattern)
                        if os.path.exists(rgb_path):
                            image_paths['rgb'] = rgb_path

                    # 샘플 추가 결정 (missing_wavelength_strategy에 따라)
                    should_include = False

                    if self.missing_wavelength_strategy == 'skip':
                        # 모든 파장이 있어야 포함 (RGB 선택적)
                        should_include = (len(missing_wavelengths) == 0)
                    elif self.missing_wavelength_strategy == 'use_available':
                        # 최소 1개 파장이라도 있으면 포함 (있는 것만 사용)
                        wavelength_count = len([wl for wl in self.wavelengths if wl in image_paths])
                        should_include = wavelength_count > 0  # RGB는 선택적
                    else:
                        # 기존 방식: 최소 1개 파장이라도 있으면 포함 (RGB 선택적)
                        should_include = len([wl for wl in self.wavelengths if wl in image_paths]) > 0

                    if should_include:
                        sample = {
                            'folder': folder_name,
                            'sample': sample_num,
                            'images': image_paths,
                            'missing_wavelengths': missing_wavelengths,
                            'label': int(row['Total']),  # Total 점수를 라벨로 사용
                            'marbling': int(row['Marbling']) if 'Marbling' in row else 0,
                            'meat_color': int(row['Meat Color']) if 'Meat Color' in row else 0,
                            'texture': int(row['Texture']) if 'Texture' in row else 0,
                            'moisture': int(row['Surface Moisture']) if 'Surface Moisture' in row else 0
                        }
                        samples.append(sample)

            except Exception as e:
                print(f"Error loading {excel_path}: {e}")
                continue

        return samples

    def _fit_scaler(self, sample_ratio=0.1, max_samples=50):
        """스케일러 학습"""
        if self.scaler_mode == "off":
            return

        print("Fitting StandardScaler...")

        # 샘플링
        num_samples = min(max_samples, int(len(self.samples) * sample_ratio))
        sample_indices = np.random.choice(len(self.samples), num_samples, replace=False)

        all_pixels = []
        for idx in sample_indices:
            try:
                image_cube = self._load_image_cube(idx)
                if image_cube is not None:
                    # 픽셀 샘플링
                    h, w, c = image_cube.shape
                    pixels = image_cube.reshape(-1, c)
                    # 랜덤하게 픽셀 선택
                    n_pixels = min(1000, pixels.shape[0])
                    pixel_indices = np.random.choice(pixels.shape[0], n_pixels, replace=False)
                    all_pixels.append(pixels[pixel_indices])
            except:
                continue

        if all_pixels:
            all_pixels = np.concatenate(all_pixels, axis=0)
            self.scaler.fit(all_pixels)
            print(f"Scaler fitted with {len(all_pixels)} pixels from {num_samples} samples")

            # 텐서 변환
            self._mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
            self._scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
        else:
            self._mean_tensor = None
            self._scale_tensor = None

    def _load_image_cube(self, idx):
        """이미지 큐브 로드 (마스킹 기반 처리)"""
        sample = self.samples[idx]
        image_cube = []
        wavelength_mask = []  # 어떤 파장이 실제로 존재하는지 마스크

        try:
            # 파장별 이미지 로드 (모든 파장에 대해 고정된 채널 수 유지)
            for wl in self.wavelengths:
                if wl in sample['images']:
                    # 파장 이미지가 존재하는 경우
                    img_path = sample['images'][wl]
                    img = Image.open(img_path).convert('L')
                    img = img.resize(self.target_size, Image.BILINEAR)
                    img_array = np.array(img, dtype=np.float32)

                    # 정규화
                    if self.scaler_mode == 'normalized':
                        img_array = img_array / 255.0

                    image_cube.append(img_array)
                    wavelength_mask.append(1.0)  # 실제 데이터 존재
                else:
                    # 누락된 파장은 제로로 채우고 마스크에서 표시
                    if self.missing_wavelength_strategy == 'use_available':
                        zero_channel = np.zeros(self.target_size, dtype=np.float32)
                        image_cube.append(zero_channel)
                        wavelength_mask.append(0.0)  # 누락된 데이터
                    else:
                        # 기존 방식 (보간 등)
                        img_array = self._handle_missing_wavelength(sample, wl, idx)
                        image_cube.append(img_array)
                        wavelength_mask.append(1.0)  # 처리된 데이터

            # RGB 이미지 로드
            if self.use_rgb:
                if 'rgb' in sample['images']:
                    rgb_path = sample['images']['rgb']
                    rgb_img = Image.open(rgb_path).convert('RGB')
                    rgb_img = rgb_img.resize(self.target_size, Image.BILINEAR)
                    rgb_array = np.array(rgb_img, dtype=np.float32)

                    # 정규화
                    if self.scaler_mode == 'normalized':
                        rgb_array = rgb_array / 255.0

                    # RGB 3채널 추가
                    for i in range(3):
                        image_cube.append(rgb_array[:, :, i])
                        wavelength_mask.append(1.0)  # RGB는 항상 존재
                else:
                    # RGB 이미지가 누락된 경우
                    for i in range(3):
                        zero_channel = np.zeros(self.target_size, dtype=np.float32)
                        image_cube.append(zero_channel)
                        wavelength_mask.append(0.0)  # RGB 누락

            # 스택
            image_cube = np.stack(image_cube, axis=-1)
            wavelength_mask = np.array(wavelength_mask, dtype=np.float32)

            return image_cube, wavelength_mask

        except Exception as e:
            print(f"Error loading images for sample {idx}: {e}")
            return None, None

    def _handle_missing_wavelength(self, sample, missing_wl, idx):
        """누락된 파장 처리"""
        if self.missing_wavelength_strategy == 'zero_fill':
            # 제로 패딩
            return np.zeros(self.target_size, dtype=np.float32)

        elif self.missing_wavelength_strategy == 'nearest':
            # 가장 가까운 파장으로 복사
            available_wavelengths = [wl for wl in self.wavelengths if wl in sample['images']]
            if available_wavelengths:
                # 파장 숫자로 정렬하여 가장 가까운 것 찾기
                missing_nm = int(missing_wl[:-2])
                closest_wl = min(available_wavelengths,
                               key=lambda wl: abs(int(wl[:-2]) - missing_nm))

                img_path = sample['images'][closest_wl]
                img = Image.open(img_path).convert('L')
                img = img.resize(self.target_size, Image.BILINEAR)
                img_array = np.array(img, dtype=np.float32)

                if self.scaler_mode == 'normalized':
                    img_array = img_array / 255.0

                return img_array
            else:
                return np.zeros(self.target_size, dtype=np.float32)

        elif self.missing_wavelength_strategy == 'interpolate':
            # 인접 파장들의 평균으로 보간
            missing_nm = int(missing_wl[:-2])
            available_wavelengths = [(wl, int(wl[:-2])) for wl in self.wavelengths if wl in sample['images']]

            if len(available_wavelengths) >= 2:
                # 누락 파장 앞뒤의 파장들 찾기
                lower_wls = [(wl, nm) for wl, nm in available_wavelengths if nm < missing_nm]
                upper_wls = [(wl, nm) for wl, nm in available_wavelengths if nm > missing_nm]

                if lower_wls and upper_wls:
                    # 가장 가까운 앞뒤 파장들
                    lower_wl = max(lower_wls, key=lambda x: x[1])[0]
                    upper_wl = min(upper_wls, key=lambda x: x[1])[0]

                    # 두 이미지 로드하여 평균
                    img1_path = sample['images'][lower_wl]
                    img2_path = sample['images'][upper_wl]

                    img1 = Image.open(img1_path).convert('L')
                    img1 = img1.resize(self.target_size, Image.BILINEAR)
                    img1_array = np.array(img1, dtype=np.float32)

                    img2 = Image.open(img2_path).convert('L')
                    img2 = img2.resize(self.target_size, Image.BILINEAR)
                    img2_array = np.array(img2, dtype=np.float32)

                    # 정규화
                    if self.scaler_mode == 'normalized':
                        img1_array = img1_array / 255.0
                        img2_array = img2_array / 255.0

                    # 평균
                    return (img1_array + img2_array) / 2

            # 보간이 불가능하면 nearest로 fallback
            available_wavelengths = [wl for wl in self.wavelengths if wl in sample['images']]
            if available_wavelengths:
                # 가장 가까운 파장으로 복사
                missing_nm = int(missing_wl[:-2])
                closest_wl = min(available_wavelengths,
                               key=lambda wl: abs(int(wl[:-2]) - missing_nm))

                img_path = sample['images'][closest_wl]
                img = Image.open(img_path).convert('L')
                img = img.resize(self.target_size, Image.BILINEAR)
                img_array = np.array(img, dtype=np.float32)

                if self.scaler_mode == 'normalized':
                    img_array = img_array / 255.0

                return img_array
            else:
                return np.zeros(self.target_size, dtype=np.float32)

        else:
            # 기본값: 제로 패딩
            return np.zeros(self.target_size, dtype=np.float32)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]

        # 이미지 큐브 로드 (마스크 포함)
        result = self._load_image_cube(idx)
        if result is None or result[0] is None:
            return None  # HSI dataset과 동일하게 None 반환

        image_cube, wavelength_mask = result

        # NaN 처리
        image_cube = np.nan_to_num(image_cube, nan=0.0, posinf=1.0, neginf=0.0)

        # 라벨 생성 - 멀티태스크용 (분류 + 회귀)
        # Total을 분류로 (3-8 -> 0-5), 나머지를 회귀로
        labels = []

        # 분류 라벨: Total을 연속된 클래스 인덱스로 매핑
        total_original = sample['label']  # 3,5,6,7,8
        class_mapping = {3: 0, 5: 1, 6: 2, 7: 3, 8: 4}  # 실제 등장하는 클래스들을 0-4로 매핑
        total_class = class_mapping.get(total_original, 0)  # 매핑되지 않은 경우 0으로 기본값
        labels.append(float(total_class))

        # 회귀 라벨: Marbling, Meat Color, Texture, Moisture
        labels.append(float(sample['marbling']))
        labels.append(float(sample['meat_color']))
        labels.append(float(sample['texture']))
        labels.append(float(sample['moisture']))

        labels = np.array(labels, dtype=np.float32)

        # 텐서 변환
        image_tensor = torch.from_numpy(image_cube).permute(2, 0, 1)  # (C, H, W)
        label_tensor = torch.from_numpy(labels)
        mask_tensor = torch.from_numpy(wavelength_mask)  # (C,)

        # StandardScaler transform (skip if off)
        if self.scaler_mode != "off":
            if hasattr(self, '_mean_tensor') and self._mean_tensor is not None:
                mean = self._mean_tensor
                scale = self._scale_tensor
                eps = 1e-6
                scale = torch.clamp(scale, min=eps)
                image_tensor = (image_tensor - mean) / scale

        # Always apply augmentation
        if self.transform:
            image_tensor = self.transform(image_tensor)

        return image_tensor, label_tensor, mask_tensor, idx


# collate_fn: None 샘플 필터링
from torch.utils.data.dataloader import default_collate

def skip_invalid_collate(batch):
    batch = [b for b in batch if b is not None]
    if len(batch) == 0:
        return torch.empty(0), torch.empty(0), torch.empty(0), []
    return default_collate(batch)


def create_vit_regression_data_loaders(root_dir, batch_size=8, num_workers=0,
                                       val_split=0.1, test_split=0.1,
                                       train_transform=None, val_transform=None, test_transform=None,
                                       scaler_mode="normalized", wavelengths=None, wavelength_strategy='auto',
                                       use_rgb=True, target_size=(224, 224), missing_wavelength_strategy='interpolate',
                                       random_state=42):
    """ViT Regression용 데이터 로더 생성"""

    print("Creating full dataset and fitting scaler...")

    # 전체 데이터셋 생성 (스케일러 학습용)
    full_dataset = ViTRegressionDataset(
        root_dir=root_dir,
        transform=None,
        scaler=None,
        fit_scaler=True,
        scaler_mode=scaler_mode,
        wavelengths=wavelengths,
        wavelength_strategy=wavelength_strategy,
        use_rgb=use_rgb,
        target_size=target_size,
        missing_wavelength_strategy=missing_wavelength_strategy
    )

    scaler = full_dataset.scaler if scaler_mode != "off" else None

    # 인덱스 분할
    total_size = len(full_dataset)
    val_size = int(total_size * val_split)
    test_size = int(total_size * test_split)
    train_size = total_size - val_size - test_size

    # sklearn의 train_test_split 사용하여 인덱스 분할
    all_indices = list(range(total_size))
    train_indices, temp_indices = train_test_split(
        all_indices, test_size=val_size + test_size,
        random_state=random_state, shuffle=True
    )

    val_prop = val_split / (val_split + test_split)
    val_indices, test_indices = train_test_split(
        temp_indices, test_size=1 - val_prop, random_state=random_state, shuffle=True
    )

    # Subset으로 분할
    train_dataset = Subset(full_dataset, train_indices)
    val_dataset = Subset(full_dataset, val_indices)
    test_dataset = Subset(full_dataset, test_indices)

    # pos_weight 계산
    print("Calculating pos_weight statistics...")
    pos_weight_info = _calculate_pos_weight_info(full_dataset, train_indices)

    # Transform 적용을 위한 wrapper 클래스
    class TransformWrapper:
        def __init__(self, dataset, transform):
            self.dataset = dataset
            self.transform = transform

        def __getitem__(self, idx):
            item = self.dataset[idx]
            if item is None:
                return None
            images, labels, mask, sample_idx = item
            if self.transform:
                images = self.transform(images)
            return images, labels, mask, sample_idx

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

    # 데이터 로더 생성 (HSI와 동일한 설정)
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
    """train set의 라벨 통계를 계산하여 pos_weight 정보를 반환"""

    # Total 점수를 분류로 사용 (첫 번째 라벨)
    train_labels = []
    class_mapping = {}  # 실제 클래스 -> 연속된 인덱스 매핑
    mapped_labels = []

    # 클래스 매핑 정의 (dataset과 동일하게)
    class_mapping = {3: 0, 5: 1, 6: 2, 7: 3, 8: 4}

    for idx in train_indices:
        if idx < len(dataset.samples):
            sample = dataset.samples[idx]
            # Total score를 연속된 인덱스로 매핑
            total_original = sample['label']  # 3,5,6,7,8
            total_class = class_mapping.get(total_original, 0)
            train_labels.append(total_class)

    # 매핑된 라벨을 그대로 사용
    mapped_labels = train_labels
    unique_classes = sorted(list(set(mapped_labels)))

    # 매핑된 라벨로 카운트 계산
    mapped_unique_labels, mapped_counts = np.unique(mapped_labels, return_counts=True)

    # pos_weight 계산 (실제 등장한 클래스 수에 맞춰)
    total_samples = len(mapped_labels)
    pos_weights = []
    num_classes = len(unique_classes)

    for cls in range(num_classes):
        if cls in mapped_unique_labels:
            cls_count = mapped_counts[np.where(mapped_unique_labels == cls)[0][0]]
            neg_count = total_samples - cls_count
            pos_weight = neg_count / max(cls_count, 1)
        else:
            pos_weight = 1.0
        pos_weights.append(pos_weight)

    pos_weight_info = {
        'cls_indices': [0],  # Total score가 분류 태스크 (첫 번째 인덱스)
        'reg_indices': [1, 2, 3, 4],  # 나머지는 회귀 태스크 (Marbling, Meat Color, Texture, Surface Moisture)
        'pos_weight': torch.tensor(pos_weights, dtype=torch.float32),
        'class_counts': dict(zip(mapped_unique_labels.tolist(), mapped_counts.tolist())),
        'total_samples': total_samples,
        'class_mapping': class_mapping,  # 원본 클래스 -> 매핑된 인덱스
        'original_classes': unique_classes  # 실제 등장한 원본 클래스들
    }

    return pos_weight_info
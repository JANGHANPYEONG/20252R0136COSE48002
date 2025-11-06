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
    
    def __init__(self, csv_path, column_config_path, 
                 fit_scaler=False, scaler_mode="normalized", 
                 use_kde=False, train_indices=None):
        """
        HSI 데이터셋 초기화
        
        Args:
            csv_path: CSV 파일 경로
            column_config_path: 컬럼 설정 파일 경로
            fit_scaler: 스케일러를 fit할지 여부
            scaler_mode: 스케일링 모드 ("normalized", "raw", "off")
            use_kde: KDE 특성을 사용할지 여부
            train_indices: KDE 계산에 사용할 train 인덱스 (feature leakage 방지)
        """
        self.csv_path = csv_path
        self.column_config_path = column_config_path
        self.scaler_mode = scaler_mode
        self.use_kde = use_kde
        self.train_indices = train_indices
        self.transform = None  # Transform은 TransformWrapper에서 처리
        assert self.scaler_mode in {"normalized", "raw", "off"}, f"Invalid scaler_mode: {self.scaler_mode}"
        
        # 설정 로드
        self.column_config = self._load_column_config()
        self.data = self._load_data()
        
        # 스케일러 설정
        if self.scaler_mode != "off":
            self.scaler = StandardScaler()
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
        
        # KDE 특성 준비 (train_indices가 제공된 경우에만 해당 인덱스로 계산)
        if self.use_kde:
            self._prepare_kde_features()
    
    def _load_column_config(self):
        """컬럼 설정을 로드합니다."""
        with open(self.column_config_path, 'r') as f:
            return json.load(f)
    
    def _load_data(self):
        """CSV 데이터를 로드합니다."""
        return pd.read_csv(self.csv_path)
    
    def _prepare_kde_features(self):
        """KDE 방식: 학습 데이터의 라벨 분포를 KDE로 모델링하여 분포 통계 feature 생성 (Feature Leakage 방지)"""
        from scipy.stats import gaussian_kde
        import warnings
        warnings.filterwarnings('ignore')
        
        print("Computing KDE features from train label distributions...")
        label_start = self.column_config['column_order']['label_start_index']
        label_columns = self.column_config['label_columns']
        
        # Feature leakage 방지: train 인덱스만 사용하여 KDE 분포 계산
        if self.train_indices is not None:
            train_data = self.data.iloc[self.train_indices]
            print(f"Using train data only for KDE computation: {len(train_data)} samples")
        else:
            train_data = self.data
            print("Warning: Using all data for KDE computation (potential feature leakage)")
        
        # 1. Train 데이터에서 각 라벨의 분포 계산
        label_distributions = {}
        for i, label_col in enumerate(label_columns):
            col_idx = label_start + i
            if col_idx < len(train_data.columns):
                # 안전한 숫자형 변환
                raw_values = train_data.iloc[:, col_idx].dropna()
                try:
                    values = pd.to_numeric(raw_values, errors='coerce').dropna().values
                    values = values.astype(np.float32)
                except:
                    print(f"Warning: Could not convert {label_col} to numeric, using default values")
                    values = np.array([0.0], dtype=np.float32)
                
                if len(values) > 1:
                    label_distributions[i] = {
                        'values': values,
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'q25': float(np.percentile(values, 25)),
                        'q50': float(np.percentile(values, 50)),
                        'q75': float(np.percentile(values, 75)),
                        'kde': gaussian_kde(values) if len(values) > 3 else None
                    }
                else:
                    # 데이터가 부족한 경우 기본값
                    label_distributions[i] = {
                        'values': values,
                        'mean': 0.0, 'std': 1.0, 'min': 0.0, 'max': 1.0,
                        'q25': 0.0, 'q50': 0.5, 'q75': 1.0, 'kde': None
                    }
        
        # 2. 고정된 분포 통계 feature vector 생성 (모든 샘플에 동일하게 적용)
        kde_stats = []
        
        # 각 라벨별 분포 통계 (라벨당 8개 특성)
        for i in range(len(label_columns)):
            if i in label_distributions:
                dist = label_distributions[i]
                kde_stats.extend([
                    dist['mean'],    # 평균
                    dist['std'],     # 표준편차  
                    dist['min'],     # 최소값
                    dist['max'],     # 최대값
                    dist['q25'],     # 1사분위수
                    dist['q50'],     # 중간값
                    dist['q75'],     # 3사분위수
                    dist['max'] - dist['min']  # 범위
                ])
            else:
                # 기본값 (8개)
                kde_stats.extend([0.0, 1.0, 0.0, 1.0, 0.0, 0.5, 1.0, 1.0])
        
        # 3. 전체 분포의 메타 통계 (6개 추가 특성)
        all_values = []
        for i in label_distributions.keys():
            all_values.extend(label_distributions[i]['values'].tolist())
        
        if all_values:
            all_values = np.array(all_values, dtype=np.float32)
            kde_stats.extend([
                float(np.mean(all_values)),           # 전체 평균
                float(np.std(all_values)),            # 전체 표준편차
                float(np.min(all_values)),            # 전체 최소값
                float(np.max(all_values)),            # 전체 최대값
                len(np.unique(all_values)) / len(all_values),  # 값 다양성
                float(np.percentile(all_values, 95))  # 95th percentile
            ])
        else:
            kde_stats.extend([0.0, 1.0, 0.0, 1.0, 1.0, 1.0])
        
        # 고정된 feature vector를 numpy array로 변환
        fixed_kde_features = np.array(kde_stats, dtype=np.float32)
        print(f"Safe KDE feature vector dimension: {len(fixed_kde_features)}")
        print(f"  - Per-label statistics: {len(label_columns)} labels × 8 features = {len(label_columns) * 8}")
        print(f"  - Global meta features: 6")
        print(f"  - Total: {len(fixed_kde_features)} features")
        
        # 4. 모든 샘플에 동일한 고정 feature vector 할당 (Feature Leakage 방지)
        self.kde_features = []
        for idx in range(len(self.data)):
            self.kde_features.append(fixed_kde_features.copy())
        
        print(f"\n Safe KDE Distribution Features Created:")
        print(f"  - Fixed feature vector applied to all {len(self.kde_features)} samples")
        print(f"  - Based on train label distributions only (no feature leakage)")
        print(f"  - No sample-specific label information used")
        print(f"  - Safe for production deployment")
        
        # 분포 정보 출력
        print(f"\nTrain Label Distribution Summary:")
        for i, label_col in enumerate(label_columns):
            if i in label_distributions:
                dist = label_distributions[i]
                print(f"  {label_col}: mean={dist['mean']:.3f}, std={dist['std']:.3f}, range=[{dist['min']:.3f}, {dist['max']:.3f}]")
        
        # 특성 통계 확인 (모든 샘플이 동일한 값을 가져야 함)
        kde_array = np.array(self.kde_features)
        variances = np.var(kde_array, axis=0)
        if np.all(variances < 1e-10):
            print(" All samples have identical KDE features (safe from feature leakage)")
        else:
            print("  Warning: KDE features should be identical across samples")
        
        # 저장해둔 분포 정보 (나중에 해석용으로 사용 가능)
        self._label_distributions = label_distributions
    def _calculate_skewness(self, values):
        """왜도(비대칭성) 계산"""
        if len(values) < 3:
            return 0.0
        mean = values.mean()
        std = values.std()
        if std == 0:
            return 0.0
        return ((values - mean) ** 3).mean() / (std ** 3)
    
    def _calculate_kurtosis(self, values):
        """첨도(뾰족함) 계산"""
        if len(values) < 4:
            return 0.0
        mean = values.mean()
        std = values.std()
        if std == 0:
            return 0.0
        return ((values - mean) ** 4).mean() / (std ** 4) - 3

    def _compute_train_image_statistics(self):
        """Train 데이터의 이미지 통계 계산 (Feature Leakage 방지)"""
        print("Computing train image statistics for KDE features...")
        train_brightness = []
        train_contrast = []
        train_spatial_var = []
        train_spectral_mean = []
        
        # Train 인덱스만 사용
        indices_to_use = self.train_indices if self.train_indices is not None else range(min(50, len(self.data)))
        
        for idx in indices_to_use:
            image_cube = self._load_image_cube(idx)
            if image_cube is not None:
                # 이미지 통계 추출
                brightness = np.mean(image_cube)
                contrast = np.std(image_cube)
                spatial_var = np.var(np.mean(image_cube, axis=2))  # 공간적 변동성
                spectral_mean = np.mean(np.mean(image_cube, axis=(0,1)))  # 스펙트럴 평균
                
                train_brightness.append(brightness)
                train_contrast.append(contrast)
                train_spatial_var.append(spatial_var)
                train_spectral_mean.append(spectral_mean)
        
        return {
            'brightness_mean': np.mean(train_brightness) if train_brightness else 0.5,
            'brightness_std': np.std(train_brightness) if train_brightness else 0.1,
            'contrast_mean': np.mean(train_contrast) if train_contrast else 0.2,
            'contrast_std': np.std(train_contrast) if train_contrast else 0.1,
            'spatial_var_mean': np.mean(train_spatial_var) if train_spatial_var else 0.1,
            'spatial_var_std': np.std(train_spatial_var) if train_spatial_var else 0.05,
            'spectral_mean_mean': np.mean(train_spectral_mean) if train_spectral_mean else 0.5,
            'spectral_mean_std': np.std(train_spectral_mean) if train_spectral_mean else 0.1
        }
    
    def _extract_sample_image_features(self, image_cube, train_image_stats, train_distribution_stats):
        """샘플별 이미지 기반 KDE 특성 추출 (라벨과 무관)"""
        # 1. 이미지 통계 특성 (8개)
        sample_brightness = np.mean(image_cube)
        sample_contrast = np.std(image_cube)
        sample_spatial_var = np.var(np.mean(image_cube, axis=2))
        sample_spectral_mean = np.mean(np.mean(image_cube, axis=(0,1)))
        
        # Train 분포 대비 상대적 위치 (Z-score normalization)
        relative_brightness = (sample_brightness - train_image_stats['brightness_mean']) / (train_image_stats['brightness_std'] + 1e-8)
        relative_contrast = (sample_contrast - train_image_stats['contrast_mean']) / (train_image_stats['contrast_std'] + 1e-8)
        relative_spatial_var = (sample_spatial_var - train_image_stats['spatial_var_mean']) / (train_image_stats['spatial_var_std'] + 1e-8)
        relative_spectral_mean = (sample_spectral_mean - train_image_stats['spectral_mean_mean']) / (train_image_stats['spectral_mean_std'] + 1e-8)
        
        # 2. 텍스처 및 복잡도 특성 (4개)
        texture_complexity = self._calculate_texture_complexity(image_cube)
        edge_density = self._calculate_edge_density(image_cube)
        spectral_diversity = self._calculate_spectral_diversity(image_cube)
        spatial_homogeneity = self._calculate_spatial_homogeneity(image_cube)
        
        # 3. 분포 상대적 특성 (4개) - 이미지 기반이므로 샘플별로 다름
        brightness_percentile = self._calculate_percentile_in_distribution(sample_brightness, 'brightness', train_distribution_stats)
        contrast_percentile = self._calculate_percentile_in_distribution(sample_contrast, 'contrast', train_distribution_stats)
        complexity_score = texture_complexity + edge_density
        diversity_score = spectral_diversity + spatial_homogeneity
        
        kde_features = [
            # 상대적 이미지 통계 (4개)
            relative_brightness, relative_contrast, relative_spatial_var, relative_spectral_mean,
            # 텍스처 및 복잡도 (4개)
            texture_complexity, edge_density, spectral_diversity, spatial_homogeneity,
            # 분포 상대적 특성 (4개)
            brightness_percentile, contrast_percentile, complexity_score, diversity_score,
            # 추가 메타 특성 (4개)
            np.clip(relative_brightness, -3, 3),  # clipped relative brightness
            np.clip(relative_contrast, -3, 3),    # clipped relative contrast
            min(1.0, max(0.0, complexity_score / 10.0)),  # normalized complexity
            min(1.0, max(0.0, diversity_score / 10.0))    # normalized diversity
        ]
        
        return kde_features
    
    def _calculate_texture_complexity(self, image_cube):
        """텍스처 복잡도 계산"""
        if image_cube.shape[2] > 0:
            gray = np.mean(image_cube, axis=2)
            # Sobel gradient magnitude
            from scipy import ndimage
            grad_x = ndimage.sobel(gray, axis=0)
            grad_y = ndimage.sobel(gray, axis=1)
            return float(np.mean(np.sqrt(grad_x**2 + grad_y**2)))
        return 0.0
    
    def _calculate_edge_density(self, image_cube):
        """엣지 밀도 계산"""
        if image_cube.shape[2] > 0:
            gray = np.mean(image_cube, axis=2)
            # Laplacian edge detection
            from scipy import ndimage
            edges = ndimage.laplace(gray)
            return float(np.mean(np.abs(edges)))
        return 0.0
    
    def _calculate_spectral_diversity(self, image_cube):
        """스펙트럴 다양성 계산"""
        if image_cube.shape[2] > 1:
            # 채널간 분산의 평균
            channel_means = np.mean(image_cube, axis=(0,1))
            return float(np.std(channel_means))
        return 0.0
    
    def _calculate_spatial_homogeneity(self, image_cube):
        """공간적 균질성 계산"""
        if image_cube.shape[0] > 1 and image_cube.shape[1] > 1:
            # 공간적 분산의 역수 (균질할수록 높은 값)
            spatial_mean = np.mean(image_cube, axis=2)
            spatial_var = np.var(spatial_mean)
            return float(1.0 / (1.0 + spatial_var))
        return 0.0
    
    def _calculate_percentile_in_distribution(self, value, feature_type, train_stats):
        """Train 분포에서의 백분위수 계산"""
        # 간단한 정규분포 가정하여 백분위수 추정
        if feature_type == 'brightness':
            mean = 0.5  # normalized image mean
            std = 0.2   # typical std
        elif feature_type == 'contrast':
            mean = 0.2  # typical contrast
            std = 0.1   # typical std
        else:
            mean = 0.0
            std = 1.0
        
        # Z-score를 백분위수로 변환 (근사)
        z_score = (value - mean) / (std + 1e-8)
        percentile = 0.5 + 0.5 * np.tanh(z_score / 2.0)  # sigmoid-like transformation
        return float(np.clip(percentile, 0.0, 1.0))

    def _get_sample_kde_features(self, idx):
        """KDE 방식: 모든 샘플에 동일한 분포 통계 feature vector 반환"""
        # 이미 계산된 고정 KDE 특성이 있으면 반환
        if hasattr(self, 'kde_features') and idx < len(self.kde_features):
            return self.kde_features[idx]
        
        # KDE 특성이 준비되지 않은 경우 기본값 반환
        print("Warning: KDE features not prepared, returning default values")
        # 라벨 개수에 따른 기본 차원 계산 (라벨당 8개 + 메타 6개)
        num_labels = len(self.column_config['label_columns'])
        default_dim = num_labels * 8 + 6
        return np.zeros(default_dim, dtype=np.float32)

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

        # === ROI ===

    def _parse_point(self, val):
        """
        문자열 '(x, y)' 같은 좌표를 튼튼하게 파싱해서 (x, y) 정수 튜플로 반환.
        실패 시 None.
        """
        if val is None or (isinstance(val, float) and np.isnan(val)):
            return None
        s = str(val).strip()
        # 흔한 오타/공백/괄호 문제 보정
        s = s.replace(' ', '').replace('))', ')').replace(':(', '(')
        # 앞뒤 괄호 제거
        if s.startswith('(') and s.endswith(')'):
            s = s[1:-1]
        if ',' not in s:
            return None
        try:
            x_str, y_str = s.split(',', 1)
            x = int(float(x_str))
            y = int(float(y_str))
            return (x, y)
        except Exception:
            return None

    def _extract_roi_points(self, row, wl):
        """
        특정 파장(wl ∈ {430,540,580})에 대한 TL/TR/BR/BL 좌표 4개를 파싱.
        4개 모두 정상 파싱되면 [(x,y),...] 반환, 아니면 None.
        """
        cols = [f"TL ({wl}nm)", f"TR ({wl}nm)", f"BR ({wl}nm)", f"BL ({wl}nm)"]
        pts = []
        for c in cols:
            if c not in row.index:
                return None
            pt = self._parse_point(row[c])
            if pt is None:
                return None
            pts.append(pt)
        return pts

    def _get_roi_bbox_from_row(self, row):
        """
        ROI 우선순위: 580 → 540 → 430. 유효한 좌표 세트 찾으면
        (x0,y0,x1,y1) bbox로 변환해서 반환. 없으면 None.
        """
        for wl in (580, 540, 430):
            pts = self._extract_roi_points(row, wl)
            if pts is not None:
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                x0, x1 = min(xs), max(xs)
                y0, y1 = min(ys), max(ys)
                # 혹시 좌표가 뒤집힌 경우 보정
                if x1 < x0: x0, x1 = x1, x0
                if y1 < y0: y0, y1 = y1, y0
                return (x0, y0, x1, y1)
        return None

    def _expand_clamp_bbox(self, bbox, w, h, margin=0.10):
        """
        bbox를 margin 비율만큼 확장하고 이미지 경계로 클램프.
        bbox: (x0,y0,x1,y1), 이미지 크기: w,h
        """
        x0, y0, x1, y1 = bbox
        bw = max(1, x1 - x0)
        bh = max(1, y1 - y0)
        dx = int(round(bw * margin))
        dy = int(round(bh * margin))
        x0 = max(0, x0 - dx)
        y0 = max(0, y0 - dy)
        x1 = min(w - 1, x1 + dx)
        y1 = min(h - 1, y1 + dy)
        return (x0, y0, x1, y1)
            # === ROI 끝 ===
    
    def _resolve_hsi_paths_with_fallback(self, row):
        """
        wavelengths = [430, 540, 580] 가정.
        image_path_start_index부터 순서대로 파일명이 온다고 가정.
        580 경로가 없을 때 fallback:
        - hsi_fallback_mode == 'duplicate_540' 이면 540 경로를 복제
        - 'zeros' 이면 None(빈 채널)로 둬서 후처리에서 0으로 채움
        """
        wavelengths = self.column_config['wavelengths']
        image_path_start = self.column_config['column_order']['image_path_start_index']
        base_dir = self.column_config['base_dirs']['hsi_image_dir']
        fb_mode = self.column_config.get('hsi_fallback_mode', 'duplicate_540')

        img_paths = []
        for i, wl in enumerate(wavelengths):
            col_idx = image_path_start + i
            if col_idx < len(row):
                name = row.iloc[col_idx]
                if pd.notna(name) and str(name).strip() != '':
                    img_paths.append(os.path.join(base_dir, str(name)))
                else:
                    img_paths.append(None)
            else:
                img_paths.append(None)

        # 580(마지막 인덱스) 폴백 처리
        if len(wavelengths) >= 3 and wavelengths[2] == 580:
            p580 = img_paths[2]
            if not p580 or not os.path.exists(p580):
                if fb_mode == 'duplicate_540' and len(wavelengths) >= 2:
                    p540 = img_paths[1] if len(img_paths) > 1 else None
                    if p540 and os.path.exists(p540):
                        img_paths[2] = p540  # 540을 580 자리에 복제 사용
                    else:
                        img_paths[2] = None  # zeros로 갈 것
                else:
                    img_paths[2] = None  # zeros
        return img_paths

    def _load_image_cube(self, idx):
        row = self.data.iloc[idx]
        wavelengths = self.column_config['wavelengths']
        image_size = tuple(self.column_config['image_size'])
        hsi_paths = self._resolve_hsi_paths_with_fallback(row)  # 새 함수 사용

        # RGB 경로는 기존 방식대로
        rgb_idx = self.column_config['column_order'].get('rgb_image_path_start_index')
        rgb_base = self.column_config['base_dirs'].get('rgb_image_dir')
        rgb_path = None
        if rgb_idx is not None and rgb_base is not None and rgb_idx < len(row):
            rgb_name = row.iloc[rgb_idx]
            if pd.notna(rgb_name) and str(rgb_name).strip() != '':
                cand = os.path.join(rgb_base, str(rgb_name))
                if os.path.exists(cand):
                    rgb_path = cand

        # 참조 해상도(ROI 좌표 쓸 때 필요하면 그대로 유지)
        ref_path = next((p for p in hsi_paths if p and os.path.exists(p)), rgb_path)
        if ref_path is None:
            return None
        try:
            with Image.open(ref_path) as ref_img:
                ref_w, ref_h = ref_img.size
        except Exception:
            return None

        # 필요시 좌표 → bbox 얻고 확장/클램프 (이미 구현되어 있으면 그대로 사용)
        bbox = None
        if hasattr(self, "_get_roi_bbox_from_row"):
            bbox = self._get_roi_bbox_from_row(row)
            if bbox and hasattr(self, "_expand_clamp_bbox"):
                bbox = self._expand_clamp_bbox(bbox, ref_w, ref_h, margin=0.10)

        # ===== HSI 채널 로딩(폴백 반영) =====
        hsi_stack = []
        for i, p in enumerate(hsi_paths):
            if p and os.path.exists(p):
                try:
                    img = Image.open(p).convert('L')
                    if bbox is not None:
                        x0, y0, x1, y1 = bbox
                        img = img.crop((x0, y0, x1 + 1, y1 + 1))
                    img = img.resize(image_size, resample=Image.NEAREST)
                    arr = np.array(img, dtype=np.float32)
                    if self.scaler_mode == 'normalized':
                        arr = arr / 255.0
                    hsi_stack.append(arr)
                except Exception as e:
                    print(f"[Error Loading HSI] row_id={idx} | path={p} | error={e}")
                    return None
            else:
                # 폴백: zeros 채널 추가
                h, w = image_size
                arr = np.zeros((h, w), dtype=np.float32)  # normalized 모드 기준 0.0
                hsi_stack.append(arr)

        if len(hsi_stack) != len(wavelengths):
            return None
        hsi_stack = np.stack(hsi_stack, axis=-1)  # (H, W, len(wavelengths))
        
        # ===== RGB =====
        if rgb_path:
            try:
                img = Image.open(rgb_path).convert('RGB')
                if bbox is not None:
                    x0, y0, x1, y1 = bbox
                    img = img.crop((x0, y0, x1 + 1, y1 + 1))
                img = img.resize(image_size, resample=Image.BILINEAR)
                rgb_arr = np.array(img, dtype=np.float32) / 255.0
            except Exception as e:
                print(f"[Error Loading RGB] row_id={idx} | path={rgb_path} | error={e}")
                rgb_arr = np.zeros((*image_size, 3), dtype=np.float32)
        else:
            # RGB 경로 없는 경우에도 제로 채널 생성
            rgb_arr = np.zeros((*image_size, 3), dtype=np.float32)

        # 항상 HSI와 RGB 붙여서 반환
        image_cube = np.concatenate([hsi_stack, rgb_arr], axis=-1)  # (H,W,6)

        return image_cube
    
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
        
        # KDE 특성 추가
        if self.use_kde:
            kde_tensor = torch.from_numpy(self.kde_features[idx])
            return image_tensor, label_tensor, kde_tensor, idx
        else:
            return image_tensor, label_tensor, idx

# collate_fn: None 샘플 필터링 및 빈 배치 방지
from torch.utils.data.dataloader import default_collate
import torch

def skip_invalid_collate(batch):
    batch = [b for b in batch if b is not None]
    if len(batch) == 0:
        # 빈 배치는 unpack 오류 방지용으로 empty tensor 반환
        return torch.empty(0), torch.empty(0), []
    
    # KDE 특성이 있는지 확인 (첫 번째 샘플의 길이로 판단)
    if len(batch[0]) == 4:  # image, label, kde, idx
        images = torch.stack([item[0] for item in batch])
        labels = torch.stack([item[1] for item in batch])
        kde_features = torch.stack([item[2] for item in batch])
        indices = [item[3] for item in batch]
        return images, labels, kde_features, indices
    else:  # image, label, idx
        return default_collate(batch)


def create_hsi_data_loaders(csv_path, column_config_path, batch_size=8, num_workers=4, 
                           val_split=0.1, test_split=0.1, random_state=42, 
                           train_transform=None, val_transform=None, test_transform=None, scaler_mode="normalized", use_kde=False):
    """
    HSI 데이터 로더를 생성합니다.
    scaler_mode: 'normalized' | 'raw' | 'off' (config["data"]["scaler_mode"]에서만 설정)
    use_kde: KDE 특성을 사용할지 여부 (feature leakage 방지를 위해 train 데이터만 사용하여 KDE 통계 계산)
    """
    from torch.utils.data import Subset
    
    # 1. 인덱스 분할 먼저 수행 (KDE 계산 전에)
    # 임시 데이터셋을 만들어서 전체 크기 확인
    temp_dataset = HSIDataset(csv_path, column_config_path, fit_scaler=False, scaler_mode="off", use_kde=False)
    total_size = len(temp_dataset)
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
    
    print(f"Data split: Train={len(train_indices)}, Val={len(val_indices)}, Test={len(test_indices)}")
    
    # 2. train 인덱스를 사용하여 전체 데이터셋 생성 (KDE는 train으로만 계산)
    print("Creating full dataset and fitting scaler...")
    full_dataset = HSIDataset(csv_path, column_config_path, fit_scaler=True, scaler_mode=scaler_mode, 
                             use_kde=use_kde, train_indices=train_indices)
    scaler = full_dataset.scaler
    
    # 3. Subset으로 분할
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
            self._debug_transform_applied = False  # 디버그용 플래그
        
        def __getitem__(self, idx):
            item = self.dataset[idx]
            if item is None:
                return None
            
            # KDE 특성이 있는지 확인
            if len(item) == 4:  # image, label, kde, idx
                images, labels, kde_features, sample_idx = item
            else:  # image, label, idx
                images, labels, sample_idx = item
                kde_features = None
            
            # 첫 번째 샘플에서만 transform 적용 여부 로그 출력
            if not self._debug_transform_applied and self.transform:
                print(f"[DEBUG] Applying transform: {type(self.transform).__name__}")
                print(f"[DEBUG] Transform details: {self.transform.transforms if hasattr(self.transform, 'transforms') else 'Custom transform'}")
                self._debug_transform_applied = True
            
            if self.transform:
                original_shape = images.shape
                images = self.transform(images)
                
                # 첫 번째 샘플에서만 shape 변화 로그 출력
                if not self._debug_transform_applied:
                    print(f"[DEBUG] Image shape before transform: {original_shape}")
                    print(f"[DEBUG] Image shape after transform: {images.shape}")
            
            # 반환 형식 맞추기
            if kde_features is not None:
                return images, labels, kde_features, sample_idx
            else:
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
#!/usr/bin/env python3
"""
HSI 예측 모듈 (학습 파이프라인과 완전 호환)

이 스크립트는 HSI best model을 로드하고 각 band의 image path 리스트를 입력받아 예측을 수행합니다.
학습 파이프라인과 완전히 호환되도록 설계되었으며, 고해상도 XAI (CAM/Attention) 생성 기능을 포함합니다.

사용법:
    # 기본 예측
    python predict_xai_hsi.py --model_dir /path/to/model_dir --image_paths /path/to/band1.png /path/to/band2.png ...
"""

import os
import sys
import json
import argparse
import torch
import numpy as np
from PIL import Image
import pickle
import mlflow
import tempfile
import warnings
import base64
import cv2
from torch.utils.data import Dataset, DataLoader
warnings.filterwarnings('ignore')

from typing import List, Optional, Dict, Any

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_model
from utils.transforms_hsi import get_test_transforms
from utils.xai import (
    generate_cam_arrays, _infer_task_from_outputs, cam_to_png_bytes, save_cam_arrays,
    generate_attention_arrays, _find_vit_attention_modules
)

class InferenceDataset(Dataset):
    def __init__(self, samples, parent):
        """
        samples: List[str], 반드시 (샘플 개수) * (band 수) 만큼의 경로가 있어야 함
        parent: HSIPredictor 인스턴스
        """
        self.samples = samples
        self.parent = parent
        self.image_size = self.parent.crop_size
        self.hsi_channels = self.parent.config.get("model", {}).get("in_channels", 9)

        assert len(self.samples) % self.hsi_channels == 0, "샘플 개수는 band 수의 배수여야 합니다."

    def __len__(self):
        return int(len(self.samples) / self.hsi_channels)
    
    def _load_one_sample_cube(self, image_paths):
        # HSI 단일 샘플 로딩: (H, W, C)
        band_arrays = []
        
        if len(image_paths) != self.hsi_channels:
            raise ValueError(f"Number of image paths ({len(image_paths)}) must match number of wavelengths ({self.hsi_channels})")

        for path in image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            img = Image.open(path).convert("L")

            # 학습 해상도와 맞추기
            if self.parent.target_hw and img.size[::-1] != self.parent.target_hw:
                img = img.resize(self.parent.target_hw[::-1], resample=Image.NEAREST)

            band_arrays.append(np.asarray(img, dtype=np.float32))

        image_cube = np.stack(band_arrays, axis=-1)  # (H, W, C)

        # 학습 시 사용한 /255 정규화 반영
        if self.parent.scaler_mode == "normalized":
            image_cube /= 255.0

        return image_cube
    
    def _to_chw_tensor_with_scaler_and_transform(self, cube_hwc):
        # (H, W, C) → (C, H, W)
        image_tensor = torch.from_numpy(cube_hwc).permute(2, 0, 1).float()

        # StandardScaler - 학습 파이프라인과 동일한 순서
        if self.parent.scaler is not None:
            # scaler의 mean_와 scale_를 사용하여 정규화
            mean = torch.as_tensor(self.parent.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
            scale = torch.as_tensor(self.parent.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)

            # 0으로 나누기 방지
            eps = 1e-6
            image_tensor = (image_tensor - mean) / torch.clamp(scale, min=eps)
        
        # 중앙 크롭 적용 - 학습 파이프라인과 동일한 순서
        transform = get_test_transforms(image_size=self.parent.crop_size)
        image_tensor = transform(image_tensor)

        return image_tensor

    def __getitem__(self, idx):
        image_paths = self.samples[idx * self.hsi_channels:(idx + 1) * self.hsi_channels]
        cube_hwc = self._load_one_sample_cube(image_paths)
        tensor_chw = self._to_chw_tensor_with_scaler_and_transform(cube_hwc)
        meta = {"paths": image_paths}
        return tensor_chw, cube_hwc, meta


def hsi_batch_collate(batch):
    tensors, cubes, metas = zip(*batch)
    batch_bchw = torch.stack(tensors, dim=0)
    return batch_bchw, list(cubes), list(metas)


class HSIPredictor:
    """HSI 예측을 위한 클래스 (학습 파이프라인과 완전 호환)"""
    
    def __init__(self, model_dir, device=None):
        """
        Args:
            model_dir: 모델 디렉토리 (best_model.pt, config.json, scaler.pkl 포함)
            device: 사용할 디바이스
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None else device
        print(f"Using device: {self.device}")

        # config 먼저 열어 scaler_mode 확보 (scaler.pkl 존재 여부 판단용)
        config_path = os.path.join(model_dir, "configs", "temp_config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        print(f"Loaded config from: {config_path}")

        self.scaler_mode = self.config.get("data", {}).get("scaler_mode", "normalized")

        # 아티팩트 로드
        self.model, self.scaler, self.column_config = self._build_artifacts(model_dir)
        self.model.eval()
        
        # 라벨 타입 정보 설정
        self._setup_label_info()
        
        # 모델 정보 출력
        self._print_model_info()
        
        # === 학습 파이프라인과 동일한 전처리를 위한 설정 ===
        self.target_hw   = tuple(self.column_config.get("image_size", [])) or None  # (H, W)
        self.crop_size   = tuple(self.config.get("data", {}).get("crop_size", [224, 224]))
        self.wavelengths = self.column_config.get("wavelengths", [])
        self.xai_mode = 'gradcam'   
        self.xai_return = 'base64'
        self._has_attn = len(_find_vit_attention_modules(self.model)) > 0
        
        # XAI 해상도 개선을 위한 설정
        self.xai_upscale_factor = 2.0  # CAM을 원본보다 2배 크게 업스케일
        self.xai_use_bicubic = True    # 더 선명한 보간을 위해 bicubic 사용
        self.xai_disable_contrast_enhancement = False  # 대비 개선 기본 활성화

    def _build_artifacts(self, model_dir):
        """
        MLflow artifacts 디렉토리에서 아티팩트들을 로드합니다.
        
        Args:
            model_dir: MLflow artifacts 디렉토리 경로 
                      (/mnt/data/mlflow_artifacts/experiment_id/run_id/artifacts)
            
        Returns:
            tuple: (model, config, scaler, column_config)
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        print(f"Loading artifacts from MLflow directory: {model_dir}")

        # 1. column_config 로드 (config['data']['column_config']에서 경로 가져오기)
        column_config_path = "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI/configs/column_config.json"
        column_config_path = self.config['data'].get('column_config', column_config_path)

        if not os.path.exists(column_config_path):
            raise FileNotFoundError(f"Column config file not found: {column_config_path}")
            
        with open(column_config_path, 'r') as f:
            column_config = json.load(f)
        print(f"Loaded column_config from: {column_config_path}")
            
        # 2. 모델 로드 (./models/best_model.pt)
        model_path = os.path.join(model_dir, "models", "best_model.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        print("Creating model architecture from config...")
        model = load_model(self.config)
        
        print(f"Loading state dict from: {model_path}")
        state_dict = torch.load(model_path, map_location=self.device)
        
        # DataParallel로 감싸진 경우 처리
        if list(state_dict.keys())[0].startswith('module.'):
            from collections import OrderedDict
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                name = k[7:]  # 'module.' 제거
                new_state_dict[name] = v
            state_dict = new_state_dict
            
        model.load_state_dict(state_dict)
        model = model.to(self.device)
        
        # 3. scaler 로드 (./scaler/temp_scaler.pkl)
        scaler = None
        scaler_path = os.path.join(model_dir, "scaler", "temp_scaler.pkl")
        if self.scaler_mode != "off":
            if os.path.exists(scaler_path):
                print(f"Loading scaler from: {scaler_path}")
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
            else:
                raise ValueError(f"scaler_mode is '{self.scaler_mode}' but scaler not found at {scaler_path}")
        else:
            print("scaler_mode is 'off', skipping normalization")
            
        return model, scaler, column_config
        
    def _setup_label_info(self):
        """라벨 타입 정보를 설정합니다."""
        self.label_columns = self.column_config.get('label_columns', [])
        self.label_types = self.column_config.get('label_types', {})
        self.cls_indices = []
        self.reg_indices = []
        
        # 분류 인덱스 설정
        if 'classification' in self.label_types:
            cls_labels = self.label_types['classification']
            for label in cls_labels:
                if label in self.label_columns:
                    idx = self.label_columns.index(label)
                    self.cls_indices.append(idx)
                    
        # 회귀 인덱스 설정
        if 'regression' in self.label_types:
            reg_labels = self.label_types['regression']
            for label in reg_labels:
                if label in self.label_columns:
                    idx = self.label_columns.index(label)
                    self.reg_indices.append(idx)
                    
        print(f"Classification indices: {self.cls_indices}")
        print(f"Regression indices: {self.reg_indices}")
        
        # scaler.mean_ shape와 wavelengths 수 일치 확인
        if self.scaler is not None and hasattr(self.scaler, 'mean_'):
            wavelengths = self.column_config.get('wavelengths', [])
            if len(self.scaler.mean_) != len(wavelengths):
                print(f"Warning: scaler.mean_ shape ({len(self.scaler.mean_)}) doesn't match wavelengths count ({len(wavelengths)})")
    
    def _gen_cam_pack(self, img_tensor, cube_hwc, output, *, task: str, target_index: int):
        if self.xai_mode == 'attn':
            if not self._has_attn:
                raise RuntimeError("model에서 attention 모듈 찾을 수 없음")
            return generate_attention_arrays(
                model=self.model,
                image_tensor_bchw=img_tensor.to(self.device),
                outputs=output,
                task=task,
                target_index=target_index,
                assume_cls_token=True,
            )

        else:
            # default: gradcam
            cam_pack = generate_cam_arrays(
                model=self.model,
                image_tensor_bchw=img_tensor.to(self.device),
                outputs=output,
                task=task,
                target_index=target_index,
                target_layer_name=None,
                image_cube_hwc=cube_hwc,
                wavelengths=self.wavelengths,
                rgb_strategy='auto',
                alpha=0.35
            )
        
        # 해상도 개선 적용
        cam_pack = self._enhance_cam_resolution(cam_pack, cube_hwc)
        return cam_pack
    
    def _enhance_cam_resolution(self, cam_pack, cube_hwc):
        """CAM 해상도를 개선합니다."""
        
        cam = cam_pack['cam']  # (H, W) numpy array [0,1]
        original_shape = cube_hwc.shape[:2]  # (H, W)
        
        # 1. 원본 이미지 크기로 업스케일 (더 정확한 매핑을 위해)
        if cam.shape != original_shape:
            if self.xai_use_bicubic:
                # bicubic 보간으로 더 선명하게
                cam_upscaled = cv2.resize(cam, (original_shape[1], original_shape[0]), 
                                        interpolation=cv2.INTER_CUBIC)
            else:
                cam_upscaled = cv2.resize(cam, (original_shape[1], original_shape[0]), 
                                        interpolation=cv2.INTER_LINEAR)
        else:
            cam_upscaled = cam.copy()
        
        # 2. 추가 업스케일링 (선택적)
        if self.xai_upscale_factor > 1.0:
            target_h = int(original_shape[0] * self.xai_upscale_factor)
            target_w = int(original_shape[1] * self.xai_upscale_factor)
            
            # INTER_LANCZOS4는 가장 고품질 보간법 중 하나
            cam_upscaled = cv2.resize(cam_upscaled, (target_w, target_h), 
                                    interpolation=cv2.INTER_LANCZOS4)
        
        # 3. 가우시안 블러를 약간 적용하여 노이즈 제거 (선택적)
        cam_upscaled = cv2.GaussianBlur(cam_upscaled, (3, 3), 0.5)
        
        # 4. 값 범위 재정규화
        cam_min, cam_max = cam_upscaled.min(), cam_upscaled.max()
        if cam_max > cam_min:
            cam_upscaled = (cam_upscaled - cam_min) / (cam_max - cam_min)
        
        # 5. 히스토그램 평활화로 대비 개선 (선택적)
        if not getattr(self, 'xai_disable_contrast_enhancement', False):
            cam_enhanced = self._enhance_contrast(cam_upscaled)
        else:
            cam_enhanced = cam_upscaled
        
        # 결과 업데이트
        enhanced_pack = cam_pack.copy()
        enhanced_pack['cam'] = cam_enhanced
        enhanced_pack['original_resolution'] = original_shape
        enhanced_pack['enhanced_resolution'] = cam_enhanced.shape
        
        return enhanced_pack
    
    def _enhance_contrast(self, cam):
        """CAM의 대비를 개선합니다."""
        
        # 히스토그램 평활화를 위해 uint8로 변환
        cam_uint8 = (cam * 255).astype(np.uint8)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization) 적용
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cam_enhanced = clahe.apply(cam_uint8)
        
        # 다시 [0,1] 범위로 정규화
        cam_enhanced = cam_enhanced.astype(np.float32) / 255.0
        
        return cam_enhanced

    def _print_model_info(self):
        """모델 정보를 출력합니다."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"Model parameters: {total_params:,} total, {trainable_params:,} trainable")
        
        # 입력 채널 수 출력
        wavelengths = self.column_config.get('wavelengths', [])
        print(f"Input channels (wavelengths): {len(wavelengths)}")
        print(f"Wavelengths: {wavelengths}")
        
    def predict_batch(self, image_paths_list: List[str], batch_size=16, crop_size=None, *, xai: bool = False,
                      xai_layer: Optional[str] = None, xai_index: Optional[int] = None, xai_save_dir: Optional[str] = None):
        """
        여러 이미지 경로 리스트를 받아서 배치 예측을 수행합니다.

        Args:
            image_paths_list: 이미지 경로 리스트들의 리스트
            crop_size: 크롭할 크기 (height, width), None이면 config에서 가져옴
            xai, xai_layer, xai_index: predict()와 동일

        Returns:
            list: 예측 결과 리스트 (JSON 직렬화 가능)
        """
        if crop_size is None:
            crop_size = self.crop_size

        all_preds = {}
        sample_idx = 0

        dataset = InferenceDataset(samples=image_paths_list, parent=self)
        batch_size = min(batch_size, len(dataset))
        dataloader = DataLoader(dataset, batch_size=batch_size,
                                shuffle=False, collate_fn=hsi_batch_collate)
        
        for batch_idx, (batch_bchw, cubes_hwc, metas) in enumerate(dataloader):
            batch_bchw = batch_bchw.to(self.device)
            with torch.no_grad():
                model_out = self.model(batch_bchw)
            
            # 배치 크기
            B = batch_bchw.size(0)

            # 샘플 단위로 처리
            for i in range(B):
                # ----- 1) per-sample 출력 뽑기 -----
                if isinstance(model_out, dict):
                    # 각 헤드에서 i번째 샘플만 추출 (shape: (1, num_labels))
                    out_i = {
                        k: v[i:i+1] for k, v in model_out.items()
                    }
                else:
                    # 단일 텐서 (B, K) -> (1, K)
                    out_i = model_out[i:i+1]

                sample_results = {}

                # ----- 2) 예측값 수집 (classification / regression) -----
                if isinstance(out_i, dict):
                    # (a) 분류
                    if 'classification' in out_i and self.cls_indices:
                        cls_logits = out_i['classification']  # (1, Cc)
                        cls_probs = torch.sigmoid(cls_logits).squeeze(0).cpu().numpy()  # (Cc,)
                        cls_results = {}
                        # 헤드 로컬 인덱스가 0..Cc-1 이고, self.cls_indices는 전역 컬럼 인덱스
                        for idx_in_head, col_idx in enumerate(self.cls_indices):
                            cls_results[self.label_columns[col_idx]] = float(cls_probs[idx_in_head])
                        sample_results['classification'] = cls_results

                    # (b) 회귀
                    if 'regression' in out_i and self.reg_indices:
                        reg_vals = out_i['regression'].squeeze(0).cpu().numpy()  # (Cr,)
                        reg_results = {}
                        for idx_in_head, col_idx in enumerate(self.reg_indices):
                            reg_results[self.label_columns[col_idx]] = float(reg_vals[idx_in_head])
                        sample_results['regression'] = reg_results

                else:
                    # 단일 헤드 (예: (1, K)) → 구성에 따라 분기
                    out_vec = out_i.squeeze(0)  # (K,)
                    output_values = out_vec.cpu().numpy()

                    if self.cls_indices and not self.reg_indices:
                        # 분류만
                        cls_probs = torch.sigmoid(out_vec).cpu().numpy()
                        cls_results = {}
                        for idx_in_head, col_idx in enumerate(self.cls_indices):
                            cls_results[self.label_columns[col_idx]] = float(cls_probs[idx_in_head])
                        sample_results['classification'] = cls_results

                    elif not self.cls_indices and self.reg_indices:
                        # 회귀만
                        reg_results = {}
                        for idx_in_head, col_idx in enumerate(self.reg_indices):
                            reg_results[self.label_columns[col_idx]] = float(output_values[idx_in_head])
                        sample_results['regression'] = reg_results

                    else:
                        # 단일 벡터에 분류+회귀가 순서대로 붙은 구조라면,
                        # 기존 로직 유지하되 "헤드 로컬 인덱스" 개념을 지키도록 보정
                        n_cls = len(self.cls_indices)
                        n_reg = len(self.reg_indices)
                        if n_cls > 0:
                            cls_probs = torch.sigmoid(out_vec[:n_cls]).cpu().numpy()
                            cls_results = {}
                            for idx_in_head, col_idx in enumerate(self.cls_indices):
                                cls_results[self.label_columns[col_idx]] = float(cls_probs[idx_in_head])
                            sample_results['classification'] = cls_results
                        if n_reg > 0:
                            reg_vals = output_values[n_cls:n_cls+n_reg]
                            reg_results = {}
                            for idx_in_head, col_idx in enumerate(self.reg_indices):
                                reg_results[self.label_columns[col_idx]] = float(reg_vals[idx_in_head])
                            sample_results['regression'] = reg_results

                # ----- 3) XAI 생성 (옵션) -----
                if xai:
                    img_tensor = batch_bchw[i:i+1]     # ✅ 배치-내 샘플 인덱스 사용
                    cube_hwc  = cubes_hwc[i]

                    # (a) 분류 XAI
                    if 'classification' in sample_results:
                        xai_items = {}
                        for idx_in_head, col_idx in enumerate(self.cls_indices):
                            cam_pack = self._gen_cam_pack(
                                img_tensor=img_tensor,
                                cube_hwc=cube_hwc,
                                output=out_i,                # per-sample 출력 전달
                                task='classification',
                                target_index=idx_in_head,     # ✅ 헤드-로컬 인덱스 사용
                            )
                            target_label = self.label_columns[col_idx]

                            saved = None
                            if xai_save_dir:
                                def _safe_name(s): 
                                    return "".join(c if c.isalnum() or c in ("-","_") else "_" for c in str(s))
                                base = f"sample_idx_{sample_idx}_{_safe_name(target_label)}_{self.xai_mode}"
                                saved = save_cam_arrays(
                                    cam=cam_pack['cam'],
                                    save_dir=xai_save_dir,
                                    basename=base,
                                    save_heatmap=True,
                                    save_rgb=False,
                                    save_overlay=True
                                )["heatmap"]

                            if self.xai_return == 'base64':
                                heatmap_png_bytes = cam_to_png_bytes(cam_pack['cam'])
                                payload = {
                                    'layer': cam_pack['layer'],
                                    'image_base64': base64.b64encode(heatmap_png_bytes).decode("utf-8")
                                }
                                if saved: payload['image_path'] = saved
                            else:
                                if not saved:
                                    os.makedirs(xai_save_dir or "xai_outputs", exist_ok=True)
                                    def _safe_name(s): 
                                        return "".join(c if c.isalnum() or c in ("-","_") else "_" for c in str(s))
                                    base = f"sample_idx_{sample_idx}_{_safe_name(target_label)}_{self.xai_mode}"
                                    saved = save_cam_arrays(
                                        cam=cam_pack['cam'],
                                        save_dir=(xai_save_dir or "xai_outputs"),
                                        basename=base,
                                        save_heatmap=True
                                    )["heatmap"]
                                payload = {'layer': cam_pack['layer'], 'image_path': saved}

                            xai_items[target_label] = payload

                        sample_results['xai_classification'] = xai_items

                    # (b) 회귀 XAI
                    if 'regression' in sample_results:
                        xai_items = {}
                        for idx_in_head, col_idx in enumerate(self.reg_indices):
                            cam_pack = self._gen_cam_pack(
                                img_tensor=img_tensor,
                                cube_hwc=cube_hwc,
                                output=out_i,                 # per-sample 출력 전달
                                task='regression',
                                target_index=idx_in_head,      # ✅ 헤드-로컬 인덱스 사용
                            )
                            target_label = self.label_columns[col_idx]

                            saved = None
                            if xai_save_dir:
                                def _safe_name(s): 
                                    return "".join(c if c.isalnum() or c in ("-","_") else "_" for c in str(s))
                                base = f"sample_idx_{sample_idx}_{_safe_name(target_label)}_{self.xai_mode}"
                                saved = save_cam_arrays(
                                    cam=cam_pack['cam'],
                                    save_dir=xai_save_dir,
                                    basename=base,
                                    save_heatmap=True,
                                    save_rgb=False,
                                    save_overlay=True
                                )["heatmap"]

                            if self.xai_return == 'base64':
                                heatmap_png_bytes = cam_to_png_bytes(cam_pack['cam'])
                                payload = {
                                    'layer': cam_pack['layer'],
                                    'image_base64': base64.b64encode(heatmap_png_bytes).decode("utf-8")
                                }
                                if saved:
                                    payload['image_path'] = saved
                            else:
                                if not saved:
                                    os.makedirs(xai_save_dir or "xai_outputs", exist_ok=True)
                                    def _safe_name(s): 
                                        return "".join(c if c.isalnum() or c in ("-","_") else "_" for c in str(s))
                                    base = f"sample_idx_{sample_idx}_{_safe_name(target_label)}_{self.xai_mode}"
                                    saved = save_cam_arrays(
                                        cam=cam_pack['cam'],
                                        save_dir=(xai_save_dir or "xai_outputs"),
                                        basename=base,
                                        save_heatmap=True
                                    )["heatmap"]
                                payload = {'layer': cam_pack['layer'], 'image_path': saved}

                            xai_items[target_label] = payload

                        sample_results['xai_regression'] = {'mode': 'per_target', 'items': xai_items}

                # 결과 적재
                all_preds[f"sample idx {sample_idx}"] = sample_results
                sample_idx += 1

        return all_preds


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='HSI Prediction (Learning Pipeline Compatible)')
    
    # mutually-exclusive group for model loading
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument('--model_dir', type=str,
                           help='Model directory containing best_model.pt, config.json, scaler.pkl')
    model_group.add_argument('--run_id', type=str,
                           help='MLflow run ID to download artifacts from')
    
    parser.add_argument('--experiment_id', type=str,
                       help='MLflow experiment ID (required when using --run_id)')
    
    parser.add_argument('--image_paths', nargs='+', required=True,
                       help='Paths to band images')
    parser.add_argument('--crop_size', nargs=2, type=int, default=None,
                       help='Crop size (height width), default from config')
    parser.add_argument('--output', type=str,
                       help='Output file path for results')
    parser.add_argument('--xai', action='store_true', help='Enable XAI')
    parser.add_argument('--xai-mode', choices=['gradcam', 'attn'], default='gradcam',
                    help='XAI backend: gradcam or attention')
    parser.add_argument('--xai-return', choices=['base64', 'url'], default='base64',
                    help='Return CAM as base64 or file path (url)')
    parser.add_argument('--xai-save-dir', type=str, default=None,
                    help='If set, save per-label CAM heatmaps to this directory')
    
    args = parser.parse_args()
    
    # 모델 디렉토리 설정
    model_dir = args.model_dir
    temp_dir = None
    
    if args.run_id:
        # MLflow run_id에서 아티팩트 직접 접근
        print(f"Loading artifacts from MLflow run: {args.run_id}")
        
        # /mnt/data/mlflow_artifacts에서 run_id 찾기
        mlflow_artifacts_base = "/mnt/data/mlflow_artifacts"
        model_dir = None
        
        if os.path.exists(mlflow_artifacts_base):
            print(f"Searching for run_id in: {mlflow_artifacts_base}")
            
            # experiment_id 디렉토리들을 순회하면서 run_id 찾기
            for experiment_dir in os.listdir(mlflow_artifacts_base):
                experiment_path = os.path.join(mlflow_artifacts_base, experiment_dir)
                if os.path.isdir(experiment_path):
                    run_path = os.path.join(experiment_path, args.run_id)
                    if os.path.exists(run_path):
                        artifacts_path = os.path.join(run_path, "artifacts")
                        if os.path.exists(artifacts_path):
                            model_dir = artifacts_path
                            print(f"Found artifacts at: {artifacts_path}")
                            break
            
            if model_dir is None:
                raise FileNotFoundError(f"Run ID {args.run_id} not found in {mlflow_artifacts_base}")
        else:
            raise FileNotFoundError(f"MLflow artifacts directory not found: {mlflow_artifacts_base}")
                
        print(f"Final model directory: {model_dir}")
    
    # 예측기 생성
    try:
        predictor = HSIPredictor(model_dir=model_dir)
        predictor.xai_mode = args.xai_mode
        predictor.xai_return = args.xai_return
        
        # 예측 수행
        results = predictor.predict_batch(
            image_paths_list=args.image_paths,
            crop_size=tuple(args.crop_size) if args.crop_size else None,
            xai=args.xai,
            xai_save_dir=args.xai_save_dir,
        )

        # 결과 출력
        for key, result in results.items():
            if key in ['xai_classification', 'xai_regression']:
                continue
            print(f"\n=== Results for {key} ===")
            if 'classification' in result:
                print(f"  Classification probabilities for {key}:")
                for label, prob in result['classification'].items():
                    print(f"    {label}: {prob:.4f}")

            if 'regression' in result:
                print(f"  Regression values for {key}:")
                for label, value in result['regression'].items():
                    print(f"    {label}: {value:.4f}")
                
        # 파일로 저장
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")
            
    except Exception as e:
        print(f"Error during prediction: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 임시 디렉토리 정리
        if temp_dir and os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")


if __name__ == "__main__":
    main() 
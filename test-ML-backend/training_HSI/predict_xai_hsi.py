#!/usr/bin/env python3
"""
HSI 예측 모듈 (학습 파이프라인과 완전 호환)

이 스크립트는 HSI best model을 로드하고 각 band의 image path 리스트를 입력받아 예측을 수행합니다.
학습 파이프라인과 완전히 호환되도록 설계되었습니다.

사용법:
    # 방법 1: 로컬 모델 디렉토리 사용
    python predict_hsi.py --model_dir /path/to/model_dir --image_paths /path/to/band1.png /path/to/band2.png ...
    
    # 방법 2: MLflow run ID 사용
    python predict_hsi.py --run_id <mlflow_run_id> --experiment_id <experiment_id> --image_paths /path/to/band1.png /path/to/band2.png ...
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
warnings.filterwarnings('ignore')

from typing import List, Optional, Dict, Any

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_model
from utils.transforms_hsi import get_test_transforms
from utils.xai import generate_cam_arrays, _infer_task_from_outputs, cam_to_png_bytes, save_cam_arrays

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
        
    def _build_artifacts(self, model_dir):
        """
        MLflow artifacts 디렉토리에서 아티팩트들을 로드합니다.
        
        Args:
            model_dir: MLflow artifacts 디렉토리 경로 
                      (/mnt/data/mlflow_artifacts/experiment_id/run_id/artifacts)
            
        Returns:
            tuple: (model, scaler, column_config)
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        print(f"Loading artifacts from MLflow directory: {model_dir}")

        # 1. column_config 로드 (config['data']['column_config']에서 경로 가져오기)
        abs_path_candidate = "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI/configs/column_config_nubci.json"
        cfg_path_in_config = self.config.get('data', {}).get('column_config', None)

        if cfg_path_in_config and not os.path.isabs(cfg_path_in_config):
            cfg_path_in_config = os.path.join(model_dir, "configs", cfg_path_in_config)

        # 우선순위: 절대경로 -> config 지정 경로
        column_config_path = None
        for cand in [abs_path_candidate, cfg_path_in_config]:
            if cand and os.path.exists(cand):
                column_config_path = cand
                break

        if not column_config_path:
            raise FileNotFoundError(
                "column_config JSON not found.\n"
                f"  Tried absolute: {abs_path_candidate}\n"
                f"  Config-specified: {cfg_path_in_config}"
            )

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
        self.label_types = self.column_config.get('label_types', {})
        self.cls_indices = []
        self.reg_indices = []
        
        # 분류 인덱스 설정
        if 'classification' in self.label_types:
            cls_labels = self.label_types['classification']
            for label in cls_labels:
                if label in self.column_config['label_columns']:
                    idx = self.column_config['label_columns'].index(label)
                    self.cls_indices.append(idx)
                    
        # 회귀 인덱스 설정
        if 'regression' in self.label_types:
            reg_labels = self.label_types['regression']
            for label in reg_labels:
                if label in self.column_config['label_columns']:
                    idx = self.column_config['label_columns'].index(label)
                    self.reg_indices.append(idx)
                    
        print(f"Classification indices: {self.cls_indices}")
        print(f"Regression indices: {self.reg_indices}")
        
        # scaler.mean_ shape와 wavelengths 수 일치 확인
        if self.scaler is not None and hasattr(self.scaler, 'mean_'):
            wavelengths = self.column_config.get('wavelengths', [])
            if len(self.scaler.mean_) != len(wavelengths):
                print(f"Warning: scaler.mean_ shape ({len(self.scaler.mean_)}) doesn't match wavelengths count ({len(wavelengths)})")
        
    def _print_model_info(self):
        """모델 정보를 출력합니다."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"Model parameters: {total_params:,} total, {trainable_params:,} trainable")
        
        # 입력 채널 수 출력
        wavelengths = self.column_config.get('wavelengths', [])
        print(f"Input channels (wavelengths): {len(wavelengths)}")
        print(f"Wavelengths: {wavelengths}")
        
    def _load_image_cube(self, image_paths):
        """
        각 band의 이미지 경로 리스트를 받아서 3D cube로 로드합니다.
        
        Args:
            image_paths: 각 band의 이미지 경로 리스트
            
        Returns:
            numpy.ndarray: (height, width, channels) 형태의 이미지 cube
        """
        if not image_paths:
            raise ValueError("Image paths list is empty")

        # wavelengths 수와 image_paths 길이 일치 확인
        wavelengths = self.column_config.get('wavelengths', [])
        if len(image_paths) != len(wavelengths):
            raise ValueError(f"Number of image paths ({len(image_paths)}) must match number of wavelengths ({len(wavelengths)})")

        band_arrays = []
        for path in image_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Image file not found: {path}")
            img = Image.open(path).convert("L")

            # 학습 해상도와 맞추기
            if self.target_hw and img.size[::-1] != self.target_hw:  # PIL: (W,H)
                img = img.resize(self.target_hw[::-1], resample=Image.NEAREST)

            band_arrays.append(np.asarray(img, dtype=np.float32))

        image_cube = np.stack(band_arrays, axis=-1)  # (H, W, C)

        # 학습 시 사용한 /255 정규화 반영
        if self.scaler_mode == "normalized":
            image_cube /= 255.0

        return image_cube
        
    def _preprocess_image(self, image_cube, crop_size=(224, 224)):
        """
        이미지 cube를 전처리합니다.
        
        Args:
            image_cube: (height, width, channels) 형태의 이미지 cube
            crop_size: 크롭할 크기 (height, width)
            
        Returns:
            torch.Tensor: (1, channels, height, width) 형태의 텐서
        """
        # 1. cube (H,W,C) → tensor (C,H,W) 변환
        image_tensor = torch.from_numpy(image_cube).permute(2, 0, 1).float()
        
        # 2. StandardScaler 정규화 (있는 경우) - 학습 파이프라인과 동일한 순서
        if self.scaler is not None:
            # scaler의 mean_와 scale_를 사용하여 정규화
            mean_tensor = torch.as_tensor(self.scaler.mean_, dtype=torch.float32).view(-1, 1, 1)
            scale_tensor = torch.as_tensor(self.scaler.scale_, dtype=torch.float32).view(-1, 1, 1)
            
            # 0으로 나누기 방지
            eps = 1e-6
            scale_tensor = torch.clamp(scale_tensor, min=eps)
            
            image_tensor = (image_tensor - mean_tensor) / scale_tensor
        
        # 3. 중앙 크롭 적용 - 학습 파이프라인과 동일한 순서
        transform = get_test_transforms(image_size=crop_size)
        image_tensor = transform(image_tensor)
        
        # 4. 배치 차원 추가 (1, C, H, W)
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor.to(self.device)
        
    def predict(self, image_paths, crop_size=None, *, xai: bool = False, xai_layer: Optional[str] = None, xai_index: Optional[int] = None, xai_save_dir: Optional[str] = None):
        """
        이미지 경로 리스트를 받아서 예측을 수행합니다.
        
        Args:
            image_paths: 각 band의 이미지 경로 리스트
            crop_size: 크롭할 크기 (height, width), None이면 config에서 가져옴
            xai: Grad-CAM 생성 여부
            xai_layer: CAM 타깃 레이어 dotted-path (None이면 마지막 Conv 자동)
            xai_index: CAM 타깃 인덱스(분류: 클래스, 회귀: 타깃). None이면 자동 선택

        Returns:
            dict: 예측 결과 (JSON 직렬화 가능)
        """
        if crop_size is None:
            crop_size = self.crop_size

        # 이미지 cube 로드
        image_cube = self._load_image_cube(image_paths)
        print(f"Predicting on cube {image_cube.shape}, crop_size={crop_size}, device={self.device}")

        # 전처리
        image_tensor = self._preprocess_image(image_cube, crop_size)
        print(f"Preprocessed tensor shape: {image_tensor.shape}")

        # 예측 수행
        with torch.no_grad():
            outputs = self.model(image_tensor)

        # 결과 처리
        results = {}

        if isinstance(outputs, dict):
            # 멀티태스크 출력
            if 'classification' in outputs and self.cls_indices:
                cls_output = outputs['classification']
                cls_probs = torch.sigmoid(cls_output).squeeze().cpu().numpy()
                cls_results = [float(cls_probs[i]) for i in self.cls_indices]
                results['classification'] = cls_results

            if 'regression' in outputs and self.reg_indices:
                reg_output = outputs['regression']
                reg_values = reg_output.squeeze().cpu().numpy()
                reg_results = [float(reg_values[i]) for i in self.reg_indices]
                results['regression'] = reg_results

        else:
            # 단일 출력
            output_values = outputs.squeeze().cpu().numpy()

            if self.cls_indices and not self.reg_indices:
                # 분류만
                cls_probs = torch.sigmoid(outputs).squeeze().cpu().numpy()
                cls_results = [float(cls_probs[i]) for i in self.cls_indices]
                results['classification'] = cls_results

            elif self.reg_indices and not self.cls_indices:
                # 회귀만
                reg_results = [float(output_values[i]) for i in self.reg_indices]
                results['regression'] = reg_results

            else:
                # 분류+회귀가 한 텐서에 함께 있는 비표준 케이스 가정
                if len(output_values) >= len(self.cls_indices) + len(self.reg_indices):
                    if self.cls_indices:
                        cls_output = outputs.squeeze()[:len(self.cls_indices)]
                        cls_probs = torch.sigmoid(cls_output).cpu().numpy()
                        cls_results = [float(cls_probs[i]) for i in range(len(self.cls_indices))]
                        results['classification'] = cls_results

                    if self.reg_indices:
                        reg_start = len(self.cls_indices)
                        reg_values = output_values[reg_start:reg_start + len(self.reg_indices)]
                        reg_results = [float(reg_values[i]) for i in range(len(self.reg_indices))]
                        results['regression'] = reg_results

        # XAI 부분
        if xai:
            # task 결정(분류 우선, 불명확하면 infer)
            if isinstance(outputs, dict):
                if 'classification' in outputs:
                    task_to_cam = 'classification'
                elif 'regression' in outputs:
                    task_to_cam = 'regression'
                else:
                    task_to_cam = _infer_task_from_outputs(outputs)
            else:
                task_to_cam = 'classification' if (outputs.ndim == 2 and outputs.shape[1] > 1) else 'regression'

            wavelengths   = self.column_config.get('wavelengths', None)
            label_columns = self.column_config.get('label_columns', [])
            lt            = self.column_config.get('label_types', {})

            # ---------- [A] 멀티라벨 분류 ----------
            if ( (isinstance(outputs, dict) and 'classification' in outputs) or
                (not isinstance(outputs, dict) and task_to_cam == 'classification') ):
                
                # outputs 형태에 맞춰 cls_out 준비
                if isinstance(outputs, dict):
                    cls_out = outputs['classification']
                else:
                    cls_out = outputs  # 단일 텐서(멀티클래스/멀티라벨)

                # 클래스 개수
                C = int(cls_out.shape[1]) if cls_out.ndim == 2 else int(cls_out.numel())

                # 라벨명 순서: label_types['classification'] 우선 → 길이 안 맞으면 self.cls_indices 기반 fallback
                cls_labels_order = list(lt.get('classification', [])) if isinstance(lt.get('classification', []), list) else []
                if len(cls_labels_order) != C:
                    cls_labels_order = []
                    for i in range(C):
                        if i < len(getattr(self, 'cls_indices', [])):
                            gidx = self.cls_indices[i]
                            if 0 <= gidx < len(label_columns):
                                cls_labels_order.append(label_columns[gidx])
                            else:
                                cls_labels_order.append(None)
                        else:
                            cls_labels_order.append(None)

                # 예측 확률 매핑 (라벨명 → 확률)
                pred_by_label = {}
                if 'classification' in results and isinstance(results['classification'], list):
                    cls_preds = results['classification']
                    lt_cls = list(lt.get('classification', [])) if isinstance(lt.get('classification', []), list) else []
                    if len(lt_cls) == len(cls_preds) and len(lt_cls) > 0:
                        for name, val in zip(lt_cls, cls_preds):
                            pred_by_label[name] = val
                    else:
                        for i, val in enumerate(cls_preds):
                            if i < len(getattr(self, 'cls_indices', [])):
                                gidx = self.cls_indices[i]
                                if 0 <= gidx < len(label_columns):
                                    pred_by_label[label_columns[gidx]] = val

                xai_items = []
                for ci in range(C):
                    cam_pack = generate_cam_arrays(
                        model=self.model,
                        image_tensor_bchw=image_tensor,
                        outputs=outputs,              # tensor/dict 모두 지원
                        task='classification',
                        target_index=ci,              # ★ 각 클래스별 CAM
                        target_layer_name=None,
                        image_cube_hwc=image_cube,
                        wavelengths=wavelengths,
                        rgb_strategy='auto',
                        alpha=0.35
                    )
                    heatmap_png_bytes = cam_to_png_bytes(cam_pack['cam'])
                    heatmap_b64 = base64.b64encode(heatmap_png_bytes).decode("utf-8")

                    target_label = cls_labels_order[ci] if ci < len(cls_labels_order) else None
                    pred_value = float(pred_by_label[target_label]) if (target_label and target_label in pred_by_label) else None

                    # (선택) 파일 저장: --xai-save-dir 지정 시
                    if xai_save_dir:
                        def _safe_name(s): return "".join(c if c.isalnum() or c in ("-","_") else "_" for c in str(s))
                        base = f"class_{ci}" if target_label is None else f"class_{ci}_{_safe_name(target_label)}"
                        save_cam_arrays(cam=cam_pack['cam'], save_dir=xai_save_dir,
                                        basename=base, save_heatmap=True,
                                        save_rgb=False, save_overlay=False)

                    xai_items.append({
                        'task': 'classification',
                        'target_index': int(ci),
                        'target_label': target_label,
                        'pred': pred_value,
                        'layer': cam_pack['layer'],
                        'image_base64': heatmap_b64
                    })

                results['xai'] = {
                    'task': 'classification',
                    'mode': 'per_target',            
                    'items': xai_items
                }

            # ---------- [B] 멀티라벨 회귀 ----------
            elif (isinstance(outputs, dict) and 'regression' in outputs):
                reg_out = outputs['regression']
                R = int(reg_out.shape[1]) if reg_out.ndim == 2 else int(reg_out.numel())

                reg_labels_order = list(lt.get('regression', [])) if isinstance(lt.get('regression', []), list) else []
                if len(reg_labels_order) != R:
                    reg_labels_order = []
                    for i in range(R):
                        if i < len(getattr(self, 'reg_indices', [])):
                            gidx = self.reg_indices[i]
                            if 0 <= gidx < len(label_columns):
                                reg_labels_order.append(label_columns[gidx])
                            else:
                                reg_labels_order.append(None)
                        else:
                            reg_labels_order.append(None)

                pred_by_label = {}
                if 'regression' in results and isinstance(results['regression'], list):
                    reg_preds = results['regression']
                    lt_reg = list(lt.get('regression', [])) if isinstance(lt.get('regression', []), list) else []
                    if len(lt_reg) == len(reg_preds) and len(lt_reg) > 0:
                        for name, val in zip(lt_reg, reg_preds):
                            pred_by_label[name] = val
                    else:
                        for i, val in enumerate(reg_preds):
                            if i < len(getattr(self, 'reg_indices', [])):
                                gidx = self.reg_indices[i]
                                if 0 <= gidx < len(label_columns):
                                    pred_by_label[label_columns[gidx]] = val

                xai_items = []
                for ri in range(R):
                    cam_pack = generate_cam_arrays(
                        model=self.model,
                        image_tensor_bchw=image_tensor,
                        outputs=outputs,
                        task='regression',
                        target_index=ri,             
                        target_layer_name=None,
                        image_cube_hwc=image_cube,
                        wavelengths=wavelengths,
                        rgb_strategy='auto',
                        alpha=0.35
                    )
                    heatmap_png_bytes = cam_to_png_bytes(cam_pack['cam'])
                    heatmap_b64 = base64.b64encode(heatmap_png_bytes).decode("utf-8")

                    target_label = reg_labels_order[ri] if ri < len(reg_labels_order) else None
                    pred_value = None
                    if target_label is not None and target_label in pred_by_label:
                        pred_value = float(pred_by_label[target_label])

                    xai_items.append({
                        'task': 'regression',
                        'target_index': int(ri),
                        'target_label': target_label,
                        'pred': pred_value,
                        'layer': cam_pack['layer'],
                        'image_base64': heatmap_b64
                    })

                results['xai'] = {
                    'task': 'regression',
                    'mode': 'per_target',
                    'items': xai_items
                }

            # ---------- [C] 단일(분류/회귀) 케이스 ----------
            else:
                cam_pack = generate_cam_arrays(
                    model=self.model,
                    image_tensor_bchw=image_tensor,
                    outputs=outputs,
                    task=task_to_cam,
                    target_index=None,            # 내부에서 argmax(분류)/0번(회귀)
                    target_layer_name=None,
                    image_cube_hwc=image_cube,
                    wavelengths=wavelengths,
                    rgb_strategy='auto',
                    alpha=0.35
                )
                heatmap_png_bytes = cam_to_png_bytes(cam_pack['cam'])
                target_label = None
                try:
                    ti = int(cam_pack['target_index'])
                    if 0 <= ti < len(label_columns):
                        target_label = label_columns[ti]
                except Exception:
                    pass

                pred_value = None
                if 'regression' in results and isinstance(results['regression'], list):
                    pred_by_label = {}
                    lt_reg = list(lt.get('regression', [])) if isinstance(lt.get('regression', []), list) else []
                    if len(lt_reg) == len(results['regression']) and len(lt_reg) > 0:
                        for name, val in zip(lt_reg, results['regression']):
                            pred_by_label[name] = val
                    else:
                        for i, val in enumerate(results['regression']):
                            if i < len(getattr(self, 'reg_indices', [])):
                                gidx = self.reg_indices[i]
                                if 0 <= gidx < len(label_columns):
                                    pred_by_label[label_columns[gidx]] = val
                    if target_label is not None and target_label in pred_by_label:
                        pred_value = float(pred_by_label[target_label])

                results['xai'] = {
                    'task': cam_pack['task'],
                    'mode': 'single',
                    'items': [{
                        'task': cam_pack['task'],
                        'target_index': int(cam_pack['target_index']),
                        'target_label': target_label,
                        'pred': pred_value,
                        'layer': cam_pack['layer'],
                        'image_base64': base64.b64encode(heatmap_png_bytes).decode("utf-8")
                    }]
                }

        return results


    def predict_batch(
        self,
        image_paths_list: List[List[str]],
        crop_size=None,
        *,
        xai: bool = False,
        xai_layer: Optional[str] = None,
        xai_index: Optional[int] = None,
    ):
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

        results = []

        for i, image_paths in enumerate(image_paths_list):
            print(f"Predicting batch {i+1}/{len(image_paths_list)}")
            try:
                result = self.predict(
                    image_paths, crop_size,
                    xai=xai, xai_layer=xai_layer, xai_index=xai_index,
                )
                results.append(result)
            except Exception as e:
                print(f"Error predicting batch {i+1}: {e}")
                results.append(None)

        return results


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
    parser.add_argument('--xai', action='store_true', help='Enable Grad-CAM')
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
        
        # 예측 수행
        results = predictor.predict(
            args.image_paths,
            tuple(args.crop_size) if args.crop_size else None,
            xai=args.xai,
            xai_save_dir=args.xai_save_dir,
        )

        # 결과 출력
        print("\n=== Prediction Results ===")
        if 'classification' in results:
            print("Classification probabilities:")
            for i, prob in enumerate(results['classification']):
                print(f"  Class {i}: {prob:.4f}")
                
        if 'regression' in results:
            print("Regression values:")
            for i, value in enumerate(results['regression']):
                print(f"  Target {i}: {value:.4f}")
                
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
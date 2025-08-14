#!/usr/bin/env python3
"""
RGB 예측 모듈 (학습 파이프라인과 완전 호환)

이 스크립트는 RGB best model을 로드하고 각 band의 image path 리스트를 입력받아 예측을 수행합니다.
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
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_model
from utils.transforms_rgb import get_test_transforms


class RGBPredictor:
    """RGB 예측을 위한 클래스 (학습 파이프라인과 완전 호환)"""

    def __init__(self, model_dir, device=None):
        """
        Args:
            model_dir: 모델 디렉토리 (best_model.pt, config.json, scaler.pkl 포함)
            device: 사용할 디바이스
        """
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None else device
        print(f"Using device: {self.device}")

        """
        config_path = os.path.join(model_dir, "configs", "temp_config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        print(f"Loaded config from: {config_path}")
        """

        # 아티팩트 로드
        self.config, self.column_config, self.model, self.scaler = self._build_artifacts(model_dir)
        self.model.eval()
        
        # 라벨 타입 정보 설정
        self._setup_label_info()
        
        # 모델 정보 출력
        self._print_model_info()
        
        # === 학습 파이프라인과 동일한 전처리를 위한 설정 ===
        self.target_hw   = tuple(self.column_config.get("image_size", [])) or None  # (H, W)
        self.image_size   = tuple(self.config.get("data", {}).get("image_size", [224, 224]))
        
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
        
        # 1. config 파일 로드
        config_path = os.path.join(model_dir, "configs", "temp_config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded config from: {config_path}")

        # 2. column_config 로드 (config['data']['column_config']에서 경로 가져오기)
        column_config_path = "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI/configs/column_config.json"
        column_config_path = config['data'].get('column_config', column_config_path)

        if not os.path.exists(column_config_path):
            raise FileNotFoundError(f"Column config file not found: {column_config_path}")
            
        with open(column_config_path, 'r') as f:
            column_config = json.load(f)
        print(f"Loaded column_config from: {column_config_path}")
            
        # 3. 모델 로드 (./models/best_model.pt)
        model_path = os.path.join(model_dir, "models", "best_model.pt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        print("Creating model architecture from config...")
        model = load_model(config)
        
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
        
        # 4. scaler 로드 (./scaler/temp_scaler.pkl)
        scaler = None
        scaler_path = os.path.join(model_dir, "scaler", "temp_scaler.pkl")
        if os.path.exists(scaler_path):
            print(f"Loading scaler from: {scaler_path}")
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
        else:
            raise ValueError(f"scaler_mode is '{self.scaler_mode}' but scaler not found at {scaler_path}")
            
        return config, column_config, model, scaler
        
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
            in_channels = self.config.get('model', {}).get('parameters', {}).get('in_channels', 3)
            if len(getattr(self.scaler, "mean_", [])) != in_channels:
                print(f"Warning: scaler.mean_ shape ({len(self.scaler.mean_)}) doesn't match input channels ({in_channels})")

    def _print_model_info(self):
        """모델 정보를 출력합니다."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"Model parameters: {total_params:,} total, {trainable_params:,} trainable")
        
        # 입력 채널 수 출력
        wavelengths = self.column_config.get('wavelengths', [])
        print(f"Input channels (wavelengths): {len(wavelengths)}")
        print(f"Wavelengths: {wavelengths}")
        
    def _load_image_cube(self, image_path):
        """
        RGB 이미지 경로 리스트를 받아서 3D cube로 로드합니다.
        
        Args:
            image_path: RBG 이미지 한 장의 경로
            
        Returns:
            numpy.ndarray: (height, width, channels) 형태의 이미지 cube
        """
        if not image_path:
            raise ValueError("Image paths list is empty")

        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        img = Image.open(image_path).convert("RGB")

        # 학습 해상도와 맞추기
        if self.target_hw and img.size[::-1] != self.target_hw:  # PIL: (W,H)
            img = img.resize(self.target_hw[::-1], resample=Image.BILINEAR)

        arr = np.asarray(img, dtype=np.float32)
        if self.scaler_mode == "normalized":
            arr /= 255.0

        return arr
        
    def _preprocess_image(self, image_cube, image_size=(224, 224)):
        """
        이미지 cube를 전처리합니다.
        HSI 이미지를 전처리 하는 방식과 동일.
        
        Args:
            image_cube: (height, width, channels) 형태의 이미지 cube
            image_size: 학습에서와 동일한 이미지 사이즈 사용
            
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
        transform = get_test_transforms(image_size=image_size)
        image_tensor = transform(image_tensor)
        
        # 4. 배치 차원 추가 (1, C, H, W)
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor.to(self.device)
        
    def predict(self, image_path, image_size=None):
        """
        이미지 경로 리스트를 받아서 예측을 수행합니다.
        
        Args:
            image_path: RGB 이미지 경로
            image_size: 학습에서와 동일한 이미지 크기 사용
            
        Returns:
            dict: 예측 결과 (JSON 직렬화 가능)
        """
        if image_size is None:
            image_size = self.image_size

        # 이미지 cube 로드
        image_cube = self._load_image_cube(image_path)
        print(f"Predicting on cube {image_cube.shape}, image_size={image_size}, device={self.device}")
        
        # 전처리
        image_tensor = self._preprocess_image(image_cube, image_size)
        print(f"Preprocessed tensor shape: {image_tensor.shape}")
        
        # 예측 수행
        with torch.no_grad():
            outputs = self.model(image_tensor)
            
        # 결과 처리 (torch.from_numpy 왕복 제거)
        results = {}
        
        if isinstance(outputs, dict):
            # 멀티태스크 출력인 경우
            if 'classification' in outputs and self.cls_indices:
                cls_output = outputs['classification']
                cls_probs = torch.sigmoid(cls_output).squeeze().cpu().numpy()
                # 분류 인덱스에 해당하는 값만 추출
                cls_results = [float(cls_probs[i]) for i in self.cls_indices]
                results['classification'] = cls_results
                
            if 'regression' in outputs and self.reg_indices:
                reg_output = outputs['regression']
                reg_values = reg_output.squeeze().cpu().numpy()
                # 회귀 인덱스에 해당하는 값만 추출
                reg_results = [float(reg_values[i]) for i in self.reg_indices]
                results['regression'] = reg_results
                
        else:
            # 단일 출력인 경우
            output_values = outputs.squeeze().cpu().numpy()
            
            if self.cls_indices and not self.reg_indices:
                # 분류만 있는 경우 - outputs 바로 sigmoid
                cls_probs = torch.sigmoid(outputs).squeeze().cpu().numpy()
                cls_results = [float(cls_probs[i]) for i in self.cls_indices]
                results['classification'] = cls_results
                
            elif self.reg_indices and not self.cls_indices:
                # 회귀만 있는 경우
                reg_results = [float(output_values[i]) for i in self.reg_indices]
                results['regression'] = reg_results
                
            else:
                # 둘 다 있는 경우 (출력이 분류+회귀 순서로 되어 있다고 가정)
                if len(output_values) >= len(self.cls_indices) + len(self.reg_indices):
                    # 분류 부분 - outputs 바로 sigmoid
                    if self.cls_indices:
                        cls_output = outputs.squeeze()[:len(self.cls_indices)]
                        cls_probs = torch.sigmoid(cls_output).cpu().numpy()
                        cls_results = [float(cls_probs[i]) for i in range(len(self.cls_indices))]
                        results['classification'] = cls_results
                        
                    # 회귀 부분
                    if self.reg_indices:
                        reg_start = len(self.cls_indices)
                        reg_values = output_values[reg_start:reg_start + len(self.reg_indices)]
                        reg_results = [float(reg_values[i]) for i in range(len(self.reg_indices))]
                        results['regression'] = reg_results
                        
        return results
        
    def predict_batch(self, image_paths_list, image_size=None):
        """
        여러 이미지 경로 리스트를 받아서 배치 예측을 수행합니다.
        
        Args:
            image_paths_list: 이미지 경로 리스트들의 리스트
            image_size: 학습에서와 동일한 이미지 크기 사용
            
        Returns:
            list: 예측 결과 리스트 (JSON 직렬화 가능)
        """
        if image_size is None:
            image_size = self.image_size

        results = []
        
        for i, image_paths in enumerate(image_paths_list):
            print(f"Predicting batch {i+1}/{len(image_paths_list)}")
            try:
                result = self.predict(image_paths, image_size)
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
    parser.add_argument('--image_size', nargs=2, type=int, default=None,
                       help='Crop size (height width), default from config')
    parser.add_argument('--output', type=str,
                       help='Output file path for results')
    
    args = parser.parse_args()
    
    # 모델 디렉토리 설정
    model_dir = args.model_dir
    temp_dir = None

    if args.run_id and args.experiment_id:
        # MLflow run_id와 experiment_id를 통해 아티팩트 직접 접근
        print(f"Loading artifacts from MLflow run: {args.run_id} (Experiment ID: {args.experiment_id})")

        # /mnt/data/mlflow_artifacts에서 run_id 찾기
        mlflow_artifacts_base = "/mnt/data/mlflow_artifacts"
        model_dir = None

        if os.path.exists(mlflow_artifacts_base):
            if os.path.exists(mlflow_artifacts_base):
                print(f"Searching for experiment_id and run_id in: {mlflow_artifacts_base}")
                experiment_path = os.path.join(mlflow_artifacts_base, args.experiment_id)
                if os.path.exists(experiment_path):
                    run_path = os.path.join(experiment_path, args.run_id)
                    if os.path.exists(run_path):
                        artifacts_path = os.path.join(run_path, "artifacts")
                        if os.path.exists(artifacts_path):
                            model_dir = artifacts_path
                            print(f"Found artifacts at: {artifacts_path}")

            if model_dir is None:
                raise FileNotFoundError(f"Run ID {args.run_id} not found in {mlflow_artifacts_base}")
        else:
            raise FileNotFoundError(f"MLflow artifacts directory not found: {mlflow_artifacts_base}")

    elif args.run_id:
        # MLflow run_id를 통해 아티팩트 직접 접근
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
        predictor = RGBPredictor(model_dir=model_dir)
        
        # 예측 수행
        results = predictor.predict(args.image_paths,
                                    tuple(args.image_size) if args.image_size else None)

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
#!/usr/bin/env python3
"""
RGB 예측 모듈 (학습 파이프라인과 완전 호환)

이 스크립트는 RGB best model을 로드하고 각 band의 image path 리스트를 입력받아 예측을 수행합니다.
학습 파이프라인과 완전히 호환되도록 설계되었습니다.

사용법:
    # 방법 1: 로컬 모델 디렉토리 사용
    python predict_rgb.py --model_dir /path/to/model_dir --image_paths /path/to/band1.png /path/to/band2.png ...
    
    # 방법 2: MLflow run ID 사용
    python predict_rgb.py --run_id <mlflow_run_id> --experiment_id <experiment_id> --image_paths /path/to/band1.png /path/to/band2.png ...
"""

import os
import sys
import json
import argparse
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.model_loader import load_model
from utils.transforms_rgb import get_test_transforms


class InferenceDataset(Dataset):
    def __init__(self, image_paths, image_size):
        self.image_paths = image_paths
        self.transform = get_test_transforms(image_size=image_size)

    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        path = self.image_paths[idx]
        if not os.path.exists(path):
            raise FileNotFoundError(f"Image not found: {path}")
        img = Image.open(path).convert("RGB")
        return self.transform(img)  # (C,H,W)


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

        # 아티팩트 로드
        self.config, self.column_config, self.model = self._build_artifacts(model_dir)
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
            tuple: (config, column_config, model)
            RGB에서는 HSI에서와 달리 scaler가 없음.
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory를 찾을 수 없습니다: {model_dir}")
        print(f"Loading artifacts from MLflow directory: {model_dir}")
        
        # 1. config 파일 로드
        config_path = os.path.join(model_dir, "configs", "temp_rgb_config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file을 찾을 수 없습니다: {config_path}")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded config from: {config_path}")

        # 2. column_config 로드 (config['data']['column_config']에서 경로 가져오기)
        column_config_path = "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI/configs/column_config.json"
        column_config_path = config['data'].get('column_config', column_config_path)

        if not os.path.exists(column_config_path):
            raise FileNotFoundError(f"Column config file을 찾을 수 없습니다: {column_config_path}")
            
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

        return config, column_config, model

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

    def _print_model_info(self):
        """모델 정보를 출력합니다."""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        print(f"Model parameters: {total_params:,} total, {trainable_params:,} trainable")
        
        # 입력 채널 수 출력
        wavelengths = self.column_config.get('wavelengths', [])
        print(f"Input channels (wavelengths): {len(wavelengths)}")
        print(f"Wavelengths: {wavelengths}")
        
    def predict_batch(self, image_paths_list, image_size=None, batch_size=32):
        """
        여러 이미지 경로 리스트를 받아서 배치 예측을 수행합니다.
        
        Args:
            image_paths_list: 이미지 경로 리스트들의 리스트
            image_size: 학습에서와 동일한 이미지 크기 사용
            
        Returns:
            list: 예측 결과 리스트 (JSON 직렬화 가능)
        """
        if image_size == None:
            image_size = self.image_size

        dataset = InferenceDataset(image_paths_list, image_size=image_size)
        batch_size = min(len(image_paths_list), batch_size)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        all_preds = {}
        sample_idx = 0
        
        with torch.no_grad():
            for batch in loader:
                batch = batch.to(self.device)
                outputs = self.model(batch)

                for output in outputs:
                    sample_results = {}
                    if isinstance(output, dict):
                        # 멀티태스크 출력인 경우
                        if 'classification' in output and self.cls_indices:
                            cls_output = output['classification']
                            cls_probs = torch.sigmoid(cls_output).cpu().numpy()
                            # 분류 인덱스에 해당하는 값만 추출
                            cls_results = {}
                            for idx, cls_idx in enumerate(self.cls_indices):
                                    cls_results[self.label_columns[cls_idx]] = float(cls_probs[idx])
                            sample_results['classification'] = cls_results
                        if 'regression' in output and self.reg_indices:
                            reg_output = output['regression']
                            reg_values = reg_output.squeeze().cpu().numpy()
                            # 회귀 인덱스에 해당하는 값만 추출
                            reg_results = {}
                            for idx, reg_idx in enumerate(self.reg_indices):
                                    reg_results[self.label_columns[reg_idx]] = float(reg_values[idx])
                            sample_results['regression'] = reg_results
                    
                    else:
                        # 단일 출력인 경우
                        output_values = output.squeeze().cpu().numpy()

                        if self.cls_indices and not self.reg_indices:
                            # 분류만 있는 경우 - output에 바로 sigmoid 적용
                            cls_probs = torch.sigmoid(output).squeeze().cpu().numpy()
                            cls_results = {}
                            for idx, cls_idx in enumerate(self.cls_indices):
                                    cls_results[self.label_columns[cls_idx]] = float(cls_probs[idx])
                            sample_results['classification'] = cls_results

                        elif not self.cls_indices and self.reg_indices:
                            # 회귀만 있는 경우
                            reg_results = {}
                            for idx, reg_idx in enumerate(self.reg_indices):
                                reg_results[self.label_columns[reg_idx]] = float(output_values[idx])
                            sample_results['regression'] = reg_results
                        
                        else:
                            # 둘 다 있는 경우
                            if self.cls_indices[0] <= self.reg_indices[0]:
                                # 분류 -> 회귀 순서로 되어 있는 경우
                                if self.cls_indices:
                                    cls_outputs = output.squeeze()[:len(self.cls_indices)]
                                    cls_probs = torch.sigmoid(cls_outputs).cpu().numpy()
                                    cls_results = {}
                                    for idx, cls_idx in enumerate(self.cls_indices):
                                        cls_results[self.label_columns[cls_idx]] = float(cls_probs[idx])
                                    sample_results['classification'] = cls_results
                            
                                if self.reg_indices:
                                    reg_start = len(self.cls_indices)
                                    reg_values = output_values[reg_start:reg_start + len(self.reg_indices)]
                                    reg_results = {}
                                    for idx, reg_idx in enumerate(self.reg_indices):
                                        reg_results[self.label_columns[reg_idx]] = float(reg_values[idx])
                                    sample_results['regression'] = reg_results

                            else:
                                # 회귀 -> 분류 순서로 되어 있는 경우
                                if self.reg_indices:
                                    reg_values = output_values[:len(self.reg_indices)]
                                    reg_results = {}
                                    for idx, reg_idx in enumerate(self.reg_indices):
                                        reg_results[self.label_columns[reg_idx]] = float(reg_values[idx])
                                    sample_results['regression'] = reg_results
                                
                                if self.cls_indices:
                                    cls_start = len(self.reg_indices)
                                    cls_outputs = output.squeeze()[cls_start:cls_start + len(self.cls_indices)]
                                    cls_probs = torch.sigmoid(cls_outputs).cpu().numpy()
                                    cls_results = {}
                                    for idx, cls_idx in enumerate(self.cls_indices):
                                        cls_results[self.label_columns[cls_idx]] = float(cls_probs[idx])
                                    sample_results['classification'] = cls_results

                    sample_name = os.path.basename(image_paths_list[sample_idx])
                    all_preds[sample_name] = sample_results
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
        
        # # 예측 수행
        results = predictor.predict_batch(args.image_paths,
                                          tuple(args.image_size) if args.image_size else None)

        # 결과 출력
        for key, result in results.items():
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
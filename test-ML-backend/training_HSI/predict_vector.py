#!/usr/bin/env python3
"""
HSI 예측 모듈 (학습 파이프라인과 완전 호환)

이 스크립트는 HSI best model을 로드하고 각 band의 image path 리스트를 입력받아 예측을 수행합니다.
학습 파이프라인과 완전히 호환되도록 설계되었습니다.

사용법:
    python predict_hsi.py --model_dir /path/to/model_dir --image_paths /path/to/band1.png /path/to/band2.png ...
"""

import os
import sys
import json
import argparse
import torch
import numpy as np
from PIL import Image
import pickle
import joblib
import mlflow
import tempfile
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class VectorPredictor:

    def __init__(self, model_dir):
        
        self.model, self.config, self.column_config = self._build_artifacts(model_dir)

        self._setup_label_info()

        self._print_model_info()

    def _build_artifacts(self, model_dir):
        """
        모델 디렉토리에서 아티팩트들을 로드합니다.
        
        Args:
            model_dir: 모델 디렉토리 경로
            
        Returns:
            tuple: (model, config, column_config)
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        print(f"Loading artifacts from: {model_dir}")
        
        # 1. config.json 로드
        config_path = os.path.join(model_dir, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        # 2. column_config.json 로드
        column_config_path = config['data']['column_config']
        if not os.path.isabs(column_config_path):
            # model_dir 기준과 프로젝트 루트 모두 시도
            possible_paths = [
                os.path.join(model_dir, column_config_path),
                os.path.join(os.path.dirname(model_dir), column_config_path)
            ]
            column_config_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    column_config_path = path
                    break
            if column_config_path is None:
                raise FileNotFoundError(f"Column config file not found in any of: {possible_paths}")
        if not os.path.exists(column_config_path):
            raise FileNotFoundError(f"Column config file not found: {column_config_path}")
            
        with open(column_config_path, 'r') as f:
            column_config = json.load(f)
            
        # 3. 모델 아키텍처 생성 및 state_dict 로드
        print("Creating model architecture from config...")

        # best_model.pkl 로드
        model_path = os.path.join(model_dir, "best_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
            
        print(f"Loading sklearn model from: {model_path}")
        model = joblib.load(model_path)
            
        return model, config, column_config

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

    def _print_model_info(self):
        """모델 정보를 출력합니다."""
        print("Model architecture:")
        print(self.model)

        # 입력 채널 수 출력
        wavelengths = self.column_config.get('wavelengths', [])
        print(f"Input channels (wavelengths): {len(wavelengths)}")
        print(f"Wavelengths: {wavelengths}")

    def _sigmoid(self, x):
        """Sigmoid 함수"""
        return 1 / (1 + np.exp(-x))

    def predict(self, data_paths, crop_size=None):
        """
        데이터 경로 리스트를 받아서 예측을 수행합니다.
        
        Args:
            image_paths: 각 band의 이미지 경로 리스트
            crop_size: 크롭할 크기 (height, width), None이면 config에서 가져옴
            
        Returns:
            dict: 예측 결과 (JSON 직렬화 가능)
        """
        if crop_size is None:
            crop_size = self.crop_size

        # 이미지 cube 로드
        vector = self._load_vector_data(data_paths)
        print(f"Predicting on vector {vector.shape}")
        
        # 예측 수행
        y_pred = self.model.predict(vector)
        if hasattr(self.model, 'predict_proba'):
            y_preds = self.model.predict_proba(vector)
            
        # 결과 처리 (torch.from_numpy 왕복 제거)
        results = {}

        if self.cls_indices:
            # 분류 인덱스에 해당하는 예측만 추출
            if hasattr(self.model, 'predict_proba'):
                cls_probs = y_preds[:, self.cls_indices]
            else:
                cls_preds = y_pred[self.cls_indices]
                cls_probs = self._sigmoid(cls_preds)
            cls_results = [float(cls_probs[i]) for i in range(len(self.cls_indices))]
            results['classification'] = cls_results

        if self.reg_indices:
            # 회귀 인덱스에 해당하는 예측만 추출
            reg_results = [float(y_pred[i]) for i in self.reg_indices]
            results['regression'] = reg_results
                        
        return results
    
    def _load_vector_data(self, data_paths):
        if not data_paths:
            raise ValueError("Data paths list is empty")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='HSI Prediction (Learning Pipeline Compatible)')
    
    model_group = parser.add_mutually_exclusive_group(required=True)
    model_group.add_argument('--model_dir', type=str,
                           help='Model directory containing best_model.pt, config.json')
    
    model_group.add_argument('--run_id', type=str,
                           help='MLflow run ID to download artifacts from')
    
    parser.add_argument('--data_paths', nargs='+', required=True,
                       help='Paths to band datasets')
    
    parser.add_argument('--output', type=str,
                       help='Output file path for results')
    
    args = parser.parse_args()
    
    # 모델 디렉토리 설정
    model_dir = args.model_dir
    temp_dir = None
    
    if args.run_id:
        # MLflow run_id에서 아티팩트 다운로드
        print(f"Downloading artifacts from MLflow run: {args.run_id}")
        temp_dir = mlflow.artifacts.download_artifacts(run_id=args.run_id)
        model_dir = temp_dir
        print(f"Artifacts downloaded to: {model_dir}")
    
    # 예측기 생성
    try:
        predictor = VectorPredictor(model_dir=model_dir)
        
        # 예측 수행
        results = predictor.predict(args.data_paths)

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
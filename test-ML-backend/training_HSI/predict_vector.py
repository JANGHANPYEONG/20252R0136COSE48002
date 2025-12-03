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
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class VectorPredictor:

    def __init__(self, model_dir):
        
        # config 먼저 열어 필요한 정보 확보
        cfg_path = os.path.join(model_dir, "configs", "temp_config.json")
        with open(cfg_path, 'r') as _f:
            _cfg_tmp = json.load(_f)
        
        self.model, self.config, self.column_config = self._build_artifacts(model_dir)

        self._setup_label_info()

        self._print_model_info()
        
        # Vector는 crop_size가 필요 없지만 호환성을 위해 추가
        self.crop_size = None

    def _build_artifacts(self, model_dir):
        """
        MLflow artifacts 디렉토리에서 아티팩트들을 로드합니다.
        
        Args:
            model_dir: MLflow artifacts 디렉토리 경로 
                      (/mnt/data/mlflow_artifacts/experiment_id/run_id/artifacts)
            
        Returns:
            tuple: (model, config, column_config)
        """
        if not os.path.exists(model_dir):
            raise FileNotFoundError(f"Model directory not found: {model_dir}")
            
        print(f"Loading artifacts from MLflow directory: {model_dir}")
        
        # 1. config 로드 (./configs/temp_config.json)
        config_path = os.path.join(model_dir, "configs", "temp_config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Loaded config from: {config_path}")

        # 2. column_config 로드 (config['data']['column_config']에서 경로 가져오기)
        column_config_path = config['data'].get('column_config',
                                                "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI/configs/column_config.json")
            
        if not os.path.exists(column_config_path):
            raise FileNotFoundError(f"Column config file not found: {column_config_path}")
            
        with open(column_config_path, 'r') as f:
            column_config = json.load(f)
        print(f"Loaded column_config from: {column_config_path}")
            
        # 3. 모델 로드 (./models/best_model.pkl)
        model_path = os.path.join(model_dir, "models", "best_model.pkl")
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
            data_paths: 벡터 데이터 경로 리스트
            crop_size: 사용하지 않음 (호환성을 위해 유지)
            
        Returns:
            dict: 예측 결과 (JSON 직렬화 가능)
        """
        # 벡터 데이터 로드
        vector = self._load_vector_data(data_paths)
        print(f"Predicting on vector {vector.shape}")
        
        # 예측 수행
        y_pred = self.model.predict(vector)
        
        # 분류 모델인 경우 확률 예측도 수행
        y_proba = None
        if hasattr(self.model, 'predict_proba'):
            y_proba = self.model.predict_proba(vector)
            
        # 결과 처리
        results = {}

        if self.cls_indices:
            # 분류 인덱스에 해당하는 예측만 추출
            if y_proba is not None:
                # 확률 예측이 가능한 경우
                if len(y_proba.shape) > 1 and y_proba.shape[1] > 1:
                    # 다중 클래스: 각 클래스별 확률
                    cls_results = []
                    for i, cls_idx in enumerate(self.cls_indices):
                        if cls_idx < y_proba.shape[1]:
                            cls_results.append(float(y_proba[0, cls_idx]))
                        else:
                            cls_results.append(0.0)
                else:
                    # 이진 분류: sigmoid 적용
                    cls_proba = y_proba[0] if len(y_proba.shape) > 0 else y_proba
                    cls_results = [float(cls_proba) for _ in self.cls_indices]
            else:
                # 확률 예측이 불가능한 경우: 하드 예측에 sigmoid 적용
                cls_results = []
                for i, cls_idx in enumerate(self.cls_indices):
                    if cls_idx < len(y_pred):
                        cls_val = float(y_pred[cls_idx])
                        cls_prob = self._sigmoid(cls_val)
                        cls_results.append(cls_prob)
                    else:
                        cls_results.append(0.0)
            
            results['classification'] = cls_results

        if self.reg_indices:
            # 회귀 인덱스에 해당하는 예측만 추출
            reg_results = []
            for i, reg_idx in enumerate(self.reg_indices):
                if reg_idx < len(y_pred):
                    reg_results.append(float(y_pred[reg_idx]))
                else:
                    reg_results.append(0.0)
            results['regression'] = reg_results
                        
        return results
    
    def _load_vector_data(self, data_paths):
        """
        벡터 데이터를 로드합니다.
        
        Args:
            data_paths: 데이터 경로 리스트
            
        Returns:
            numpy.ndarray: 벡터 데이터
        """
        if not data_paths:
            raise ValueError("Data paths list is empty")
        
        # 단일 CSV 파일에서 벡터 데이터 로드
        import pandas as pd
        
        # 첫 번째 경로를 사용 (벡터 데이터는 보통 단일 파일)
        data_path = data_paths[0]
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"Data file not found: {data_path}")
        
        # CSV 파일 로드
        df = pd.read_csv(data_path)
        
        # wavelengths에 해당하는 컬럼들만 추출
        wavelengths = self.column_config.get('wavelengths', [])
        spectral_columns = [str(w) for w in wavelengths]
        
        # 스펙트럼 데이터만 추출
        if all(col in df.columns for col in spectral_columns):
            vector_data = df[spectral_columns].values
        else:
            # wavelength 컬럼이 없으면 숫자 컬럼들을 사용
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            vector_data = df[numeric_columns].values
        
        print(f"Loaded vector data shape: {vector_data.shape}")
        return vector_data


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
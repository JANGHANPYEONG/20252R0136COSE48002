"""
HSI/RGB 전반 실험을 위한 공통 MLflow 로깅 도우미.

실험 생성·연결, 파라미터/메트릭 기록, 곡선 시각화 저장까지 처리한다.
"""

import os
import json
import mlflow
import mlflow.pytorch
import mlflow.sklearn
from typing import Dict, Any, Optional, List
import torch
import numpy as np
from datetime import datetime
from mlflow.tracking import MlflowClient

# 헤드리스 안전을 위한 matplotlib 백엔드 고정
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


class MLflowLogger:
    """MLflow 로깅을 위한 클래스"""
    
    def __init__(self, tracking_uri: str, experiment_name: str):
        """
        Args:
            tracking_uri: MLflow tracking URI
            experiment_name: 실험 이름
        """
        self.tracking_uri = tracking_uri
        self.experiment_name = experiment_name
        self.run_id = None
        self.experiment_id = None
        self.client = MlflowClient()
        
        # MLflow 설정
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
    
    def start_run(self, experiment_id: Optional[str] = None, run_id: Optional[str] = None):
        """MLflow run을 시작합니다."""
        if run_id is not None:
            mlflow.start_run(run_id=run_id)
            self.run_id = run_id

            # 실제 experiment_id를 조회하여 검증/설정
            run_info = mlflow.get_run(run_id).info
            self.experiment_id = run_info.experiment_id

            if experiment_id is not None and str(self.experiment_id) != str(experiment_id):
                mlflow.end_run()
                self.run_id = None
                self.experiment_id = None
                raise ValueError(
                    f"Provided experiment_id {experiment_id} does not match run's experiment_id {self.experiment_id}"
                )

            print(f"Mlflow attached: run_id={self.run_id}, experiment_id={self.experiment_id})")
            return

        if experiment_id is None:
        # experiment_name 으로 선택/생성
            exp = mlflow.set_experiment(self.experiment_name)  # Experiment 객체 반환
            experiment_id = exp.experiment_id
        else:
            # 주어진 experiment_id가 유효한지(선택적으로) 확인
            exp = self.client.get_experiment(str(experiment_id))
            if exp is None:
                raise ValueError(f"Experiment id {experiment_id} not found")

        # experiment_id 아래 새 run 생성
        run = mlflow.start_run(experiment_id=str(experiment_id))
        self.run_id = run.info.run_id
        self.experiment_id = run.info.experiment_id

        print(f"MLflow STARTED: run_id={self.run_id}, experiment_id={self.experiment_id}")

    def end_run(self):
        """MLflow run을 종료합니다."""
        if mlflow.active_run():
            mlflow.end_run()
            print("MLflow run ended")
    
    def log_params(self, params: Dict[str, Any]):
        """하이퍼파라미터를 로깅합니다."""
        mlflow.log_params(params)
        print(f"Logged parameters: {list(params.keys())}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """메트릭을 로깅합니다."""
        mlflow.log_metrics(metrics, step=step)
        if step is not None:
            print(f"Step {step} - Logged metrics: {list(metrics.keys())}")
        else:
            print(f"Logged metrics: {list(metrics.keys())}")
    
    def log_model(self, model: torch.nn.Module, model_name: str = "hsi_2d_cnn"):
        """모델을 로깅합니다."""
        mlflow.pytorch.log_model(model, model_name)
        print(f"Model logged: {model_name}")

    def log_model_ml(self, model: Any, model_name: str = "hsi_vector"):
        mlflow.sklearn.log_model(model, model_name)
        print(f"Model logged: {model_name}")
    
    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None):
        """아티팩트를 로깅합니다."""
        mlflow.log_artifact(local_path, artifact_path)
        print(f"Artifact logged: {local_path}")
    
    def log_config(self, config: Dict[str, Any], config_name: str = "config.json"):
        """설정 파일을 로깅합니다."""
        # 임시 파일로 저장 후 로깅
        temp_path = f"temp_{config_name}"
        with open(temp_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        mlflow.log_artifact(temp_path, "configs")
        os.remove(temp_path)  # 임시 파일 삭제
        print(f"Config logged: configs/{config_name}")
    
    def log_scaler(self, scaler, scaler_name: str = "scaler.pkl"):
        """StandardScaler를 로깅합니다."""
        import pickle
        
        temp_path = f"temp_{scaler_name}"
        with open(temp_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        mlflow.log_artifact(temp_path, artifact_path="scaler")
        os.remove(temp_path)
        print(f"Scaler logged: scaler/{scaler_name}")
    
    def log_training_curve(self, train_losses: list, val_losses: list, 
                          train_metrics: Dict[str, list], val_metrics: Dict[str, list],
                          plot_keys: Optional[List[str]] = None):
        """훈련 곡선을 로깅합니다."""
        
        # 기본 플롯 키 설정
        if plot_keys is None:
            plot_keys = ["cls_f1_score", "reg_r2", "combined_score"]
        
        # 실제 존재하는 키만 필터링
        available_keys = [key for key in plot_keys if key in train_metrics and key in val_metrics]
        if not available_keys:
            # 대체 키들
            available_keys = list(train_metrics.keys())[:3]
        
        # 서브플롯 수 계산
        num_plots = min(len(available_keys) + 1, 4)  # 손실 + 메트릭 (최대 4개)
        
        plt.figure(figsize=(12, 8))
        
        # 손실 곡선 (항상 첫 번째)
        plt.subplot(2, 2, 1)
        plt.plot(train_losses, label='Train Loss')
        plt.plot(val_losses, label='Val Loss')
        plt.title('Loss Curve')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True)
        
        # 메트릭 서브플롯들
        for i, metric_name in enumerate(available_keys[:3]):  # 최대 3개 메트릭
            plt.subplot(2, 2, i + 2)
            plt.plot(train_metrics[metric_name], label=f'Train {metric_name}')
            plt.plot(val_metrics[metric_name], label=f'Val {metric_name}')
            plt.title(f'{metric_name} Curve')
            plt.xlabel('Epoch')
            plt.ylabel(metric_name)
            plt.legend()
            plt.grid(True)
        
        plt.tight_layout()
        
        # 임시 파일로 저장 후 로깅
        temp_path = "training_curves.png"
        plt.savefig(temp_path, dpi=300, bbox_inches='tight')
        mlflow.log_artifact(temp_path, artifact_path="training_curves")
        plt.close()
        os.remove(temp_path)
        
        print(f"Training curves logged with metrics: {available_keys}")
    
    def get_run_id(self) -> Optional[str]:
        """현재 run ID를 반환합니다."""
        return self.run_id
    
    def get_experiment_id(self) -> Optional[str]:
        """현재 experiment ID를 반환합니다."""
        if mlflow.active_run():
            return mlflow.active_run().info.experiment_id
        return None
    
    def log_dict_metrics(self, to_json):
        mlflow.log_dict(to_json,
                        artifact_file='final_metrics.json')


def create_logger(config: Dict[str, Any]) -> MLflowLogger:
    """설정에서 로거를 생성합니다."""
    mlflow_config = config.get('mlflow', {})
    tracking_uri = mlflow_config.get('tracking_uri', 'http://3.38.117.43:5000')
    experiment_name = mlflow_config.get('experiment_name', 'Deeplant_ML_training')
    
    return MLflowLogger(tracking_uri, experiment_name)


def log_training_summary(logger: MLflowLogger, config: Dict[str, Any], 
                        final_metrics: Dict[str, float], training_time: float):
    """훈련 요약을 로깅합니다."""
    # 최종 메트릭 로깅
    logger.log_metrics(final_metrics)
    
    # 훈련 시간 로깅
    logger.log_metrics({'training_time_minutes': training_time / 60})
    
    # 설정 로깅
    logger.log_config(config)
    
    print(f"Training completed in {training_time/60:.2f} minutes")
    print(f"Final metrics: {final_metrics}")

def log_training_ml_summary(logger: MLflowLogger, config: Dict[str, Any], 
                        final_metrics: Dict[str, float], training_time: float, to_json: Dict):
    """훈련 요약을 로깅합니다."""
    # 최종 메트릭 로깅
    logger.log_metrics(final_metrics)
    
    # 훈련 시간 로깅
    logger.log_metrics({'training_time_minutes': training_time / 60})
    
    # 설정 로깅
    logger.log_config(config)

    logger.log_dict_metrics(to_json)
    
    print(f"Training completed in {training_time/60:.2f} minutes")
    print(f"Final metrics: {final_metrics}")

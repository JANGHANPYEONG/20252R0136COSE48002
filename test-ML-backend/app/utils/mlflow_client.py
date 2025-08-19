"""
MLflow 클라이언트 모듈

실시간으로 MLflow에서 메트릭을 가져오는 기능을 제공합니다.
"""

import mlflow
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class MLflowMetricsClient:
    def __init__(self, tracking_uri: str = "http://3.38.117.43:5000"):
        """
        Args:
            tracking_uri: MLflow tracking 서버 URI
        """
        self.tracking_uri = tracking_uri
        mlflow.set_tracking_uri(tracking_uri)
        self.client = mlflow.tracking.MlflowClient()
    
    def get_run_metrics(self, run_id: str, after_step: int = 0) -> List[Dict[str, Any]]:
        """
        MLflow run에서 특정 step 이후의 메트릭을 가져옵니다.
        
        Args:
            run_id: MLflow run ID
            after_step: 이 step 이후의 메트릭만 가져옴
            
        Returns:
            메트릭 리스트
        """
        try:
            # run 정보 가져오기
            run = self.client.get_run(run_id)
            if not run:
                return []
            
            # 메트릭 히스토리 가져오기
            metrics_history = self.client.get_metric_history(run_id, "train_loss")
            
            # after_step 이후의 메트릭만 필터링
            filtered_metrics = []
            for metric in metrics_history:
                if metric.step > after_step:
                    # 모든 메트릭을 한 번에 가져오기
                    step_metrics = self._get_step_metrics(run_id, metric.step)
                    if step_metrics:
                        filtered_metrics.append(step_metrics)
            
            return filtered_metrics
            
        except Exception as e:
            print(f"Error getting MLflow metrics: {e}")
            return []
    
    def _get_step_metrics(self, run_id: str, step: int) -> Optional[Dict[str, Any]]:
        """
        특정 step의 모든 메트릭을 가져옵니다.
        """
        try:
            # 주요 메트릭들 가져오기
            metrics = {}
            
            # 기본 메트릭들
            metric_names = [
                "train_loss", "val_loss", "train_cls_f1_score", "val_cls_f1_score",
                "train_cls_auc", "val_cls_auc", "train_reg_r2", "val_reg_r2",
                "train_reg_mse", "val_reg_mse", "train_combined_score", "val_combined_score"
            ]
            
            for metric_name in metric_names:
                try:
                    history = self.client.get_metric_history(run_id, metric_name)
                    # 해당 step의 메트릭 찾기
                    for metric in history:
                        if metric.step == step:
                            metrics[metric_name] = metric.value
                            break
                except:
                    continue
            
            if metrics:
                metrics["step"] = step
                metrics["timestamp"] = datetime.now().isoformat()
                return metrics
            
            return None
            
        except Exception as e:
            print(f"Error getting step metrics: {e}")
            return None
    
    def get_run_status(self, run_id: str) -> str:
        """
        MLflow run의 상태를 확인합니다.
        
        Returns:
            "RUNNING", "FINISHED", "FAILED", "UNKNOWN"
        """
        try:
            run = self.client.get_run(run_id)
            if run:
                return run.info.status
            return "UNKNOWN"
        except Exception as e:
            print(f"Error getting run status: {e}")
            return "UNKNOWN"
    
    def get_latest_metrics(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        가장 최근 메트릭을 가져옵니다.
        """
        try:
            # 가장 최근 step 찾기
            history = self.client.get_metric_history(run_id, "train_loss")
            if not history:
                return None
            
            latest_step = max(metric.step for metric in history)
            return self._get_step_metrics(run_id, latest_step)
            
        except Exception as e:
            print(f"Error getting latest metrics: {e}")
            return None
    
    def is_run_active(self, run_id: str) -> bool:
        """
        run이 활성 상태인지 확인합니다.
        """
        status = self.get_run_status(run_id)
        return status == "RUNNING"


def get_mlflow_client() -> MLflowMetricsClient:
    """
    의존성 주입용 팩토리 함수
    """
    return MLflowMetricsClient()

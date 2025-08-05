from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Literal
import json
import tempfile
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult

from training_HSI.predict_hsi import main as predict_hsi
from training_HSI.predict_vector import main as predict_vector

# Celery 및 APIRouter 설정
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

router = APIRouter()


# Pydantic 모델 정의
class PredictRequest(BaseModel):
    model_uri: str  # MLflow run_id 또는 모델 디렉토리 경로
    data_path: str  # 예측할 데이터 경로
    input_type: Literal["image", "vector"]

class PredictResponse(BaseModel):
    message: str
    prediction_id: str
    process_pid: Optional[int] = None
    created_at: datetime

class PredictStatus(BaseModel):
    prediction_id: str
    status: Literal["PENDING", "PREDICTING", "SUCCESS", "FAILURE", "REVOKED"]
    progress: float
    elapsed_time: Optional[float] = None
    error_message: Optional[str] = None
    result: Optional[Dict] = None


# Celery 백그라운드에서 예측을 실행하는 함수
@celery_app.task(bind=True)
def run_prediction_task(self, model_uri: str, data_path: str, input_type: str):
    import time
    import os
    import sys
    
    try:
        # 현재 프로세스 PID 가져오기
        current_pid = os.getpid()
        
        # 시작 시간 기록
        start_time = time.time()
        
        # input_type 검증
        if input_type not in ["image", "vector"]:
            raise ValueError(f"Invalid input_type: {input_type}. Must be 'image' or 'vector'")
        
        # 예측 상태 업데이트: PREDICTING (PID 포함)
        self.update_state(state='PREDICTING', meta={
            'progress': 0.0,
            'elapsed_time': 0.0,
            'input_type': input_type,
            'process_pid': current_pid,
            'start_time': start_time
        })
        
        try:
            print(f"Starting prediction with model: {model_uri}, data: {data_path}")
            
            # sys.argv 백업
            original_argv = sys.argv
            
            # 예측 실행
            if input_type == "image":
                # HSI 이미지 예측
                if len(model_uri) == 32:  # MLflow run_id (32자리)
                    sys.argv = ['predict_hsi.py', '--run_id', model_uri, '--image_paths', data_path]
                else:
                    sys.argv = ['predict_hsi.py', '--model_dir', model_uri, '--image_paths', data_path]
                
                prediction_result = predict_hsi()
            else:
                # Vector 예측
                if len(model_uri) == 32:  # MLflow run_id (32자리)
                    sys.argv = ['predict_vector.py', '--run_id', model_uri, '--data_path', data_path]
                else:
                    sys.argv = ['predict_vector.py', '--model_dir', model_uri, '--data_path', data_path]
                
                prediction_result = predict_vector()
            
            print(f"Prediction completed successfully")
            
            # argv 복원
            sys.argv = original_argv
            
            # 완료 시간 계산
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 예측 완료 - SUCCESS 상태로 업데이트
            self.update_state(state='SUCCESS', meta={
                'progress': 1.0,
                'elapsed_time': elapsed_time
            })
            
            # 최종 결과 반환
            return {
                'progress': 1.0, 
                'prediction_result': prediction_result,
                'elapsed_time': elapsed_time
            }

        finally:
            # argv 복원 (에러 발생 시에도)
            sys.argv = original_argv
        
    except Exception as e:
        # 실패 상태로 업데이트
        self.update_state(state='FAILURE', meta={'progress': 0.0, 'error_message': str(e)})
        raise e


@router.post("/predict", response_model=PredictResponse)
async def start_predict(request: PredictRequest):
    """
    ML 모델 예측을 시작하는 엔드포인트
    """
    try:
        # Celery 작업 시작
        task = run_prediction_task.apply_async(
            args=[request.model_uri, request.data_path, request.input_type]
        )
        
        # 작업이 시작될 때까지 잠시 기다려서 PID 가져오기
        import time
        process_pid = None
        for _ in range(10):  # 최대 1초 대기
            result = AsyncResult(task.id, app=celery_app)
            if result.state == 'PREDICTING' and result.info:
                process_pid = result.info.get('process_pid')
                break
            time.sleep(0.1)
        
        return PredictResponse(
            message=f"Prediction started in background for {request.input_type} model",
            prediction_id=task.id,
            process_pid=process_pid,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict/{prediction_id}", response_model=PredictStatus)
async def get_predict_status(prediction_id: str):
    """
    예측 상태를 확인하는 엔드포인트
    """
    import time
    
    try:
        result = AsyncResult(prediction_id, app=celery_app)
        
        # 기본 상태 정보 (Redis에서 가져온 데이터로 업데이트됨)
        status_info = {
            "prediction_id": prediction_id,
            "status": result.state,
            "progress": 0.0,
            "elapsed_time": None,
            "error_message": None,
            "result": None
        }
        
        if result.state == 'PENDING':
            # 작업이 아직 시작되지 않음
            status_info["progress"] = 0.0
            status_info["elapsed_time"] = 0.0

        elif result.state == 'PREDICTING':
            # 작업이 진행 중 - 현재 시간으로 경과 시간 계산
            if result.info:
                start_time = result.info.get('start_time')
                if start_time:
                    current_elapsed = time.time() - start_time
                    status_info["elapsed_time"] = current_elapsed
                    # 진행률은 시간 기반으로 추정하기 어려우므로 0.5로 설정
                    status_info["progress"] = 0.5
                status_info.update({k: v for k, v in result.info.items() if k != 'start_time'})

        elif result.state == 'SUCCESS':
            # 작업 완료
            status_info["progress"] = 1.0
            status_info["result"] = result.result
            if result.info:
                status_info["elapsed_time"] = result.info.get("elapsed_time")

        elif result.state == 'FAILURE':
            # 작업 실패
            status_info["error_message"] = str(result.info)

        elif result.state == 'REVOKED':
            # 작업 취소됨
            status_info["progress"] = 0.0
            status_info["error_message"] = "Prediction was cancelled"
            if result.info:
                start_time = result.info.get('start_time')
                if start_time:
                    status_info["elapsed_time"] = time.time() - start_time
                status_info.update({k: v for k, v in result.info.items() if k not in ['start_time']})
                status_info["error_message"] = "Prediction was cancelled"
        
        return PredictStatus(**status_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting prediction status: {str(e)}")


@router.delete("/predict/{prediction_id}")
async def cancel_predict(prediction_id: str):
    """
    예측 작업을 취소하는 엔드포인트
    """
    try:
        result = AsyncResult(prediction_id, app=celery_app)
        
        if result.state not in ["PENDING", "PREDICTING"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel prediction in state {result.state}")
        
        # Celery 작업 취소
        celery_app.control.revoke(prediction_id, terminate=True)
        
        return {
            "message": "Prediction cancelled successfully",
            "prediction_id": prediction_id,
            "cancelled_at": datetime.now()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling prediction: {str(e)}")


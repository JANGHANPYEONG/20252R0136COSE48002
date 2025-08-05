from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal
import json
import tempfile
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult

from training_HSI.train_HSI_2d import main as train_hsi_2d
from training_HSI.train_vector import main as train_vector

# Celery 및 APIRouter 설정
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

router = APIRouter()


# Pydantic 모델 정의
class TrainRequest(BaseModel):
    config: Optional[Dict] = None
    input_type: Literal["image", "vector"]

class TrainResponse(BaseModel):
    message: str
    train_id: str
    process_pid: Optional[int] = None
    created_at: datetime

class TrainStatus(BaseModel):
    train_id: str
    status: Literal["PENDING", "TRAINING", "SUCCESS", "FAILURE", "REVOKED"]
    progress: float
    elapsed_time: Optional[float] = None  # 실행 시간 (초)
    error_message: Optional[str] = None
    result: Optional[Dict] = None


# Celery 백그라운드에서 학습을 실행하는 함수
@celery_app.task(bind=True)
def run_train_task(self, config: Dict):
    import time
    import os
    
    try:
        # 현재 프로세스 PID 가져오기
        current_pid = os.getpid()
        
        # 시작 시간 기록
        start_time = time.time()
        
        # input_type 검증
        input_type = config.get("input_type")
        if input_type not in ["image", "vector"]:
            raise ValueError(f"Invalid input_type: {input_type}. Must be 'image' or 'vector'")
        
        # 학습 상태 업데이트: TRAINING (PID 포함)
        self.update_state(state='TRAINING', meta={
            'progress': 0.0, 
            'elapsed_time': 0.0,
            'input_type': input_type,
            'process_pid': current_pid,
            'start_time': start_time
        })
        
        # train_HSI directory의 main 함수 실행
        # 임시 config 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            config_path = f.name
        
        try:
            print(f"Starting training with config: {config_path}")
            
            # train_HSI_2d.py 스크립트의 main 함수에 config 경로 전달
            import sys

            original_argv = sys.argv
            
            # 학습 실행
            # train_HSI_2d 함수가 mlflow run ID를 반환한다고 가정
            if config.get("input_type") == "image":
                sys.argv = ['train_HSI_2d.py', '--config', config_path]
                mlflow_run_id = train_hsi_2d()
            else:
                sys.argv = ['train_vector.py', '--config', config_path]
                mlflow_run_id = train_vector()
            print(f"Training completed with run ID: {mlflow_run_id}")

            # argv 복원
            sys.argv = original_argv
            
            # 완료 시간 계산
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 학습 완료 - SUCCESS 상태로 업데이트
            self.update_state(state='SUCCESS', meta={
                'progress': 1.0,
                'mlflow_run_id': mlflow_run_id,
                'elapsed_time': elapsed_time
            })
            
            # 최종 결과 반환
            return {'progress': 1.0, 'mlflow_run_id': mlflow_run_id}

        finally:
            # argv 복원 (에러 발생 시에도)
            sys.argv = original_argv
            
            # train_HSI_2d 함수 실행을 위해 임시로 만들었던 config 파일 삭제
            if os.path.exists(config_path):
                os.remove(config_path)
        
    except Exception as e:
        # Celery가 자동으로 FAILURE 상태로 처리하도록 예외를 다시 발생시킴
        # 커스텀 에러 정보는 예외 메시지에 포함
        import traceback
        error_message = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"Training failed: {error_message}")
        
        # 예외를 다시 발생시켜서 Celery가 자동으로 FAILURE 처리하도록 함
        raise Exception(error_message)


@router.post("/", response_model=TrainResponse)
async def start_train(request: TrainRequest):
    """
    ML 모델 학습을 시작하는 엔드포인트
    """
    try:
        config = request.config
        if not config:
            raise HTTPException(status_code=400, detail="Config is required")
        
        # config에 input_type 추가
        config["input_type"] = request.input_type
        
        # Celery 작업 시작
        task = run_train_task.apply_async(args=[config])
        
        # 작업이 시작될 때까지 잠시 기다려서 PID 가져오기
        import time
        process_pid = None
        for _ in range(10):  # 최대 1초 대기
            result = AsyncResult(task.id, app=celery_app)
            if result.state == 'TRAINING' and result.info:
                process_pid = result.info.get('process_pid')
                break
            time.sleep(0.1)
        
        return TrainResponse(
            message=f"Training started in background for {request.input_type} model",
            train_id=task.id,
            process_pid=process_pid,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_id}", response_model=TrainStatus)
async def get_train_status(train_id: str):
    """
    학습 상태를 확인하는 엔드포인트
    """
    import time
    
    try:
        result = AsyncResult(train_id, app=celery_app)
        
        # 기본 상태 정보 (Redis에서 가져온 데이터로 업데이트됨)
        status_info = {
            "train_id": train_id,
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

        elif result.state == 'TRAINING':
            # 작업이 진행 중 - 현재 시간으로 경과 시간 계산
            if result.info:
                start_time = result.info.get('start_time')
                if start_time:
                    current_elapsed = time.time() - start_time
                    status_info["elapsed_time"] = current_elapsed
                    # 진행률은 시간 기반으로 추정하기 어려우므로 0.1로 설정
                    status_info["progress"] = 0.1
                status_info.update({k: v for k, v in result.info.items() if k != 'start_time'})

        elif result.state == 'SUCCESS':
            # 작업 완료
            status_info["progress"] = 1.0
            status_info["result"] = result.result
            if result.info:
                status_info["elapsed_time"] = result.info.get("elapsed_time")

        elif result.state == 'FAILURE':
            # 작업 실패 - Celery가 자동으로 처리한 예외
            status_info["progress"] = 0.0
            if result.info:
                # result.info는 예외 객체이므로 문자열로 변환
                status_info["error_message"] = str(result.info)
            else:
                status_info["error_message"] = "Training failed with unknown error"

        elif result.state == 'REVOKED':
            # 작업 취소됨
            status_info["progress"] = 0.0
            status_info["error_message"] = "Training was cancelled"
            if result.info:
                start_time = result.info.get('start_time')
                if start_time:
                    status_info["elapsed_time"] = time.time() - start_time
                status_info.update({k: v for k, v in result.info.items() if k not in ['start_time']})
                status_info["error_message"] = "Training was cancelled"
        
        return TrainStatus(**status_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting training status: {str(e)}")


@router.delete("/{train_id}")
async def cancel_train(train_id: str):
    """
    학습 작업을 취소하는 엔드포인트
    """
    try:
        result = AsyncResult(train_id, app=celery_app)
        
        if result.state not in ["PENDING", "TRAINING"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel training in state {result.state}")
        
        # Celery 작업 취소
        celery_app.control.revoke(train_id, terminate=True)
        
        return {"message": "Training cancelled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling training: {str(e)}") 
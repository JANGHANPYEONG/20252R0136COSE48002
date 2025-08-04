from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid
import json
import tempfile
import os
from datetime import datetime

from training_HSI.train_HSI_2d import main as train_hsi_2d

router = APIRouter()

# Pydantic 모델들
class TrainingRequest(BaseModel):
    config: Optional[Dict] = None

class TrainingResponse(BaseModel):
    status: str
    message: str
    training_id: str
    model_path: Optional[str] = None
    created_at: datetime

class TrainingStatus(BaseModel):
    training_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: float
    current_epoch: Optional[int] = None
    total_epochs: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

# 임시 저장소 (실제로는 데이터베이스 사용)
training_jobs = {}


def run_training_background(training_id: str, request: TrainingRequest):
    """
    백그라운드에서 학습을 실행하는 함수
    """
    try:
        # 학습 상태 업데이트
        training_jobs[training_id]["status"] = "running"
        training_jobs[training_id]["updated_at"] = datetime.now()
        
        # training_HSI_2d.py의 main 함수 호출
        config = request.config

        # 임시 config 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            config_path = f.name
        
        try:
            # 3. train_HSI_2d의 main 함수 호출
            print(f"Starting training with config: {config_path}")
            
            # main 함수에 config 경로 전달
            # 만약 main 함수가 argparse를 사용한다면 sys.argv를 조작해야 함
            import sys

            original_argv = sys.argv

            sys.argv = ['train_HSI_2d.py', '--config', config_path]
            
            # 학습 실행
            mlflow_run_id = train_hsi_2d()
            print(f"Training started with run ID: {mlflow_run_id}")

            # argv 복원
            sys.argv = original_argv
            
            # 4. 학습 완료
            training_jobs[training_id]["status"] = "completed"
            training_jobs[training_id]["progress"] = 1.0
            training_jobs[training_id]["model_path"] = result.get("model_path", None)
            training_jobs[training_id]["updated_at"] = datetime.now()

        finally:
            # 임시 config 파일 삭제
            if os.path.exists(config_path):
                os.remove(config_path)
        
    except Exception as e:
        training_jobs[training_id]["status"] = "failed"
        training_jobs[training_id]["error_message"] = str(e)
        training_jobs[training_id]["updated_at"] = datetime.now()


@router.post("/training", response_model=TrainingResponse)
async def start_training(request: TrainingRequest, background_tasks: BackgroundTasks):
    """
    ML 모델 학습을 시작하는 엔드포인트
    """
    try:
        config = request.config
        if not config:
            raise HTTPException(status_code=400, detail="Config is required")
        
        training_id = str(uuid.uuid4())
        created_at = datetime.now()
        
        # 학습 작업 정보 저장
        training_jobs[training_id] = {
            "training_id": training_id,
            "status": "pending",
            "progress": 0.0,
            "current_epoch": 0,
            "total_epochs": request.epochs,
            "error_message": None,
            "created_at": created_at,
            "updated_at": created_at,
            "request": request.dict()
        }
        
        # 백그라운드에서 학습 시작
        background_tasks.add_task(run_training_background, training_id, request)
        
        return TrainingResponse(
            status="started",
            message=f"Training started for {request.model_type} model",
            training_id=training_id,
            model_path=f"/models/{training_id}/model.pth",
            created_at=created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training/{training_id}", response_model=TrainingStatus)
async def get_training_status(training_id: str):
    """
    학습 상태를 확인하는 엔드포인트
    """
    if training_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[training_id]
    return TrainingStatus(**job)


@router.get("/training", response_model=List[TrainingStatus])
async def list_trainings():
    """
    모든 학습 작업 목록을 반환하는 엔드포인트
    """
    return [TrainingStatus(**job) for job in training_jobs.values()]


@router.delete("/training/{training_id}")
async def cancel_training(training_id: str):
    """
    학습 작업을 취소하는 엔드포인트
    """
    if training_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[training_id]
    if job["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel completed or failed training")
    
    # 취소 로직
    job["status"] = "cancelled"
    job["updated_at"] = datetime.now()
    
    return {"message": "Training cancelled successfully"} 
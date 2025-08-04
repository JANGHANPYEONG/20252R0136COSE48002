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
    config: Optional[Dict] = None
    input_type: Literal["image", "vector"]

class PredictResponse(BaseModel):
    status: Literal["started", "completed", "failed"]
    message: str
    prediction_id: str
    process_pid: Optional[int] = None
    result_path: Optional[str] = None
    created_at: datetime

class PredictStatus(BaseModel):
    prediction_id: str
    status: Literal["PENDING", "STARTED", "SUCCESS", "FAILURE", "REVOKED"]
    progress: float
    result: Optional[Dict] = None
    error_message: Optional[str] = None


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Literal, List
from datetime import datetime
import asyncio
import time

from app.utils.cache_model import (
    load_or_get_cached_model,
    get_cache_status as get_cache_status_info,
    clear_cache as clear_model_cache,
    remove_cached_model
)

router = APIRouter()


# Pydantic 모델 정의
class PredictRequest(BaseModel):
    model_uri: str  # MLflow run_id 또는 모델 디렉토리 경로
    data_path: str  # 예측할 데이터 경로
    input_type: Literal["image", "vector"]

class PredictResponse(BaseModel):
    message: str
    prediction_result: Dict
    elapsed_time: float
    created_at: datetime


# 비동기 예측 함수
async def run_prediction(model_uri: str, data_path: str, input_type: str) -> Dict:
    """
    비동기로 예측을 실행하는 함수
    """
    try:
        print(f"Starting prediction with model: {model_uri}, data: {data_path}")
        
        # 캐시된 모델 사용 (input_type에 따라 적절한 Predictor 반환)
        predictor = load_or_get_cached_model(model_uri, input_type)
        
        # data_path가 여러 경로인 경우 처리
        if ',' in data_path:
            data_paths = data_path.split(',')
        else:
            data_paths = [data_path]
        
        # 예측 실행 (CPU 집약적 작업을 별도 스레드에서 실행)
        prediction_result = await asyncio.to_thread(predictor.predict, data_paths)
        
        print(f"Prediction completed successfully")
        
        return prediction_result
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        raise e


@router.post("/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    ML 모델 예측을 실행하는 엔드포인트
    """
    try:
        start_time = time.time()
        
        # input_type 검증
        if request.input_type not in ["image", "vector"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid input_type: {request.input_type}. Must be 'image' or 'vector'"
            )
        
        # 예측 실행
        prediction_result = await run_prediction(
            request.model_uri, 
            request.data_path, 
            request.input_type
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        return PredictResponse(
            message=f"Prediction completed successfully for {request.input_type} model",
            prediction_result=prediction_result,
            elapsed_time=elapsed_time,
            created_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.get("/cache/status")
async def get_cache_status():
    """
    모델 캐시 상태를 확인하는 엔드포인트
    """
    cache_status = get_cache_status_info()
    
    # datetime 변환
    for model_info in cache_status["cached_models"]:
        model_info["cached_at"] = datetime.fromtimestamp(model_info["cached_at"])
    
    return cache_status


@router.delete("/cache")
async def clear_cache():
    """
    모델 캐시를 모두 삭제하는 엔드포인트
    """
    cleared_count = clear_model_cache()
    
    return {
        "message": f"Cache cleared successfully. {cleared_count} models removed.",
        "cleared_at": datetime.now()
    }


@router.delete("/cache/{cache_key}")
async def remove_cached_model_endpoint(cache_key: str):
    """
    특정 모델을 캐시에서 제거하는 엔드포인트
    """
    removed_model = remove_cached_model(cache_key)
    
    if removed_model:
        return {
            "message": f"Model removed from cache: {removed_model['model_uri']}",
            "removed_at": datetime.now()
        }
    else:
        raise HTTPException(status_code=404, detail=f"Cache key not found: {cache_key}")
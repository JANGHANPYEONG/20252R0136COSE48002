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
        print(f"Starting prediction with model: {model_uri}, data: {data_path}, type: {input_type}")
        
        # MLflow run ID 형태 검증 및 정보 출력
        if len(model_uri) == 32:
            print(f"Detected MLflow run ID: {model_uri}")
        elif model_uri.startswith('mlflow://'):
            print(f"Detected MLflow URI: {model_uri}")
        else:
            print(f"Using local model path: {model_uri}")
        
        # 캐시된 모델 사용 (input_type에 따라 적절한 Predictor 반환)
        print("Loading model from cache or creating new instance...")
        predictor = load_or_get_cached_model(model_uri, input_type)
        print(f"Model loaded successfully: {type(predictor).__name__}")
        
        # data_path가 여러 경로인 경우 처리
        if ',' in data_path:
            data_paths = [path.strip() for path in data_path.split(',')]
            print(f"Multiple data paths detected: {len(data_paths)} files")
        else:
            data_paths = [data_path.strip()]
            print(f"Single data path: {data_path}")
        
        # 파일 존재 여부 확인
        import os
        for i, path in enumerate(data_paths):
            if not os.path.exists(path):
                raise FileNotFoundError(f"Data file not found: {path}")
            print(f"Data file {i+1} exists: {path}")
        
        # 예측 실행 (CPU 집약적 작업을 별도 스레드에서 실행)
        print("Starting prediction process...")
        prediction_result = await asyncio.to_thread(predictor.predict, data_paths)
        print(f"Prediction completed successfully")
        print(f"Result type: {type(prediction_result)}")
        
        return prediction_result
        
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error during prediction: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e


@router.post("/", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    ML 모델 예측을 실행하는 엔드포인트
    """
    try:
        start_time = time.time()
        
        # 입력 검증
        if request.input_type not in ["image", "vector"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid input_type: {request.input_type}. Must be 'image' or 'vector'"
            )
        
        if not request.model_uri.strip():
            raise HTTPException(
                status_code=400,
                detail="model_uri cannot be empty"
            )
        
        if not request.data_path.strip():
            raise HTTPException(
                status_code=400,
                detail="data_path cannot be empty"
            )
        
        print(f"Prediction request received: model={request.model_uri}, type={request.input_type}")
        
        # 예측 실행
        prediction_result = await run_prediction(
            request.model_uri, 
            request.data_path, 
            request.input_type
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"Prediction completed in {elapsed_time:.2f} seconds")
        
        return PredictResponse(
            message=f"Prediction completed successfully for {request.input_type} model",
            prediction_result=prediction_result,
            elapsed_time=elapsed_time,
            created_at=datetime.now()
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        print(f"Unexpected error in predict endpoint: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
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


@router.get("/debug/model-info/{model_uri}")
async def get_model_debug_info(model_uri: str, input_type: str):
    """
    모델 로딩 디버깅 정보를 제공하는 엔드포인트
    """
    try:
        print(f"Debug info requested for model: {model_uri}, type: {input_type}")
        
        # 모델 URI 분석
        is_mlflow_run = len(model_uri) == 32
        is_mlflow_uri = model_uri.startswith('mlflow://')
        is_local_path = not (is_mlflow_run or is_mlflow_uri)
        
        debug_info = {
            "model_uri": model_uri,
            "input_type": input_type,
            "uri_analysis": {
                "is_mlflow_run_id": is_mlflow_run,
                "is_mlflow_uri": is_mlflow_uri,
                "is_local_path": is_local_path,
                "uri_length": len(model_uri)
            }
        }
        
        # MLflow 연결 테스트
        if is_mlflow_run or is_mlflow_uri:
            try:
                import mlflow.pyfunc
                run_id = model_uri.replace('mlflow://', '')
                mlflow_uri = f"runs:/{run_id}/model"
                
                # MLflow 모델 정보 가져오기 시도
                try:
                    model_info = mlflow.models.get_model_info(mlflow_uri)
                    debug_info["mlflow_info"] = {
                        "model_uri": mlflow_uri,
                        "flavors": list(model_info.flavors.keys()) if model_info.flavors else [],
                        "model_uuid": model_info.model_uuid,
                        "utc_time_created": str(model_info.utc_time_created),
                        "model_size_bytes": model_info.model_size_bytes
                    }
                    debug_info["mlflow_status"] = "accessible"
                except Exception as model_info_error:
                    debug_info["mlflow_status"] = "model_info_failed"
                    debug_info["mlflow_error"] = str(model_info_error)
                    
            except ImportError:
                debug_info["mlflow_status"] = "mlflow_not_available"
            except Exception as mlflow_error:
                debug_info["mlflow_status"] = "connection_failed"
                debug_info["mlflow_error"] = str(mlflow_error)
        
        # 로컬 경로인 경우 파일 존재 확인
        if is_local_path:
            import os
            debug_info["local_path_info"] = {
                "exists": os.path.exists(model_uri),
                "is_directory": os.path.isdir(model_uri) if os.path.exists(model_uri) else False,
                "is_file": os.path.isfile(model_uri) if os.path.exists(model_uri) else False
            }
            
            if os.path.exists(model_uri) and os.path.isdir(model_uri):
                try:
                    files = os.listdir(model_uri)
                    debug_info["local_path_info"]["directory_contents"] = files[:10]  # 처음 10개만
                except:
                    debug_info["local_path_info"]["directory_contents"] = "access_denied"
        
        # 캐시 상태 확인
        from app.utils.cache_model import get_model_cache_key, get_cached_model
        cache_key = get_model_cache_key(model_uri, input_type)
        cached_entry = get_cached_model(model_uri, input_type)
        
        debug_info["cache_info"] = {
            "cache_key": cache_key,
            "is_cached": cached_entry is not None,
            "cached_at": datetime.fromtimestamp(cached_entry["cached_at"]) if cached_entry else None
        }
        
        return debug_info
        
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "model_uri": model_uri,
            "input_type": input_type
        }
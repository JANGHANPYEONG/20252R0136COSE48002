"""
모델 캐시 관리 모듈

이 모듈은 ML 모델의 메모리 캐싱을 담당합니다.
예측 성능 향상을 위해 자주 사용되는 모델을 메모리에 캐시합니다.
"""

import hashlib
import time
from typing import Optional, Dict, Any
from training_HSI.predict_hsi import HSIPredictor
from training_HSI.predict_vector import VectorPredictor


# 모델 캐시를 위한 전역 딕셔너리
MODEL_CACHE = {}
CACHE_MAX_SIZE = 3  # 최대 캐시할 모델 수


def get_model_cache_key(model_uri: str, input_type: str) -> str:
    """
    모델 캐시 키 생성
    
    Args:
        model_uri: 모델 URI (run_id 또는 로컬 경로)
        input_type: 입력 타입 ("image" 또는 "vector")
        
    Returns:
        str: MD5 해시로 생성된 캐시 키
    """
    return hashlib.md5(f"{model_uri}_{input_type}".encode()).hexdigest()


def get_cached_model(model_uri: str, input_type: str) -> Optional[Dict[str, Any]]:
    """
    캐시된 모델 가져오기
    
    Args:
        model_uri: 모델 URI
        input_type: 입력 타입
        
    Returns:
        Optional[Dict]: 캐시된 모델 정보 또는 None
    """
    cache_key = get_model_cache_key(model_uri, input_type)
    return MODEL_CACHE.get(cache_key)


def cache_model(model_uri: str, input_type: str, model_instance: Any) -> None:
    """
    모델을 캐시에 저장
    
    Args:
        model_uri: 모델 URI
        input_type: 입력 타입
        model_instance: 캐시할 모델 인스턴스
    """
    cache_key = get_model_cache_key(model_uri, input_type)
    
    # 캐시 크기 제한 (LRU 방식)
    if len(MODEL_CACHE) >= CACHE_MAX_SIZE:
        # 가장 오래된 항목 제거
        oldest_key = next(iter(MODEL_CACHE))
        del MODEL_CACHE[oldest_key]
        print(f"Cache full, removed oldest model: {oldest_key}")
    
    MODEL_CACHE[cache_key] = {
        'model': model_instance,
        'cached_at': time.time(),
        'model_uri': model_uri,
        'input_type': input_type
    }
    print(f"Model cached: {cache_key} (total cached: {len(MODEL_CACHE)})")


def load_or_get_cached_model(model_uri: str, input_type: str):
    """
    캐시에서 모델을 가져오거나 새로 로드
    
    Args:
        model_uri: 모델 URI (run_id 또는 로컬 경로)
        input_type: 입력 타입 ("image" 또는 "vector")
        
    Returns:
        모델 인스턴스 또는 None
    """
    # 캐시에서 확인
    cached_entry = get_cached_model(model_uri, input_type)
    if cached_entry:
        print(f"Using cached model for {model_uri}")
        return cached_entry['model']
    
    # 캐시에 없으면 새로 로드
    print(f"Loading new model for {model_uri}")
    
    if input_type == "image":
        # model_uri가 MLflow run_id인지, 로컬 디렉토리인지 판별
        # MLflow run_id 판별 (32자리 또는 mlflow:// 접두사)
        if len(model_uri) == 32 or model_uri.startswith('mlflow://'):
            # MLflow에서 임시 다운로드
            import mlflow
            temp_dir = mlflow.artifacts.download_artifacts(run_id=model_uri.replace('mlflow://', ''))
            model_instance = HSIPredictor(model_dir=temp_dir)
        else:
            # 로컬 디렉토리
            model_instance = HSIPredictor(model_dir=model_uri)
        
        # 캐시에 저장
        cache_model(model_uri, input_type, model_instance)
        return model_instance
    
    elif input_type == "vector":
        # Vector 모델 로드 및 캐시 처리
        if len(model_uri) == 32 or model_uri.startswith('mlflow://'):
            # MLflow에서 임시 다운로드
            import mlflow
            temp_dir = mlflow.artifacts.download_artifacts(run_id=model_uri.replace('mlflow://', ''))
            model_instance = VectorPredictor(model_dir=temp_dir)
        else:
            # 로컬 디렉토리
            model_instance = VectorPredictor(model_dir=model_uri)
        
        # 캐시에 저장
        cache_model(model_uri, input_type, model_instance)
        return model_instance
    
    else:
        raise ValueError(f"Unsupported input_type: {input_type}. Must be 'image' or 'vector'")


def get_cache_status() -> Dict[str, Any]:
    """
    캐시 상태 정보 반환
    
    Returns:
        Dict: 캐시 상태 정보
    """
    cache_info = []
    for cache_key, cache_entry in MODEL_CACHE.items():
        cache_info.append({
            "cache_key": cache_key,
            "model_uri": cache_entry["model_uri"],
            "input_type": cache_entry["input_type"],
            "cached_at": cache_entry["cached_at"],
            "cache_age_seconds": time.time() - cache_entry["cached_at"]
        })
    
    return {
        "total_cached_models": len(MODEL_CACHE),
        "max_cache_size": CACHE_MAX_SIZE,
        "cached_models": cache_info
    }


def clear_cache() -> int:
    """
    모든 캐시 삭제
    
    Returns:
        int: 삭제된 모델 수
    """
    global MODEL_CACHE
    cleared_count = len(MODEL_CACHE)
    MODEL_CACHE.clear()
    return cleared_count


def remove_cached_model(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    특정 모델을 캐시에서 제거
    
    Args:
        cache_key: 제거할 캐시 키
        
    Returns:
        Optional[Dict]: 제거된 모델 정보 또는 None
    """
    if cache_key in MODEL_CACHE:
        return MODEL_CACHE.pop(cache_key)
    return None


def get_cache_size() -> int:
    """
    현재 캐시 크기 반환
    
    Returns:
        int: 캐시된 모델 수
    """
    return len(MODEL_CACHE)


def set_cache_max_size(new_size: int) -> None:
    """
    최대 캐시 크기 설정
    
    Args:
        new_size: 새로운 최대 캐시 크기
    """
    global CACHE_MAX_SIZE
    CACHE_MAX_SIZE = new_size
    
    # 현재 캐시가 새로운 크기보다 크면 오래된 항목들 제거
    while len(MODEL_CACHE) > CACHE_MAX_SIZE:
        oldest_key = next(iter(MODEL_CACHE))
        del MODEL_CACHE[oldest_key]
        print(f"Cache size reduced, removed model: {oldest_key}")

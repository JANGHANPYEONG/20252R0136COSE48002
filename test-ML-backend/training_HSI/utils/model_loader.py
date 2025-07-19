import importlib
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import os

def load_model(config: Dict[str, Any]) -> nn.Module:
    """
    설정에 따라 모델을 동적으로 로드합니다.
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        nn.Module: 로드된 모델
        
    Raises:
        ImportError: 모델 파일을 찾을 수 없는 경우
        AttributeError: create_model 함수가 없는 경우
        ValueError: 모델 생성 중 오류가 발생한 경우
    """
    model_config = config.get('model', {})
    model_file = model_config.get('file')
    
    if not model_file:
        raise ValueError("Config에 'model.file'이 지정되지 않았습니다.")
    
    try:
        # 모델 모듈 import
        module_path = f'models.HSI_image.{model_file}'
        module = importlib.import_module(module_path)
        
        # create_model 함수 호출
        if hasattr(module, 'create_model'):
            model = module.create_model(config)
        elif hasattr(module, 'create_hsi_resnet_model'):  # 기존 호환성 유지
            model = module.create_hsi_resnet_model(config)
        else:
            raise AttributeError(f"Module {model_file} does not have create_model function")
        
        print(f"Successfully loaded model: {model_file}")
        return model
        
    except ImportError as e:
        print(f"Error importing model module '{module_path}': {e}")
        raise
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

def validate_model_config(config: Dict[str, Any]) -> bool:
    """
    모델 config의 유효성을 검증합니다.
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        bool: 유효성 여부
    """
    model_config = config.get('model', {})
    
    # 필수 키 확인
    required_keys = ['file', 'num_classes']
    for key in required_keys:
        if key not in model_config:
            print(f"Error: Missing required key '{key}' in model config")
            return False
    
    # 모델 파일 존재 확인
    model_file = model_config['file']
    module_path = f'models.HSI_image.{model_file}'
    
    try:
        importlib.import_module(module_path)
    except ImportError:
        print(f"Error: Model file '{module_path}' not found")
        return False
    
    return True

def get_model_info(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    모델 정보를 반환합니다.
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        Dict[str, Any]: 모델 정보
    """
    model_config = config.get('model', {})
    
    return {
        'model_file': model_config.get('file', 'unknown'),
        'num_classes': model_config.get('num_classes', 0),
        'parameters': model_config.get('parameters', {})
    } 
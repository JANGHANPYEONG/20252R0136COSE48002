import importlib
import torch
import torch.nn as nn
from typing import Dict, Any, Optional
import os

def load_model(config: Dict[str, Any]) -> nn.Module:
    model_config = config.get('model', {})
    model_file = model_config.get('file')
    namespace = model_config.get('namespace', 'HSI_image')
    
    if not model_file:
        raise ValueError("Config에 'model.file'이 지정되지 않았습니다.")
    
    module_path = f'models.{namespace}.{model_file}'
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'create_model'):
            model = module.create_model(config)
        elif hasattr(module, 'create_hsi_resnet_model'):
            model = module.create_hsi_resnet_model(config)
        else:
            raise AttributeError(f"Module {module_path} does not have create_model function")
        print(f"Successfully loaded model: {module_path}")
        return model
    except ImportError as e:
        print(f"Error importing model module '{module_path}': {e}")
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
    namespace = model_config.get('namespace', 'HSI_image')
    module_path = f'models.{namespace}.{model_file}'
    
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
        'namespace': model_config.get('namespace', 'HSI_image'),
        'num_classes': model_config.get('num_classes', 0),
        'parameters': model_config.get('parameters', {})
    }

# 하위 호환성을 위한 별칭 함수들
def load_vector_model(config: Dict[str, Any]) -> nn.Module:
    """
    HSI_vector 모델을 로드하는 하위 호환성 함수
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        nn.Module: 로드된 모델
    """
    # namespace를 HSI_vector로 강제 설정
    if 'model' not in config:
        config['model'] = {}
    config['model']['namespace'] = 'HSI_vector'
    return load_model(config)

def validate_vector_model_config(config: Dict[str, Any]) -> bool:
    """
    HSI_vector 모델 config의 유효성을 검증하는 하위 호환성 함수
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        bool: 유효성 여부
    """
    # namespace를 HSI_vector로 강제 설정
    if 'model' not in config:
        config['model'] = {}
    config['model']['namespace'] = 'HSI_vector'
    return validate_model_config(config)

def get_vector_model_info(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    HSI_vector 모델 정보를 반환하는 하위 호환성 함수
    
    Args:
        config: 설정 딕셔너리
        
    Returns:
        Dict[str, Any]: 모델 정보
    """
    # namespace를 HSI_vector로 강제 설정
    if 'model' not in config:
        config['model'] = {}
    config['model']['namespace'] = 'HSI_vector'
    return get_model_info(config) 
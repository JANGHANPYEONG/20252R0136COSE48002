import importlib
import mlflow
from typing import Dict, Any, Tuple, List
import os

def load_preprocessing_model(config: Dict) -> Any:
    """전처리 모델을 로딩합니다."""
    
    pre_config = config.get('preprocessing', {})
    model_name = pre_config.get('model_name', 'mrmr')
    model_file = pre_config.get('model_file', 'mrmr_model')
    
    try:
        # 모델 모듈 import
        module = importlib.import_module(f'models.pre.{model_file}')
        
        # 모델 생성 함수 호출
        if hasattr(module, 'create_model'):
            model = module.create_model(model_name, config)
        else:
            raise AttributeError(f"Module {model_file} does not have create_model function")
        
        print(f"Successfully loaded preprocessing model: {model_name}")
        return model
        
    except ImportError as e:
        print(f"Error importing preprocessing model module: {e}")
        raise
    except Exception as e:
        print(f"Error loading preprocessing model: {e}")
        raise

def load_training_model(config: Dict) -> Any:
    """본처리 모델을 로딩합니다."""
    
    train_config = config.get('training', {})
    model_name = train_config.get('model_name', 'gpr_ard')
    model_file = train_config.get('model_file', 'gpr_ard_model')
    load_model = train_config.get('load_model', False)
    model_version = train_config.get('model_version', None)
    
    if not load_model:
        try:
            # 모델 모듈 import
            module = importlib.import_module(f'models.training.{model_file}')
            
            # 모델 생성 함수 호출
            if hasattr(module, 'create_model'):
                model = module.create_model(model_name, config)
            else:
                raise AttributeError(f"Module {model_file} does not have create_model function")
            
            print(f"Successfully loaded training model: {model_name}")
            return model
            
        except ImportError as e:
            print(f"Error importing training model module: {e}")
            raise
        except Exception as e:
            print(f"Error loading training model: {e}")
            raise
    
    else:
        # MLflow에서 저장된 모델 로딩 (메인 파이프라인에서만 사용)
        try:
            model_uri = f"models:/{model_name}/{model_version}"
            model = mlflow.pytorch.load_model(model_uri)
            print(f"Successfully loaded model from MLflow: {model_uri}")
            return model
        except mlflow.exceptions.MlflowException as e:
            print(f"Error loading model from MLflow: {e}")
            raise

def validate_model_config(config: Dict, stage: str) -> bool:
    """모델 config의 유효성을 검증합니다."""
    
    if stage == 'preprocessing':
        pre_config = config.get('preprocessing', {})
        required_keys = ['model_name', 'model_file']
        
        for key in required_keys:
            if key not in pre_config:
                print(f"Error: Missing required key '{key}' in preprocessing config")
                return False
        
        # 모델 파일 존재 확인
        model_file = pre_config['model_file']
        module_path = f'models.pre.{model_file}'
        
        try:
            importlib.import_module(module_path)
        except ImportError:
            print(f"Error: Model file '{module_path}' not found")
            return False
    
    elif stage == 'training':
        train_config = config.get('training', {})
        required_keys = ['model_name', 'model_file']
        
        for key in required_keys:
            if key not in train_config:
                print(f"Error: Missing required key '{key}' in training config")
                return False
        
        # 모델 파일 존재 확인
        model_file = train_config['model_file']
        module_path = f'models.training.{model_file}'
        
        try:
            importlib.import_module(module_path)
        except ImportError:
            print(f"Error: Model file '{module_path}' not found")
            return False
    
    return True

def get_model_info(config: Dict, stage: str) -> Dict[str, Any]:
    """모델 정보를 반환합니다."""
    
    if stage == 'preprocessing':
        pre_config = config.get('preprocessing', {})
        return {
            'model_name': pre_config.get('model_name', 'unknown'),
            'model_file': pre_config.get('model_file', 'unknown'),
            'parameters': pre_config.get('parameters', {})
        }
    
    elif stage == 'training':
        train_config = config.get('training', {})
        return {
            'model_name': train_config.get('model_name', 'unknown'),
            'model_file': train_config.get('model_file', 'unknown'),
            'load_model': train_config.get('load_model', False),
            'model_version': train_config.get('model_version', None),
            'parameters': train_config.get('parameters', {})
        }
    
    return {}

# 메인 파이프라인에서만 사용하는 MLflow 저장 함수
def save_model_to_mlflow(model: Any, model_name: str, config: Dict, stage: str):
    """모델을 MLflow에 저장합니다 (메인 파이프라인에서만 호출)."""
    
    try:
        # 모델 저장
        mlflow.pytorch.log_model(model, f"{stage}_model")
        
        # config 저장
        mlflow.log_dict(config, f"{stage}_config/config.json")
        
        print(f"Successfully saved {stage} model to MLflow")
        
    except Exception as e:
        print(f"Error saving model to MLflow: {e}")
        raise 
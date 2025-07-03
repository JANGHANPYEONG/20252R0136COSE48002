from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # 기본 설정
    PROJECT_NAME: str = "ML Server"
    PROJECT_DESCRIPTION: str = "MLops Server"
    VERSION: str = "0.0.1"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS 설정
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # ML 모델 설정
    MODEL_SAVE_PATH: str = "/models"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 
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
    
    # 데이터베이스 설정
    DB_URI: str = "postgresql://username:password@localhost:5432/database_name"
    
    # AWS S3 설정
    S3_BUCKET_NAME: str = "your-s3-bucket-name"
    S3_REGION_NAME: str = "ap-northeast-2"
    AWS_ACCESS_KEY_ID: str = "your-aws-access-key"
    AWS_SECRET_ACCESS_KEY: str = "your-aws-secret-key"
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 
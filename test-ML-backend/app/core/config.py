from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Union
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # 기본 설정
    PROJECT_NAME: str = "ML Server"
    PROJECT_DESCRIPTION: str = "MLops Server"
    VERSION: str = "0.0.1"
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # 환경 설정
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # CORS 설정 - 환경별 분리
    ALLOWED_ORIGINS: List[str] = []
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    
    # 미들웨어 설정
    ENABLE_LOGGING: bool = True
    ENABLE_PERFORMANCE_MONITORING: bool = True
    ENABLE_DETAILED_LOGGING: bool = False  # 개발환경에서만 사용
    
    # 성능 제한 설정
    MAX_MEMORY_MB: int = 1000
    MAX_REQUESTS_PER_MINUTE: int = 1000

    # DB에 로그인 토큰 저장
    ALLOW_AUTO_PROVISION: bool = False
    ADMIN_WHITELIST: str = ""
    
    # Celery / Redis 설정
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

    # 학습 스크립트 디렉토리
    TRAINING_DIR: Union[str, None] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 환경별 CORS 설정 자동 구성
        if self.ENVIRONMENT == "development":
            self.ALLOWED_ORIGINS = [
                "http://localhost:3000",     # React 개발서버 (기본)
                "http://127.0.0.1:3000",     # 로컬호스트 alias
                "http://localhost:3001",     # 추가 React 서버 (다중 앱)
                "http://127.0.0.1:3001",     # 로컬호스트 alias
            ]
        elif self.ENVIRONMENT == "production":
            # 프로덕션에서는 명시적으로 도메인 지정 필요
            if not self.ALLOWED_ORIGINS:
                self.ALLOWED_ORIGINS = []  # 기본값: 빈 리스트 (보안)
        else:
            # 테스트 환경 등
            self.ALLOWED_ORIGINS = ["http://localhost:3000"]
        
        # TRAINING_DIR 기본값 설정 (프로젝트 루트의 training_HSI 폴더)
        if not self.TRAINING_DIR:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
            default_training_dir = os.path.join(base_dir, "training_HSI")
            self.TRAINING_DIR = os.path.normpath(default_training_dir)
    
    # ML 모델 설정
    MODEL_SAVE_PATH: str = "/models"
    MLFLOW_TRACKING_URI: str = "http://3.38.117.43:5000"
    
    # 데이터베이스 설정
    DB_URI: str
    
    # AWS S3 설정
    S3_BUCKET_NAME: str
    S3_REGION_NAME: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    FIREBASE_BUCKET_ADDRESS: str
    
    # Firebase 설정
    FIREBASE_CREDENTIALS: str

settings = Settings()
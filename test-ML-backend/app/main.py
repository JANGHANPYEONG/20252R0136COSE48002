from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import train, predict, meat, user, statistic_api, data_upload, data_crud, xai, hsi_predict, hsi_train, list_data, spectral_info, dashboard
from app.core.config import settings

# 미들웨어 임포트
from app.middleware.logging import LoggingMiddleware, DetailedLoggingMiddleware
from app.middleware.error_handler import GlobalExceptionMiddleware, ValidationErrorMiddleware
from app.middleware.performance import PerformanceMonitoringMiddleware, ResourceLimitMiddleware

# Firebase 초기화 및 토큰 검증 의존성, /auth 라우터(로그인)
from app.core.firebase import init_firebase                
from app.core.security import verify_firebase_token        
from app.api.routers.auth import router as auth_router         
from app.db.database import SessionLocal
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 설정을 app.state에 저장 (미들웨어에서 접근 가능)
app.state.settings = settings

# 미들웨어 등록 (순서 중요: 역순으로 실행됨)
# 1. 전역 예외 처리 (가장 바깥쪽)
app.add_middleware(GlobalExceptionMiddleware)
app.add_middleware(ValidationErrorMiddleware)

# 보안 미들웨어 제거됨 (Swagger UI 호환성 문제로 인해)

# 3. 로깅 미들웨어
if settings.ENABLE_LOGGING:
    app.add_middleware(LoggingMiddleware)

if settings.ENABLE_DETAILED_LOGGING and settings.ENVIRONMENT == "development":
    app.add_middleware(DetailedLoggingMiddleware, enable_body_logging=True)

# 4. 성능 모니터링
if settings.ENABLE_PERFORMANCE_MONITORING:
    app.add_middleware(PerformanceMonitoringMiddleware)
    app.add_middleware(
        ResourceLimitMiddleware,
        max_memory_mb=settings.MAX_MEMORY_MB,
        max_requests_per_minute=settings.MAX_REQUESTS_PER_MINUTE
    )

# 5. CORS 설정 (가장 안쪽)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# 로그인용 라우터 등록
app.include_router(auth_router, prefix="/auth", tags=["auth"])
# ✅ Firebase Admin 초기화 (앱 기동 시 1회)
@app.on_event("startup")
def _startup():
    init_firebase()
    app.state.db_session = SessionLocal()

# 라우터 등록
app.include_router(train.router, prefix="/train", tags=["training"])  # Celery 구성 필요
app.include_router(hsi_train.router, prefix="/hsi-train", tags=["HSI training"])  # HSI 학습 API
app.include_router(predict.router, prefix="/predict", tags=["prediction"])
app.include_router(meat.router, prefix="/meat", tags=["meat"])  # 육류 데이터 관리
app.include_router(user.router, prefix="/user", tags=["user"])  # 사용자 관리
app.include_router(statistic_api.router, prefix="/statistic", tags=["statistic"])  # 통계 데이터 관리
app.include_router(data_upload.router, prefix="/data-upload", tags=["data-upload"])  # 데이터 업로드 API
app.include_router(data_crud.router, prefix="/data", tags=["data-crud"])  # 데이터 수정/삭제 API
app.include_router(xai.router, prefix="/xai", tags=["explainable AI"])  # XAI 관련 API
app.include_router(hsi_predict.router, prefix="/hsipredict", tags=["HSI prediction"])  # HSI 예측 API
# app.include_router(training_stream.router, prefix="/train-stream", tags=["training-stream"])  # 스트리밍 학습 API 추가
app.include_router(list_data.router, prefix="/list-data", tags=["list-data"])  # 데이터 목록 조회 API
app.include_router(spectral_info.router, prefix="/spectral", tags=["spectral-info"])  # 스펙트럼 정보 관리 API
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])  # 대시보드 데이터 조회 API

#  - 여기서는 기존 호환을 위해 그대로 두고, 라우터 내부에서 엔드포인트별 보호를 권장
app.include_router(user.router, prefix="/user", tags=["user"])

@app.get("/")
async def root():
    return {"message": "ML Training API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-training-api"}

@app.get("/config/cors")
async def get_cors_config():
    """개발 환경에서 CORS 설정 확인용 (프로덕션에서는 제거 권장)"""
    if settings.DEBUG:
        return {
            "environment": settings.ENVIRONMENT,
            "allowed_origins": settings.ALLOWED_ORIGINS,
            "allowed_methods": settings.ALLOWED_METHODS,
            "allow_credentials": settings.ALLOW_CREDENTIALS,
        }
    return {"message": "Config endpoint disabled in production"}

@app.get("/stats/performance")
async def get_performance_stats():
    """성능 통계 확인 (개발/스테이징 환경에서만)"""
    if settings.ENVIRONMENT == "production":
        return {"message": "Performance stats disabled in production"}
    
    # 성능 미들웨어에서 통계 가져오기
    for middleware in app.user_middleware:
        if hasattr(middleware, 'cls') and middleware.cls.__name__ == 'PerformanceMonitoringMiddleware':
            if hasattr(middleware, 'kwargs') and 'instance' in middleware.kwargs:
                return middleware.kwargs['instance'].get_stats()
    
    return {"message": "Performance monitoring not enabled"} 
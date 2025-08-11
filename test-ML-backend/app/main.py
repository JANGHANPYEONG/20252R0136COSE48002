from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import train, predict, meat, user, statistic_api
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(train.router, prefix="/train", tags=["training"])  # Celery 구성 필요
app.include_router(predict.router, prefix="/predict", tags=["prediction"])
app.include_router(meat.router, prefix="/meat", tags=["meat"])  # 육류 데이터 관리
app.include_router(user.router, prefix="/user", tags=["user"])  # 사용자 관리
app.include_router(statistic_api.router, prefix="/statistic", tags=["statistic"])  # 통계 데이터 관리   

@app.get("/")
async def root():
    return {"message": "ML Training API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-training-api"} 
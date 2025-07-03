from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import training
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
app.include_router(training.router, prefix="/api/v1", tags=["training"])

@app.get("/")
async def root():
    return {"message": "ML Training API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ml-training-api"} 
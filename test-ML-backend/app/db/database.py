"""
FastAPI용 데이터베이스 세션 관리 모듈
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from ..core.config import settings

# 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = settings.DB_URI

# 엔진 생성
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=300,    # 5분마다 연결 재생성
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 스코프된 세션 (요청별로 세션 관리)
db_session = scoped_session(SessionLocal)

# 베이스 클래스
Base = declarative_base()
Base.query = db_session.query_property()

def get_db():
    """
    FastAPI 의존성 주입을 위한 데이터베이스 세션 생성자
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    데이터베이스 초기화 및 테이블 생성
    """
    try:
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
        
        # 초기 데이터 로드
        from .db_model import load_initial_data
        load_initial_data(db_session)
        print("Initial data loaded successfully")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

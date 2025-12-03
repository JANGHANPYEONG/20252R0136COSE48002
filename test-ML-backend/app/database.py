"""
FastAPI 서비스에서 사용할 SQLAlchemy 기본 설정을 담은 모듈.

엔진/세션/베이스 클래스를 생성해 다른 모듈에서 import 후 공유할 수 있게 해준다.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DB URL 예시: SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# PostgreSQL 예시: "postgresql://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}  # SQLite일 경우만
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

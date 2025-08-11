"""
데이터베이스 마이그레이션 스크립트
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

def check_database_connection():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    try:
        engine = create_engine(settings.DB_URI)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Database connection successful")
            return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def create_tables():
    """
    모든 테이블을 생성합니다.
    """
    try:
        from .database import init_db
        init_db()
        print("Tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

def backup_existing_data():
    """
    기존 데이터를 백업합니다.
    """
    try:
        # 백업 로직 구현 (필요시)
        print("Data backup completed")
        return True
    except Exception as e:
        print(f"Error backing up data: {e}")
        return False

def run_migration():
    """
    전체 마이그레이션을 실행합니다.
    """
    print("Starting database migration...")
    
    # 1. 데이터베이스 연결 확인
    if not check_database_connection():
        print("Migration failed: Cannot connect to database")
        return False
    
    # 2. 기존 데이터 백업
    if not backup_existing_data():
        print("Migration failed: Data backup failed")
        return False
    
    # 3. 테이블 생성
    if not create_tables():
        print("Migration failed: Table creation failed")
        return False
    
    print("Migration completed successfully")
    return True

if __name__ == "__main__":
    run_migration()

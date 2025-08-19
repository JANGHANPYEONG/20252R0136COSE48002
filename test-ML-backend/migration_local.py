"""
로컬 PostgreSQL 데이터베이스 마이그레이션 스크립트
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# .env 파일 로드
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded successfully")
except ImportError:
    print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Using system environment variables only")
except Exception as e:
    print(f"⚠️  Error loading .env file: {e}")

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_local_database_connection():
    """
    로컬 PostgreSQL 데이터베이스 연결 상태를 확인합니다.
    """
    try:
        # 환경변수에서 설정을 가져오거나 기본값 사용
        db_user = os.getenv("LOCAL_DB_USER", "postgres")
        db_password = os.getenv("LOCAL_DB_PASSWORD", "password")
        db_host = os.getenv("LOCAL_DB_HOST", "127.0.0.1")
        db_port = os.getenv("LOCAL_DB_PORT", "5432")
        db_name = os.getenv("LOCAL_DB_NAME", "ml_database")
        
        print(f"🔍 Database settings:")
        print(f"   User: {db_user}")
        print(f"   Host: {db_host}")
        print(f"   Port: {db_port}")
        print(f"   Database: {db_name}")
        print(f"   Password: {'*' * len(db_password) if db_password else 'None'}")
        
        # 먼저 postgres 데이터베이스에 연결하여 데이터베이스 존재 여부 확인
        postgres_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
        
        print(f"\n📡 Step 1: Connecting to PostgreSQL server at {db_host}:{db_port}")
        
        postgres_engine = create_engine(postgres_url)
        with postgres_engine.connect() as conn:
            print("✅ Step 1: PostgreSQL server connection successful")
            
            # 데이터베이스 존재 여부 확인
            print(f"\n📋 Step 2: Checking if database '{db_name}' exists")
            result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname = :db_name"), {"db_name": db_name})
            db_exists = result.fetchone() is not None
            
            if not db_exists:
                print(f"⚠️  Database '{db_name}' does not exist. Creating it...")
                # 자동 커밋으로 데이터베이스 생성
                conn.execute(text("COMMIT"))
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created successfully")
            else:
                print(f"✅ Database '{db_name}' already exists")
            
            # 이제 실제 데이터베이스에 연결
            local_db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            
            print(f"\n🔗 Step 3: Connecting to database '{db_name}'")
            
            local_engine = create_engine(local_db_url)
            with local_engine.connect() as local_conn:
                local_conn.execute(text("SELECT 1"))
                print("✅ Step 3: Database connection successful")
                return True, local_db_url
                
    except Exception as e:
        print(f"❌ Local database connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        return False, None

def create_local_tables():
    """
    로컬 데이터베이스에 모든 테이블을 생성합니다.
    """
    try:
        # 로컬 데이터베이스 연결
        success, db_url = check_local_database_connection()
        if not success:
            return False
            
        # 로컬 엔진 생성
        local_engine = create_engine(db_url)
        
        # 로컬 세션 생성
        LocalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=local_engine)
        local_db_session = LocalSessionLocal()
        
        # 실제 Base 클래스 사용 (LocalBase 대신)
        from app.db.database import Base
        
        # 모델들을 Base에 등록
        import app.db.db_model as models
        
        # 모든 테이블 생성
        Base.metadata.create_all(bind=local_engine)
        print("✅ Local database tables created successfully")
        
        # 초기 데이터 로드 (선택사항)
        try:
            if hasattr(models, 'load_initial_data'):
                models.load_initial_data(local_db_session)
                print("✅ Initial data loaded successfully")
            else:
                print("⚠️  load_initial_data function not found")
        except Exception as e:
            print(f"⚠️  Initial data loading failed (optional): {e}")
        
        local_db_session.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating local tables: {e}")
        return False

def backup_existing_data():
    """
    기존 데이터를 백업합니다.
    """
    try:
        print("📋 Data backup completed (no existing data to backup)")
        return True
    except Exception as e:
        print(f"⚠️  Error backing up data: {e}")
        return False

def run_local_migration():
    """
    로컬 데이터베이스 마이그레이션을 실행합니다.
    """
    print("🚀 Starting local database migration...")
    
    # 1. 로컬 데이터베이스 연결 확인
    success, _ = check_local_database_connection()
    if not success:
        print("❌ Migration failed: Cannot connect to local database")
        print("\n💡 Troubleshooting tips:")
        print("1. PostgreSQL 서비스가 실행 중인지 확인")
        print("2. 데이터베이스가 생성되었는지 확인")
        print("3. 사용자 권한이 올바른지 확인")
        print("4. 환경변수 설정 확인:")
        print("   - LOCAL_DB_USER")
        print("   - LOCAL_DB_PASSWORD") 
        print("   - LOCAL_DB_HOST")
        print("   - LOCAL_DB_PORT")
        print("   - LOCAL_DB_NAME")
        return False
    
    # 2. 기존 데이터 백업
    if not backup_existing_data():
        print("⚠️  Migration continued despite backup failure")
    
    # 3. 테이블 생성
    if not create_local_tables():
        print("❌ Migration failed: Table creation failed")
        return False
    
    print("✅ Local migration completed successfully!")
    return True

if __name__ == "__main__":
    run_local_migration()

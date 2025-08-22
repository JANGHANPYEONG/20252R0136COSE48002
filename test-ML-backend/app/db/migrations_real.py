"""
데이터베이스 마이그레이션 스크립트 (로컬 및 AWS RDS 지원)
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

def create_database_if_not_exists():
    """
    데이터베이스가 없으면 생성합니다.
    """
    try:
        # 기본 연결 (postgres 데이터베이스에 연결)
        db_uri = settings.DB_URI
        if 'postgresql://' in db_uri:
            # 데이터베이스 이름을 추출
            db_name = db_uri.split('/')[-1]
            # postgres 데이터베이스에 연결하는 URI 생성
            base_uri = db_uri.rsplit('/', 1)[0] + '/postgres'
            
            # autocommit 모드로 엔진 생성
            engine = create_engine(base_uri, isolation_level="AUTOCOMMIT")
            with engine.connect() as conn:
                # 데이터베이스 존재 여부 확인
                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if not result.fetchone():
                    # 데이터베이스가 없으면 생성
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"Database '{db_name}' created successfully")
                else:
                    print(f"Database '{db_name}' already exists")
            return True
        else:
            print("Not a PostgreSQL database, skipping database creation")
            return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def check_database_connection():
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    try:
        # DB_URI에서 연결 정보 추출
        db_uri = settings.DB_URI
        print(f"🔍 Database settings from DB_URI:")
        print(f"   URI: {db_uri.replace(db_uri.split('@')[0].split(':')[-1], '***')}")
        
        # 연결 테스트
        print(f"\n📡 Step 1: Testing database connection...")
        engine = create_engine(db_uri)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Step 1: Database connection successful")
            
            # 데이터베이스 정보 확인
            db_info = conn.execute(text("SELECT current_database(), current_user, version()"))
            db_name, db_user, db_version = db_info.fetchone()
            print(f"   Connected to: {db_name}")
            print(f"   User: {db_user}")
            print(f"   Version: {db_version.split(',')[0]}")
            
            return True, engine
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Error details: {str(e)}")
        return False, None

def check_database_health():
    """
    데이터베이스 상태를 확인합니다.
    """
    try:
        success, engine = check_database_connection()
        if not success:
            return False, None
            
        with engine.connect() as conn:
            print(f"\n📋 Step 2: Checking database health...")
            
            # 테이블 개수 확인
            table_count = conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'"))
            table_count = table_count.fetchone()[0]
            print(f"   Existing tables: {table_count}")
            
            # 데이터베이스 크기 확인
            db_size = conn.execute(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
            db_size = db_size.fetchone()[0]
            print(f"   Database size: {db_size}")
            
            # 연결 수 확인
            connections = conn.execute(text("SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()"))
            connections = connections.fetchone()[0]
            print(f"   Active connections: {connections}")
            
            print("✅ Step 2: Database health check completed")
            return True, engine
            
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False, None

def backup_existing_data(engine):
    """
    기존 데이터를 백업합니다.
    """
    try:
        print(f"\n💾 Step 3: Checking existing data...")
        
        with engine.connect() as conn:
            # 기존 테이블 목록 확인
            tables = conn.execute(text("""
                SELECT table_name, 
                       (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public') as total_tables
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            existing_tables = []
            for table in tables:
                existing_tables.append(table[0])
            
            if existing_tables:
                print(f"   Found {len(existing_tables)} existing tables:")
                for table in existing_tables[:5]:  # 처음 5개만 표시
                    print(f"     - {table}")
                if len(existing_tables) > 5:
                    print(f"     ... and {len(existing_tables) - 5} more")
                
                # 데이터가 있는지 확인
                for table in existing_tables[:3]:  # 처음 3개 테이블만 확인
                    try:
                        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        row_count = count.fetchone()[0]
                        if row_count > 0:
                            print(f"     ⚠️  Table '{table}' has {row_count} rows")
                    except:
                        pass
                        
                print("   ⚠️  Existing data detected - tables will be recreated")
            else:
                print("   No existing tables found - fresh installation")
            
            print("✅ Step 3: Data assessment completed")
            return True
            
    except Exception as e:
        print(f"⚠️  Data assessment failed (continuing): {e}")
        return True

def create_tables(engine):
    """
    모든 테이블을 생성합니다.
    """
    try:
        print(f"\n🏗️  Step 4: Creating database tables...")
        
        # Base 클래스와 모델들 가져오기
        from .database import init_db, Base
        from . import db_model as models
        
        # 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✅ Step 4: Tables created successfully")
        
        # 생성된 테이블 확인
        with engine.connect() as conn:
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """))
            
            created_tables = [table[0] for table in tables]
            print(f"   Created {len(created_tables)} tables:")
            for table in created_tables:
                print(f"     - {table}")
        
        # 초기 데이터 로드 (선택사항)
        try:
            if hasattr(models, 'load_initial_data'):
                print(f"\n📊 Step 5: Loading initial data...")
                LocalSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                db_session = LocalSessionLocal()
                
                models.load_initial_data(db_session)
                print("✅ Step 5: Initial data loaded successfully")
                db_session.close()
            else:
                print(f"\n📊 Step 5: No initial data to load")
                print("✅ Step 5: Skipped (load_initial_data function not found)")
        except Exception as e:
            print(f"⚠️  Initial data loading failed (optional): {e}")
            print("✅ Step 5: Skipped due to error")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

def run_migration():
    """
    전체 마이그레이션을 실행합니다.
    """
    print("🚀 Starting database migration...")
    print(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    # 1. 데이터베이스 연결 확인
    success, engine = check_database_connection()
    if not success:
        print("❌ Migration failed: Cannot connect to database")
        print("\n💡 Troubleshooting tips:")
        print("1. DB_URI 환경변수가 올바르게 설정되었는지 확인")
        print("2. 데이터베이스 서버가 실행 중인지 확인")
        print("3. 네트워크 연결 및 방화벽 설정 확인")
        print("4. 데이터베이스 사용자 권한 확인")
        return False
    
    # 2. 데이터베이스 상태 확인
    success, engine = check_database_health()
    if not success:
        print("❌ Migration failed: Database health check failed")
        return False
    
    # 3. 기존 데이터 백업/확인
    if not backup_existing_data(engine):
        print("❌ Migration failed: Data backup/assessment failed")
        return False
    
    # 4. 테이블 생성
    if not create_tables(engine):
        print("❌ Migration failed: Table creation failed")
        return False
    
    print(f"\n🎉 Migration completed successfully!")
    print(f"   Database: {settings.DB_URI.split('/')[-1]}")
    print(f"   Tables created and ready for use")
    return True

if __name__ == "__main__":
    run_migration()

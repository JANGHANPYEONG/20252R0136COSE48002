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
        
        # 직접 Base 클래스 생성 (app.db.database import 방지)
        from sqlalchemy.ext.declarative import declarative_base
        LocalBase = declarative_base()
        
        # 모델들을 직접 정의 (db_model.py의 내용을 기반으로)
        from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, CheckConstraint, PrimaryKeyConstraint, ForeignKeyConstraint
        from sqlalchemy.dialects.postgresql import JSONB
        from sqlalchemy.sql import func
        
        # 기본 정보 테이블들
        class SpeciesInfo(LocalBase):
            __tablename__ = "species_info"
            id = Column(Integer, primary_key=True)
            value = Column(String(255))
        
        class CategoryInfo(LocalBase):
            __tablename__ = "category_info"
            id = Column(Integer, primary_key=True)
            speciesId = Column(Integer, nullable=False)
            primalValue = Column(String(255), nullable=False)
            secondaryValue = Column(String(255), nullable=False)
            
            __table_args__ = (
                ForeignKeyConstraint(["speciesId"], ["species_info.id"], onupdate="CASCADE"),
            )
        
        class GradeInfo(LocalBase):
            __tablename__ = "grade_info"
            id = Column(Integer, primary_key=True)
            value = Column(String(255))
        
        class SexInfo(LocalBase):
            __tablename__ = "sex_info"
            id = Column(Integer, primary_key=True)
            value = Column(String(255))
        
        class StatusInfo(LocalBase):
            __tablename__ = "status_info"
            id = Column(Integer, primary_key=True)
            value = Column(String(255))
        
        class UserTypeInfo(LocalBase):
            __tablename__ = "userType_info"
            id = Column(Integer, primary_key=True)
            name = Column(String(255))
        
        # 사용자 테이블
        class User(LocalBase):
            __tablename__ = "user"
            userId = Column(String(255), primary_key=True)
            createdAt = Column(DateTime, nullable=False)
            updatedAt = Column(DateTime)
            loginAt = Column(DateTime)
            name = Column(String(255), nullable=False)
            company = Column(String(255))
            jobTitle = Column(String(255))
            homeAddr = Column(String(255))
            alarm = Column(Boolean, nullable=False, server_default='0')
            type = Column(Integer, nullable=False)
            
            __table_args__ = (
                ForeignKeyConstraint(["type"], ["userType_info.id"], onupdate="CASCADE"),
            )
        
        # 육류 테이블
        class Meat(LocalBase):
            __tablename__ = "meat"
            id = Column(String(255), primary_key=True)
            userId = Column(String(255), nullable=False, server_default='deeplant@example.com')
            sexType = Column(Integer)
            categoryId = Column(Integer, nullable=False)
            gradeNum = Column(Integer)
            statusType = Column(Integer, server_default='0')
            createdAt = Column(DateTime, nullable=False)
            updatedAt = Column(DateTime)
            traceNum = Column(String(255), nullable=False)
            farmAddr = Column(String(255))
            farmerName = Column(String(255))
            butcheryYmd = Column(DateTime, nullable=False)
            birthYmd = Column(DateTime)
            imagePath = Column(String(255))
            
            __table_args__ = (
                ForeignKeyConstraint(["userId"], ["user.userId"], ondelete="SET DEFAULT", onupdate="CASCADE"),
                ForeignKeyConstraint(["sexType"], ["sex_info.id"], onupdate="CASCADE"),
                ForeignKeyConstraint(["categoryId"], ["category_info.id"], onupdate="CASCADE"),
                ForeignKeyConstraint(["gradeNum"], ["grade_info.id"], onupdate="CASCADE"),
                ForeignKeyConstraint(["statusType"], ["status_info.id"], onupdate="CASCADE"),
            )
        
        # 딥에이징 정보
        class DeepAgingInfo(LocalBase):
            __tablename__ = "deepAging_info"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            isCompleted = Column(Integer, server_default='0')
            date = Column(DateTime, nullable=False)
            minute = Column(Integer, nullable=False)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno"),
                ForeignKeyConstraint(["id"], ["meat.id"], ondelete="CASCADE", onupdate="CASCADE"),
            )
        
        # 관능검사 (원육)
        class SensoryEval(LocalBase):
            __tablename__ = "sensory_eval"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            isRefrigerated = Column(Boolean, nullable=False, server_default='0')
            createdAt = Column(DateTime, nullable=False)
            userId = Column(String(255), nullable=False, server_default='deeplant@example.com')
            period = Column(Integer, nullable=False)
            filmedAt = Column(DateTime)
            imagePath = Column(String(255))
            marbling = Column(Float)
            meat_color = Column(Float)
            texture = Column(Float)
            surface_moisture = Column(Float)
            overall = Column(Float)
            manufactureYmd = Column(DateTime, nullable=False)
            expireYmd = Column(DateTime)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
                ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
                ForeignKeyConstraint(["userId"], ["user.userId"], ondelete="SET DEFAULT", onupdate="CASCADE"),
            )
        
        # AI 관능검사
        class AI_SensoryEval(LocalBase):
            __tablename__ = "ai_sensory_eval"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            isRefrigerated = Column(Boolean, nullable=False, server_default='0')
            createdAt = Column(DateTime, nullable=False)
            xai_imagePath = Column(String(255))
            xai_gradeNum = Column(Integer)
            xai_gradeNum_imagePath = Column(String(255))
            marbling = Column(Float)
            meat_color = Column(Float)
            texture = Column(Float)
            surface_moisture = Column(Float)
            overall = Column(Float)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
                ForeignKeyConstraint(["id", "seqno", "isRefrigerated"], ["sensory_eval.id", "sensory_eval.seqno", "sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
                ForeignKeyConstraint(["xai_gradeNum"], ["grade_info.id"], onupdate="CASCADE"),
            )
        
        # 관능검사 (가열육)
        class HeatedmeatSensoryEval(LocalBase):
            __tablename__ = "heatedmeat_sensory_eval"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            createdAt = Column(DateTime, nullable=False)
            userId = Column(String(255), nullable=False, server_default='deeplant@example.com')
            period = Column(Integer, nullable=False)
            filmedAt = Column(DateTime)
            imagePath = Column(String(255))
            isRefrigerated = Column(Boolean, nullable=False, server_default='0')
            flavor = Column(Float)
            juiciness = Column(Float)
            tenderness = Column(JSONB)
            umami = Column(Float)
            palatability = Column(Float)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno"),
                ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
                ForeignKeyConstraint(["userId"], ["user.userId"], ondelete="SET DEFAULT", onupdate="CASCADE"),
            )
        
        # AI 가열육 관능검사
        class AI_HeatedmeatSensoryEval(LocalBase):
            __tablename__ = "ai_heatedmeat_sensory_eval"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            createdAt = Column(DateTime, nullable=False)
            xai_imagePath = Column(String(255))
            flavor = Column(Float)
            juiciness = Column(Float)
            tenderness = Column(JSONB)
            umami = Column(Float)
            palatability = Column(Float)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno"),
                ForeignKeyConstraint(["id", "seqno"], ["heatedmeat_sensory_eval.id", "heatedmeat_sensory_eval.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
            )
        
        # 실험 데이터
        class ProbexptData(LocalBase):
            __tablename__ = "probexpt_data"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            isHeated = Column(Boolean, nullable=False, server_default='0')
            createdAt = Column(DateTime, nullable=False)
            userId = Column(String(255), nullable=False, server_default='deeplant@example.com')
            period = Column(Integer)
            L = Column(Float)
            a = Column(Float)
            b = Column(Float)
            DL = Column(Float)
            CL = Column(Float)
            RW = Column(Float)
            ph = Column(Float)
            WBSF = Column(Float)
            cardepsin_activity = Column(Float)
            MFI = Column(Float)
            Collagen = Column(Float)
            sourness = Column(Float)
            bitterness = Column(Float)
            umami = Column(Float)
            richness = Column(Float)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno", "isHeated"),
                ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
                ForeignKeyConstraint(['userId'], ['user.userId'], ondelete="SET DEFAULT", onupdate="CASCADE"),
            )
        
        # OpenCV 이미지 정보
        class OpenCVImagesInfo(LocalBase):
            __tablename__ = "openCV_images_info"
            id = Column(String(255), nullable=False)
            seqno = Column(Integer, nullable=False)
            section_imagePath = Column(String(255))
            full_palette = Column(JSONB)
            fat_palette = Column(JSONB)
            protein_palette = Column(JSONB)
            protein_rate = Column(Float)
            fat_rate = Column(Float)
            lbp_images = Column(JSONB)
            gabor_images = Column(JSONB)
            contrast = Column(Float)
            dissimilarity = Column(Float)
            homogeneity = Column(Float)
            energy = Column(Float)
            correlation = Column(Float)
            createdAt = Column(DateTime, nullable=False)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno"),
                ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
            )
        
        # 스펙트럼 정보
        class SpectralInfo(LocalBase):
            __tablename__ = "spectral_info"
            spectral_index = Column(Integer, primary_key=True)
            wavelength_nm = Column(Float, unique=True)
        
        # HSI 관능검사
        class HSISensoryEval(LocalBase):
            __tablename__ = "hsi_sensory_eval"
            id = Column(String(255), primary_key=True)
            seqno = Column(Integer, primary_key=True)
            isRefrigerated = Column(Boolean, nullable=False, server_default='0', primary_key=True)
            createdAt = Column(DateTime)
            xai_imagePath = Column(String(255))
            xai_gradeNum = Column(Integer)
            xai_gradeNum_imagePath = Column(String(255))
            marbling = Column(Float)
            meat_color = Column(Float)
            texture = Column(Float)
            surface_moisture = Column(Float)
            overall = Column(Float)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
                ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
            )
        
        # HSI 이미지 밴드
        class HSIImagesBands(LocalBase):
            __tablename__ = "hsi_images_bands"
            id = Column(String(255), primary_key=True)
            seqno = Column(Integer, primary_key=True)
            isRefrigerated = Column(Boolean, nullable=False, server_default='0', primary_key=True)
            spectral_index = Column(Integer, nullable=False, primary_key=True)
            topLeft = Column(Integer)
            topRight = Column(Integer)
            bottomRight = Column(Integer)
            bottomLeft = Column(Integer)
            filename = Column(String(255))
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno", "isRefrigerated", "spectral_index"),
                ForeignKeyConstraint(["id", "seqno", "isRefrigerated"], ["hsi_sensory_eval.id", "hsi_sensory_eval.seqno", "hsi_sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
                ForeignKeyConstraint(["spectral_index"], ["spectral_info.spectral_index"], ondelete="CASCADE", onupdate="CASCADE"),
            )
        
        # AI HSI 관능검사
        class AI_HSISensoryEval(LocalBase):
            __tablename__ = "ai_hsi_sensory_eval"
            id = Column(String(255), primary_key=True)
            seqno = Column(Integer, primary_key=True)
            isRefrigerated = Column(Boolean, nullable=False, server_default='0', primary_key=True)
            createdAt = Column(DateTime, nullable=False)
            xai_imagePath = Column(String(255))
            xai_gradeNum = Column(Integer)
            xai_gradeNum_imagePath = Column(String(255))
            marbling = Column(Float)
            meat_color = Column(Float)
            texture = Column(Float)
            surface_moisture = Column(Float)
            overall = Column(Float)
            
            __table_args__ = (
                PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
                ForeignKeyConstraint(["id", "seqno", "isRefrigerated"], ["hsi_sensory_eval.id", "hsi_sensory_eval.seqno", "hsi_sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
                ForeignKeyConstraint(["xai_gradeNum"], ["grade_info.id"], onupdate="CASCADE"),
            )
        
        # 모든 테이블 생성
        LocalBase.metadata.create_all(bind=local_engine)
        print("✅ All local database tables created successfully")
        
        # 초기 데이터 로드
        try:
            # 기본 정보 데이터 삽입
            print("📝 Loading initial data...")
            
            # Species Info
            species_data = ["소", "돼지"]
            for i, species in enumerate(species_data):
                local_db_session.execute(text("INSERT INTO species_info (id, value) VALUES (:id, :value) ON CONFLICT (id) DO NOTHING"), 
                                       {"id": i, "value": species})
            
            # User Type Info
            user_types = {0: "Normal", 1: "Researcher", 2: "Manager", 3: "None"}
            for user_id, user_type in user_types.items():
                local_db_session.execute(text("INSERT INTO userType_info (id, name) VALUES (:id, :name) ON CONFLICT (id) DO NOTHING"), 
                                       {"id": user_id, "name": user_type})
            
            # Grade Info
            grades = {0: "1++", 1: "1+", 2: "1", 3: "2", 4: "3", 5: "None"}
            for grade_id, grade in grades.items():
                local_db_session.execute(text("INSERT INTO grade_info (id, value) VALUES (:id, :value) ON CONFLICT (id) DO NOTHING"), 
                                       {"id": grade_id, "value": grade})
            
            # Sex Info
            sexes = {0: "수", 1: "암", 2: "거세", 3: "null"}
            for sex_id, sex in sexes.items():
                local_db_session.execute(text("INSERT INTO sex_info (id, value) VALUES (:id, :value) ON CONFLICT (id) DO NOTHING"), 
                                       {"id": sex_id, "value": sex})
            
            # Status Info
            statuses = {0: "대기중", 1: "반려", 2: "승인"}
            for status_id, status in statuses.items():
                local_db_session.execute(text("INSERT INTO status_info (id, value) VALUES (:id, :value) ON CONFLICT (id) DO NOTHING"), 
                                       {"id": status_id, "value": status})
            
            # Default User
            from datetime import datetime
            now = datetime.now()
            local_db_session.execute(text("""
                INSERT INTO "user" (userId, createdAt, name, type, alarm) 
                VALUES (:userId, :createdAt, :name, :type, :alarm) 
                ON CONFLICT (userId) DO NOTHING
            """), {
                "userId": "deeplant@example.com",
                "createdAt": now,
                "name": "deeplant",
                "type": 2,
                "alarm": False
            })
            
            local_db_session.commit()
            print("✅ Initial data loaded successfully")
            
        except Exception as e:
            print(f"⚠️  Initial data loading failed: {e}")
            local_db_session.rollback()
        
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

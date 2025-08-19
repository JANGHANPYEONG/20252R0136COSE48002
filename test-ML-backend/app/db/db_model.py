# DB Model Config File
import time
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
    Boolean,
    CheckConstraint, create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, scoped_session, sessionmaker, validates

from app.utils import *

# 기본 사용자 정보 직접 정의 (import 문제 해결을 위해)
default_user_id = 'deeplant@example.com'
default_user_type = 2

# Base는 database.py에서 import
from .database import Base


# initialize_db 함수는 database.py로 이동됨


# SET UP CONTROLLER
def load_initial_data(db_session):
    """
    초기 데이터 셋업 function
    """
    # 1. Specie
    for id, specie in enumerate(species):
        if not db_session.query(SpeciesInfo).get(id):
            temp = SpeciesInfo(id=id, value=specie)  # 0: Cattle, 1: Pig
            db_session.add(temp)
    db_session.commit()

    # 2. Cattle
    for id, large in enumerate(cattleLarge):
        for s_id, small in enumerate(cattleSmall[id]):
            index = calId(id, s_id, CATTLE)
            if not db_session.query(CategoryInfo).get(index):
                temp = CategoryInfo(
                    id=index,
                    speciesId=CATTLE,
                    primalValue=large,
                    secondaryValue=small,
                )
                db_session.add(temp)
    db_session.commit()

    # 3. Pig
    for id, large in enumerate(pigLarge):
        for s_id, small in enumerate(pigSmall[id]):
            index = calId(id, s_id, PIG)
            if not db_session.query(CategoryInfo).get(index):
                temp = CategoryInfo(
                    id=index,
                    speciesId=PIG,
                    primalValue=large,
                    secondaryValue=small,
                )
                db_session.add(temp)
    db_session.commit()

    # 4. UserType
    for id, Type in usrType.items():
        if not db_session.query(UserTypeInfo).get(id):
            temp = UserTypeInfo(id=id, name=Type)
            db_session.add(temp)
    db_session.commit()

    # 5. GradeNum
    for id, Type in gradeNum.items():
        if not db_session.query(GradeInfo).get(id):
            temp = GradeInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()

    # 6. SexType
    for id, Type in sexType.items():
        if not db_session.query(SexInfo).get(id):
            temp = SexInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()

    # 7. StatusType
    for id, Type in statusType.items():
        if not db_session.query(StatusInfo).get(id):
            temp = StatusInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()
    
    # 8. User
    default_user = db_session.query(User).get(default_user_id)

    if not default_user:
        current_date = datetime.now().strftime('%Y-%m-%d')
        temp = User(
            userId=default_user_id,
            createdAt=current_date,
            name='deeplant',
            type=default_user_type,
            updatedAt=None,
            loginAt=None,
            company=None,
            jobTitle=None,
            homeAddr=None,
            alarm=False
        )
        db_session.add(temp)
    db_session.commit()


# Texonomy Table
class SpeciesInfo(Base):
    __tablename__ = "species_info"
    id = Column(Integer, primary_key=True)  # 종 ID
    value = Column(String(255))  # 종명(ex. cattle, pig)


class CategoryInfo(Base):
    __tablename__ = "category_info"
    id = Column(Integer, primary_key=True)  # 카테고리 ID
    speciesId = Column(Integer)
    primalValue = Column(String(255), nullable=False)
    secondaryValue = Column(String(255), nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ["speciesId"], ["species_info.id"],
            onupdate="CASCADE"
        ),
    )


class GradeInfo(Base):
    """
    0: 1++
    1: 1+
    2: 1
    3: 2
    4: 3
    5: None(Null)
    """

    __tablename__ = "grade_info"
    id = Column(Integer, primary_key=True)  # 등급 ID
    value = Column(String(255))  # 등급


class SexInfo(Base):
    """
    0: 수
    1: 암
    2: 거세
    3: null
    """

    __tablename__ = "sex_info"
    id = Column(Integer, primary_key=True)  # 성별 ID
    value = Column(String(255))  # 성별 값


class StatusInfo(Base):
    """
    0: 대기중
    1: 반려
    2: 승인
    """

    __tablename__ = "status_info"
    id = Column(Integer, primary_key=True)  # 승인 ID
    value = Column(String(255))  # 승인 정보


class UserTypeInfo(Base):
    """
    0: Normal
    1: Researcher
    2: Manager
    3: None
    """

    __tablename__ = "userType_info"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    
    
class User(Base):
    __tablename__ = "user"
    userId = Column(String(255), primary_key=True) # 유저 ID(이메일)
    createdAt = Column(DateTime, nullable=False) # 유저 ID 생성 시간
    updatedAt = Column(DateTime) # 최신의 유저 정보 수정 시간
    loginAt = Column(DateTime) # 유저 로그인 시간
    name = Column(String(255), nullable=False) # 유저명
    company = Column(String(255))  # 직장명
    jobTitle = Column(String(255))  # 직위명
    homeAddr = Column(String(255))  # 유저 주소
    alarm = Column(
        Boolean, 
        nullable=False,
        server_default='0'
    )  # 유저 알람 허용 여부
    type = Column(Integer, nullable=False)  # 유저 타입 ID
    __table_args__ = (
        ForeignKeyConstraint(
            ["type"], ["userType_info.id"],
            onupdate="CASCADE"
        ),
    )


class Meat(Base):
    __tablename__ = "meat"
    # 1. 기본 정보
    id = Column(String(255), primary_key=True)  # 육류 관리번호
    userId = Column(
        String(255),
        nullable=False, 
        server_default=default_user_id
    )  # 생성한 유저 ID
    sexType = Column(Integer)  # 성별 ID
    categoryId = Column(Integer, nullable=False)  # 육종 ID
    gradeNum = Column(Integer)  # 등급 ID
    statusType = Column(Integer, server_default='0')  # 승인 여부 ID

    # 2. 육류 Open API 정보
    createdAt = Column(DateTime, nullable=False)  # 육류 관리번호 생성 시간
    updatedAt = Column(DateTime) # 대기 중인 상태에서 반려한 시간
    traceNum = Column(String(255), nullable=False)  # 이력번호(혹은 묶은 번호)
    farmAddr = Column(String(255))  # 농장 주소
    farmerName = Column(String(255))  # 농장주 이름
    butcheryYmd = Column(DateTime, nullable=False)  # 도축 일자
    birthYmd = Column(DateTime)  # 출생일자

    # 3. 이미지 Path
    imagePath = Column(String(255))  # QR 이미지 S3 경로
    
    __table_args__ = (
        ForeignKeyConstraint(
            ["userId"], ["user.userId"],
            ondelete="SET DEFAULT",
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["sexType"], ["sex_info.id"],
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["categoryId"], ["category_info.id"],
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["gradeNum"], ["grade_info.id"],
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["statusType"], ["status_info.id"],
            onupdate="CASCADE"
        ),
    )


class DeepAgingInfo(Base):
    __tablename__ = "deepAging_info"
    
    # 1. 복합키 설정
    id = Column(
        String(255),
        primary_key=True,
    )  # 육류 관리번호
    seqno = Column(Integer, primary_key=True)  # 가공 횟수
    isCompleted = Column(Integer, server_default='0')
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id"], ["meat.id"],
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
    )

    # 2. 딥에이징 데이터
    date = Column(DateTime, nullable=False)  # 딥에이징 실시 날짜
    minute = Column(Integer, nullable=False)  # 딥에이징 진행 시간 (분)


class SensoryEval(Base):
    __tablename__ = "sensory_eval"

    # 1. 복합키 설정
    id = Column(
        String(255),
        primary_key=True,
    )  # 육류 관리번호
    seqno = Column(Integer, primary_key=True)  # 가공 횟수

    # 2. 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)  # 관능검사 생성 시간
    userId = Column(
        String(255), 
        nullable=False, 
        server_default=default_user_id
    )  # 관능검사 생성한 유저 ID
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    filmedAt = Column(DateTime) # 이미지 등록 시간
    imagePath = Column(String(255))  # 관능검사 이미지 경로
    isRefrigerated = Column(Boolean, nullable=False, server_default='0')  # 추가

    # 3. 관능검사 측정 데이터
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)

    weight_kg = Column(Float)
    manufactureYmd = Column(DateTime, nullable=False)
    expireYmd = Column(DateTime) 

    # 3. 이미지 Path
    imagePath = Column(String(255))
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint(
            ["id", "seqno",], ["deepAging_info.id", "deepAging_info.seqno",],
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["userId"], ["user.userId"],
            ondelete="SET DEFAULT",
            onupdate="CASCADE"
        ),
        CheckConstraint("period >= 0", name="check_period_non_negative"),
        CheckConstraint("marbling >= 1 AND marbling <= 10", name="check_marbling_range"),
        CheckConstraint("color >= 1 AND color <= 10", name="check_color_range"),
        CheckConstraint("texture >= 1 AND texture <= 10", name="check_texture_range"),
        CheckConstraint('"surfaceMoisture" >= 1 AND "surfaceMoisture" <= 10', name="check_surfaceMoisture_range"),
        CheckConstraint("overall >= 1 AND overall <= 10", name="check_overall_range"),
    )


class AI_SensoryEval(Base):
    __tablename__ = "ai_sensory_eval"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)

    # 2. AI 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    xai_imagePath = Column(String(255))  # 예측 관능검사 이미지 경로
    xai_gradeNum = Column(Integer)  # 예측 등급
    xai_gradeNum_imagePath = Column(String(255))  # 예측 등급 image path

    # 3. 관능검사 AI 예측 데이터
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint(
            ["id", "seqno", "isRefrigerated"],
            ["sensory_eval.id", "sensory_eval.seqno", "sensory_eval.isRefrigerated"],
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["xai_gradeNum"], ["grade_info.id"],
            onupdate="CASCADE"
        ),
        CheckConstraint("marbling >= 1 AND marbling <= 10", name="check_marbling_range"),
        CheckConstraint("color >= 1 AND color <= 10", name="check_color_range"),
        CheckConstraint("texture >= 1 AND texture <= 10", name="check_texture_range"),
        CheckConstraint('"surfaceMoisture" >= 1 AND "surfaceMoisture" <= 10', name="check_surfaceMoisture_range"),
        CheckConstraint("overall >= 1 AND overall <= 10", name="check_overall_range"),
    )


class HeatedmeatSensoryEval(Base):
    __tablename__ = "heatedmeat_sensory_eval"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)

    # 2. 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    userId = Column(
        String(255), 
        nullable=False,
        server_default=default_user_id
    )
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    filmedAt = Column(DateTime) # 이미지 등록 시간
    imagePath = Column(String(255))  # 가열육 관능검사 이미지 경로
    isRefrigerated = Column(Boolean, nullable=False, server_default='0')  # 추가

    # 3. 관능검사 측정 데이터
    flavor = Column(Float)
    juiciness = Column(Float)
    tenderness = Column(JSONB)
    umami = Column(Float)
    palatability = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], 
            ["deepAging_info.id", "deepAging_info.seqno"],
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ["userId"], 
            ["user.userId"], 
            ondelete="SET DEFAULT", 
            onupdate="CASCADE"
        ),
        CheckConstraint('"period" >= 0', name="check_period_value"),
        CheckConstraint('"flavor" >= 1 and "flavor" <= 10', name="check_flavor_stat"),
        CheckConstraint('"juiciness" >= 1 and "juiciness" <= 10', name="check_juiciness_stat"),
        CheckConstraint('"umami" >= 1 and "umami" <= 10', name="check_umami_stat"),
        CheckConstraint('"palatability" >= 1 and "palatability" <= 10', name="check_palatability_stat")
    )
    
    @validates('tenderness')
    def validate_tenderness(self, key, value):
        required_keys = {'0', '3', '7', '14', '21'}
        if not isinstance(value, dict):
            raise ValueError("Tenderness must be a JSON object")
        
        keys = set(value.keys())
        if not keys.issubset(required_keys):
            raise ValueError(f"Invalid keys in tenderness: {keys - required_keys}")
        
        for k, v in value.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"Tenderness value for key {k} must be a number")
            if not (1 <= v <= 10):
                raise ValueError(f"Tenderness value for key {k} must be between 1 and 10")
        
        return value


class AI_HeatedmeatSeonsoryEval(Base):
    __tablename__ = "ai_heatedmeat_sensory_eval"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)

    # 2. AI 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    xai_imagePath = Column(String(255))  # 예측 관능검사 이미지 경로

    # 3. 관능검사 AI 예측 데이터
    flavor = Column(Float)
    juiciness = Column(Float)
    tenderness = Column(JSONB)
    umami = Column(Float)
    palatability = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], 
            ["heatedmeat_sensory_eval.id", "heatedmeat_sensory_eval.seqno"], 
            ondelete="CASCADE", 
            onupdate="CASCADE"
        ),
        CheckConstraint('"flavor" >= 1 and "flavor" <= 10', name="check_flavor_stat"),
        CheckConstraint('"juiciness" >= 1 and "juiciness" <= 10', name="check_juiciness_stat"),
        CheckConstraint('"umami" >= 1 and "umami" <= 10', name="check_umami_stat"),
        CheckConstraint('"palatability" >= 1 and "palatability" <= 10', name="check_palatability_stat")
    )
    
    @validates('tenderness')
    def validate_tenderness(self, key, value):
        required_keys = {'0', '3', '7', '14', '21'}
        if not isinstance(value, dict):
            raise ValueError("Tenderness must be a JSON object")
        
        keys = set(value.keys())
        if not keys.issubset(required_keys):
            raise ValueError(f"Invalid keys in tenderness: {keys - required_keys}")
        
        for k, v in value.items():
            if not isinstance(v, (int, float)):
                raise ValueError(f"Tenderness value for key {k} must be a number")
            if not (1 <= v <= 10):
                raise ValueError(f"Tenderness value for key {k} must be between 1 and 10")
        
        return value


class ProbexptData(Base):
    __tablename__ = "probexpt_data"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    isHeated = Column(
        Boolean, 
        primary_key=True,
        server_default='0'
    )

    # 2. 연구실 메타 데이터
    createdAt = Column(DateTime, nullable=False)
    userId = Column(
        String(255), 
        nullable=False,
        server_default=default_user_id
    )
    period = Column(Integer)

    # 3. 실험 데이터
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

    # 4. 전자혀 데이터
    sourness = Column(Float)
    bitterness = Column(Float)
    umami = Column(Float)
    richness = Column(Float) 
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isHeated"),
        ForeignKeyConstraint(
            ["id", "seqno"], 
            ["deepAging_info.id", "deepAging_info.seqno"], 
            ondelete="CASCADE", 
            onupdate="CASCADE"
        ),
        ForeignKeyConstraint(
            ['userId'],
            ['user.userId'],
            ondelete="SET DEFAULT",
            onupdate="CASCADE"
        ),
        CheckConstraint('"period" >= 0', name="check_period_value"),
        CheckConstraint('"DL" >= 0 AND "DL" <= 100', name="check_DL_percentage"),
        CheckConstraint('"CL" >= 0 AND "CL" <= 100', name="check_CL_percentage"),
        CheckConstraint('"RW" >= 0 AND "RW" <= 100', name="check_RW_percentage"),
    )


class OpenCVImagesInfo(Base):
    __tablename__ = "openCV_images_info"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)

    # 2. 단면 이미지
    section_imagePath = Column(String(255))
    
    # 3. 컬러팔레트 및 단백질 비율
    full_palette = Column(JSONB)
    fat_palette = Column(JSONB)
    protein_palette = Column(JSONB)
    protein_rate = Column(Float)
    fat_rate = Column(Float)
    
    # 4. 학습에 필요한 이미지 URL JSONB
    lbp_images = Column(JSONB)
    gabor_images = Column(JSONB)
    
    # 5. 학습에 필요한 텍스쳐 정보
    contrast = Column(Float)
    dissimilarity = Column(Float)
    homogeneity = Column(Float)
    energy = Column(Float)
    correlation = Column(Float)
    
    createdAt = Column(DateTime, nullable=False)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], 
            ["deepAging_info.id", "deepAging_info.seqno"], 
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        CheckConstraint('"protein_rate" >= 0 and "protein_rate" <= 100', name="check_protein_rate"),
        CheckConstraint('"fat_rate" >= 0 and "fat_rate" <= 100', name="check_fat_rate"),
        CheckConstraint('"contrast" >= 0', name="check_texture_contrast"),
        CheckConstraint('"dissimilarity" >= 0', name="check_texture_dissimilarity"),
        CheckConstraint('"homogeneity" >= 0', name="check_texture_homogeneity"),
        CheckConstraint('"energy" >= 0', name="check_texture_energy"),
        CheckConstraint('"correlation" >= 0', name="check_texture_correlation"),
    )


# HSI 관련 테이블

class SpectralInfo(Base):
    __tablename__ = "spectral_info"
    spectral_index = Column(Integer, primary_key=True)
    wavelength_nm = Column(Float, unique=True)


class HSISensoryEval(Base):
    __tablename__ = "hsi_sensory_eval"
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    isRefrigerated = Column(Boolean, nullable=False, server_default='0', primary_key=True)
    createdAt = Column(DateTime)
    xai_imagePath = Column(String(255))
    xai_gradeNum = Column(Integer)
    xai_gradeNum_imagePath = Column(String(255))
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint([
            "id", "seqno"
        ], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),

    )


class HSIImagesBands(Base):
    __tablename__ = "hsi_images_bands"
    # 복합키 설정
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
        ForeignKeyConstraint([
            "id", "seqno", "isRefrigerated", 
        ], ["hsi_sensory_eval.id", "hsi_sensory_eval.seqno", "hsi_sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint([
            "spectral_index"
        ], ["spectral_info.spectral_index"], ondelete="CASCADE", onupdate="CASCADE"),
    )


class AI_HSISensoryEval(Base):
    __tablename__ = "ai_hsi_sensory_eval"
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    isRefrigerated = Column(Boolean, nullable=False, server_default='0', primary_key=True)
    createdAt = Column(DateTime, nullable=False)
    xai_imagePath = Column(String(255))
    xai_gradeNum = Column(Integer)
    xai_gradeNum_imagePath = Column(String(255))
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint([
            "id", "seqno", "isRefrigerated"
        ], ["hsi_sensory_eval.id", "hsi_sensory_eval.seqno", "hsi_sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint([
            "xai_gradeNum"
        ], ["grade_info.id"], onupdate="CASCADE"),
    )

## {parent}-{child} 테이블 간 관계 정의
# categoryInfo - meat
CategoryInfo.meats = relationship(
    "Meat",
    back_populates="categoryInfos"
)
Meat.categoryInfos = relationship("CategoryInfo", back_populates="meats")

# speciesInfo - categoryInfo
SpeciesInfo.categoryInfos = relationship(
    "CategoryInfo",
    back_populates="speciesInfos"
)
CategoryInfo.speciesInfos = relationship("SpeciesInfo", back_populates="categoryInfos")

# gradeInfo - meat
GradeInfo.meats = relationship(
    "Meat",
    back_populates="gradeInfos"
)
Meat.gradeInfos = relationship("GradeInfo", back_populates="meats")

# gradeInfo - aiSensoryEval
GradeInfo.aiSensoryEvals = relationship(
    "AI_SensoryEval",
    back_populates="gradeInfos"
)
AI_SensoryEval.gradeInfos = relationship("GradeInfo", back_populates="aiSensoryEvals")

# sexInfo - meat
SexInfo.meats = relationship(
    "Meat",
    back_populates="sexInfos"
)
Meat.sexInfos = relationship("SexInfo", back_populates="meats")

# statusInfo - meat
StatusInfo.meats = relationship(
    "Meat",
    back_populates="statusInfos"
)
Meat.statusInfos = relationship("StatusInfo", back_populates="meats")

# userType - user
UserTypeInfo.users = relationship(
    "User", 
    back_populates="userTypeInfos",
    cascade="all, delete-orphan"
)
User.userTypeInfos = relationship("UserTypeInfo", back_populates="users")

# user - meat
User.meats = relationship(
    "Meat",
    back_populates="users"
)
Meat.users = relationship("User", back_populates="meats")

# user - sensoryEval
User.sensoryEvals = relationship(
    "SensoryEval",
    back_populates="users"
)
SensoryEval.users = relationship("User", back_populates="sensoryEvals")

# user - heatedMeatSensoryEval
User.heatedMeatSensoryEvals = relationship(
    "HeatedmeatSensoryEval",
    back_populates="users"
)
HeatedmeatSensoryEval.users = relationship("User", back_populates="heatedMeatSensoryEvals")

# user - probexptData
User.probexptDatas = relationship(
    "ProbexptData",
    back_populates="users"
)
ProbexptData.users = relationship("User", back_populates="probexptDatas")

# meat - deepAgingInfo
Meat.deepAgingInfos = relationship(
    "DeepAgingInfo", 
    back_populates="meats",
    cascade="all, delete-orphan"
)
DeepAgingInfo.meats = relationship("Meat", back_populates="deepAgingInfos")

# deepAgingInfo - SensoryEval
DeepAgingInfo.sensoryEvals = relationship(
    "SensoryEval",
    back_populates="deepAgingInfos",
    cascade="all, delete-orphan"
)
SensoryEval.deepAgingInfos = relationship("DeepAgingInfo", back_populates="sensoryEvals")

# deepAgingInfo - heatedmeatSensoryEval
DeepAgingInfo.heatedmeatSensoryEvals = relationship(
    "HeatedmeatSensoryEval",
    back_populates="deepAgingInfos",
    cascade="all, delete-orphan"
)
HeatedmeatSensoryEval.deepAgingInfos = relationship("DeepAgingInfo", back_populates="heatedmeatSensoryEvals")

# deepAgingInfo - probexptData
DeepAgingInfo.probexptDatas = relationship(
    "ProbexptData",
    back_populates="deepAgingInfos",
    cascade="all, delete-orphan"
)
ProbexptData.deepAgingInfos = relationship("DeepAgingInfo", back_populates="probexptDatas")

# deepAgingInfo - OpenCVImagesInfo
DeepAgingInfo.openCVImagesInfos = relationship(
    "OpenCVImagesInfo",
    back_populates="deepAgingInfos",
    cascade="all, delete-orphan"
)
OpenCVImagesInfo.deepAgingInfos = relationship("DeepAgingInfo", back_populates="openCVImagesInfos")

# deepAgingInfo - HSISensoryEval
DeepAgingInfo.hsiSensoryEvals = relationship(
    "HSISensoryEval",
    back_populates="deepAgingInfo",
    cascade="all, delete-orphan"
)
HSISensoryEval.deepAgingInfo = relationship("DeepAgingInfo", back_populates="hsiSensoryEvals")

# sensoryEval - aiSensoryEval
SensoryEval.aiSensoryEvals = relationship(
    "AI_SensoryEval",
    back_populates="sensoryEvals",
    cascade="all, delete-orphan"
)
AI_SensoryEval.sensoryEvals = relationship("SensoryEval", back_populates="aiSensoryEvals")

# heatedmeatSensoryEval - aiHeatedmeatSensoryEval
HeatedmeatSensoryEval.aiHeatedmeatSensoryEvals = relationship(
    "AI_HeatedmeatSeonsoryEval",
    back_populates="heatedmeatSensoryEvals",
    cascade="all, delete-orphan"
)
AI_HeatedmeatSeonsoryEval.heatedmeatSensoryEvals = relationship("HeatedmeatSensoryEval", back_populates="aiHeatedmeatSensoryEvals")

# HSISensoryEval - HSIImagesBands
HSISensoryEval.hsiImagesBands = relationship(
    "HSIImagesBands",
    back_populates="hsiSensoryEval",
    cascade="all, delete-orphan"
)
HSIImagesBands.hsiSensoryEval = relationship("HSISensoryEval", back_populates="hsiImagesBands")

# SpectralInfo - HSIImagesBands
SpectralInfo.hsiImagesBands = relationship(
    "HSIImagesBands",
    back_populates="spectralInfo",
    cascade="all, delete-orphan"
)
HSIImagesBands.spectralInfo = relationship("SpectralInfo", back_populates="hsiImagesBands")

# HSISensoryEval - AI_HSISensoryEval
HSISensoryEval.aiHSISensoryEvals = relationship(
    "AI_HSISensoryEval",
    back_populates="hsiSensoryEval",
    cascade="all, delete-orphan"
)
AI_HSISensoryEval.hsiSensoryEval = relationship("HSISensoryEval", back_populates="aiHSISensoryEvals")

# GradeInfo - AI_HSISensoryEval
GradeInfo.aiHSISensoryEvals = relationship(
    "AI_HSISensoryEval",
    back_populates="gradeInfo"
)
AI_HSISensoryEval.gradeInfo = relationship("GradeInfo", back_populates="aiHSISensoryEvals")

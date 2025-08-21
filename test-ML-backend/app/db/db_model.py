# db_model.py — rebuilt from user's schema with color→meat_color, casing unified for HSI blocks,
# duplicate fields fixed, typos corrected, and constraints aligned.
from __future__ import annotations

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
    CheckConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates

from app.utils import *  # species, cattleLarge, cattleSmall, pigLarge, pigSmall, usrType, gradeNum, sexType, statusType, calId, CATTLE, PIG

# 기본 사용자 정보 직접 정의 (import 문제 해결용)
default_user_id = 'deeplant@example.com'
default_user_type = 2

# Base는 database.py에서 import
from .database import Base


# =============================================================================
# 초기 데이터 셋업
# =============================================================================

def load_initial_data(db_session):
    """초기 데이터 셋업 function"""
    # 1. Species
    for id, specie in enumerate(species):
        if not db_session.query(SpeciesInfo).get(id):
            db_session.add(SpeciesInfo(id=id, value=specie))
    db_session.commit()

    # 2. Cattle Category
    for id, large in enumerate(cattleLarge):
        for s_id, small in enumerate(cattleSmall[id]):
            index = calId(id, s_id, CATTLE)
            if not db_session.query(CategoryInfo).get(index):
                db_session.add(CategoryInfo(id=index, speciesId=CATTLE, primalValue=large, secondaryValue=small))
    db_session.commit()

    # 3. Pig Category
    for id, large in enumerate(pigLarge):
        for s_id, small in enumerate(pigSmall[id]):
            index = calId(id, s_id, PIG)
            if not db_session.query(CategoryInfo).get(index):
                db_session.add(CategoryInfo(id=index, speciesId=PIG, primalValue=large, secondaryValue=small))
    db_session.commit()

    # 4. UserType
    for id, Type in usrType.items():
        if not db_session.query(UserTypeInfo).get(id):
            db_session.add(UserTypeInfo(id=id, name=Type))
    db_session.commit()

    # 5. Grade
    for id, Type in gradeNum.items():
        if not db_session.query(GradeInfo).get(id):
            db_session.add(GradeInfo(id=id, value=Type))
    db_session.commit()

    # 6. Sex
    for id, Type in sexType.items():
        if not db_session.query(SexInfo).get(id):
            db_session.add(SexInfo(id=id, value=Type))
    db_session.commit()

    # 7. Status
    for id, Type in statusType.items():
        if not db_session.query(StatusInfo).get(id):
            db_session.add(StatusInfo(id=id, value=Type))
    db_session.commit()

    # 8. Default User
    if not db_session.query(User).get(default_user_id):
        now = datetime.now()
        db_session.add(User(userId=default_user_id, createdAt=now, name='deeplant', type=default_user_type,
                            updatedAt=None, loginAt=None, company=None, jobTitle=None, homeAddr=None, alarm=False))
    db_session.commit()


# =============================================================================
# 텍사노미
# =============================================================================

class SpeciesInfo(Base):
    __tablename__ = "species_info"

    id = Column(Integer, primary_key=True)
    value = Column(String(255))


class CategoryInfo(Base):
    __tablename__ = "category_info"

    id = Column(Integer, primary_key=True)
    speciesId = Column(Integer, nullable=False)
    primalValue = Column(String(255), nullable=False)
    secondaryValue = Column(String(255), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(["speciesId"], ["species_info.id"], onupdate="CASCADE"),
    )


class GradeInfo(Base):
    """0: 1++  1: 1+  2: 1  3: 2  4: 3  5: None"""
    __tablename__ = "grade_info"

    id = Column(Integer, primary_key=True)
    value = Column(String(255))


class SexInfo(Base):
    """0: 수  1: 암  2: 거세  3: null"""
    __tablename__ = "sex_info"

    id = Column(Integer, primary_key=True)
    value = Column(String(255))


class StatusInfo(Base):
    """0: 대기중  1: 반려  2: 승인"""
    __tablename__ = "status_info"

    id = Column(Integer, primary_key=True)
    value = Column(String(255))


class UserTypeInfo(Base):
    """0: Normal  1: Researcher  2: Manager  3: None"""
    __tablename__ = "userType_info"  # 원본 테이블명 유지

    id = Column(Integer, primary_key=True)
    name = Column(String(255))


# =============================================================================
# 유저
# =============================================================================

class User(Base):
    __tablename__ = "user"

    userId = Column(String(255), primary_key=True)  # 이메일

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


# =============================================================================
# 원육
# =============================================================================

class Meat(Base):
    __tablename__ = "meat"

    # 기본
    id = Column(String(255), primary_key=True)  # 육류 관리번호
    userId = Column(String(255), nullable=False, server_default=default_user_id)
    sexType = Column(Integer)
    categoryId = Column(Integer, nullable=False)
    gradeNum = Column(Integer)
    statusType = Column(Integer, server_default='0')

    # 오픈 API 정보
    createdAt = Column(DateTime, nullable=False)
    updatedAt = Column(DateTime)
    traceNum = Column(String(255), nullable=False)
    farmAddr = Column(String(255))
    farmerName = Column(String(255))
    butcheryYmd = Column(DateTime, nullable=False)
    birthYmd = Column(DateTime)

    # 이미지 Path
    imagePath = Column(String(255))  # QR 이미지 S3 경로

    __table_args__ = (
        ForeignKeyConstraint(["userId"], ["user.userId"], ondelete="SET DEFAULT", onupdate="CASCADE"),
        ForeignKeyConstraint(["sexType"], ["sex_info.id"], onupdate="CASCADE"),
        ForeignKeyConstraint(["categoryId"], ["category_info.id"], onupdate="CASCADE"),
        ForeignKeyConstraint(["gradeNum"], ["grade_info.id"], onupdate="CASCADE"),
        ForeignKeyConstraint(["statusType"], ["status_info.id"], onupdate="CASCADE"),
    )


# =============================================================================
# 딥에이징
# =============================================================================

class DeepAgingInfo(Base):
    __tablename__ = "deepAging_info"  # 원본 테이블명 유지

    id = Column(String(255), nullable=False)  # 육류 관리번호
    seqno = Column(Integer, nullable=False)  # 가공 횟수
    isCompleted = Column(Integer, server_default='0')

    # 데이터
    date = Column(DateTime, nullable=False)
    minute = Column(Integer, nullable=False)  # 진행 시간(분)

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(["id"], ["meat.id"], ondelete="CASCADE", onupdate="CASCADE"),
    )


# =============================================================================
# 관능검사 (원육)
# =============================================================================

class SensoryEval(Base):
    __tablename__ = "sensory_eval"

    # 키
    id = Column(String(255), nullable=False)
    seqno = Column(Integer, nullable=False)
    isRefrigerated = Column(Boolean, nullable=False, server_default='0')

    # 메타
    createdAt = Column(DateTime, nullable=False)
    userId = Column(String(255), nullable=False, server_default=default_user_id)
    period = Column(Integer, nullable=False)
    filmedAt = Column(DateTime)
    imagePath = Column(String(255))  # (중복 선언 제거)

    # 측정값 (統一)
    marbling = Column(Float)
    meat_color = Column(Float)  # ← 통일 포인트
    texture = Column(Float)
    surface_moisture = Column(Float)
    overall = Column(Float)

    manufactureYmd = Column(DateTime, nullable=False)
    expireYmd = Column(DateTime)

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint(["userId"], ["user.userId"], ondelete="SET DEFAULT", onupdate="CASCADE"),
        CheckConstraint("period >= 0", name="check_period_non_negative"),
        CheckConstraint("marbling >= 1 AND marbling <= 10", name="check_marbling_range"),
        CheckConstraint("meat_color >= 1 AND meat_color <= 10", name="check_meat_color_range"),
        CheckConstraint("texture >= 1 AND texture <= 10", name="check_texture_range"),
        CheckConstraint("surface_moisture >= 1 AND surface_moisture <= 10", name="check_surface_moisture_range"),
        CheckConstraint("overall >= 1 AND overall <= 10", name="check_overall_range"),
    )


class AI_SensoryEval(Base):
    __tablename__ = "ai_sensory_eval"

    id = Column(String(255), nullable=False)
    seqno = Column(Integer, nullable=False)
    isRefrigerated = Column(Boolean, nullable=False, server_default='0')

    createdAt = Column(DateTime, nullable=False)
    xai_imagePath = Column(String(255))
    xai_gradeNum = Column(Integer)
    xai_gradeNum_imagePath = Column(String(255))

    # 예측값 (統一)
    marbling = Column(Float)
    meat_color = Column(Float)
    texture = Column(Float)
    surface_moisture = Column(Float)
    overall = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint(["id", "seqno", "isRefrigerated"], ["sensory_eval.id", "sensory_eval.seqno", "sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint(["xai_gradeNum"], ["grade_info.id"], onupdate="CASCADE"),
        CheckConstraint("marbling >= 1 AND marbling <= 10", name="check_ai_marbling_range"),
        CheckConstraint("meat_color >= 1 AND meat_color <= 10", name="check_ai_meat_color_range"),
        CheckConstraint("texture >= 1 AND texture <= 10", name="check_ai_texture_range"),
        CheckConstraint("surface_moisture >= 1 AND surface_moisture <= 10", name="check_ai_surface_moisture_range"),
        CheckConstraint("overall >= 1 AND overall <= 10", name="check_ai_overall_range"),
    )


# =============================================================================
# 관능검사 (가열육)
# =============================================================================

class HeatedmeatSensoryEval(Base):
    __tablename__ = "heatedmeat_sensory_eval"

    id = Column(String(255), nullable=False)
    seqno = Column(Integer, nullable=False)

    createdAt = Column(DateTime, nullable=False)
    userId = Column(String(255), nullable=False, server_default=default_user_id)
    period = Column(Integer, nullable=False)
    filmedAt = Column(DateTime)
    imagePath = Column(String(255))
    isRefrigerated = Column(Boolean, nullable=False, server_default='0')

    flavor = Column(Float)
    juiciness = Column(Float)
    tenderness = Column(JSONB)  # {"0":x, "3":y, "7":z, "14":a, "21":b}
    umami = Column(Float)
    palatability = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint(["userId"], ["user.userId"], ondelete="SET DEFAULT", onupdate="CASCADE"),
        CheckConstraint('"period" >= 0', name="check_period_value"),
        CheckConstraint('"flavor" >= 1 and "flavor" <= 10', name="check_flavor_stat"),
        CheckConstraint('"juiciness" >= 1 and "juiciness" <= 10', name="check_juiciness_stat"),
        CheckConstraint('"umami" >= 1 and "umami" <= 10', name="check_umami_stat"),
        CheckConstraint('"palatability" >= 1 and "palatability" <= 10', name="check_palatability_stat"),
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


class AI_HeatedmeatSensoryEval(Base):  # 오탈자 수정(Seonsory→Sensory)
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
        CheckConstraint('"flavor" >= 1 and "flavor" <= 10', name="check_ai_flavor_stat"),
        CheckConstraint('"juiciness" >= 1 and "juiciness" <= 10', name="check_ai_juiciness_stat"),
        CheckConstraint('"umami" >= 1 and "umami" <= 10', name="check_ai_umami_stat"),
        CheckConstraint('"palatability" >= 1 and "palatability" <= 10', name="check_ai_palatability_stat"),
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


# =============================================================================
# 실험 데이터 / OpenCV
# =============================================================================

class ProbexptData(Base):
    __tablename__ = "probexpt_data"

    id = Column(String(255), nullable=False)
    seqno = Column(Integer, nullable=False)
    isHeated = Column(Boolean, nullable=False, server_default='0')

    createdAt = Column(DateTime, nullable=False)
    userId = Column(String(255), nullable=False, server_default=default_user_id)
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
        CheckConstraint('"period" >= 0', name="check_period_value"),
        CheckConstraint('"DL" >= 0 AND "DL" <= 100', name="check_DL_percentage"),
        CheckConstraint('"CL" >= 0 AND "CL" <= 100', name="check_CL_percentage"),
        CheckConstraint('"RW" >= 0 AND "RW" <= 100', name="check_RW_percentage"),
    )


class OpenCVImagesInfo(Base):
    __tablename__ = "openCV_images_info"  # 원본 테이블명 유지

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
        CheckConstraint('"protein_rate" >= 0 and "protein_rate" <= 100', name="check_protein_rate"),
        CheckConstraint('"fat_rate" >= 0 and "fat_rate" <= 100', name="check_fat_rate"),
        CheckConstraint('"contrast" >= 0', name="check_texture_contrast"),
        CheckConstraint('"dissimilarity" >= 0', name="check_texture_dissimilarity"),
        CheckConstraint('"homogeneity" >= 0', name="check_texture_homogeneity"),
        CheckConstraint('"energy" >= 0', name="check_texture_energy"),
        CheckConstraint('"correlation" >= 0', name="check_texture_correlation"),
    )


# =============================================================================
# HSI
# =============================================================================

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

    # 통일된 명명
    marbling = Column(Float)
    meat_color = Column(Float)
    texture = Column(Float)
    surface_moisture = Column(Float)
    overall = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint(["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"], ondelete="CASCADE", onupdate="CASCADE"),
    )


class HSIImagesBands(Base):
    __tablename__ = "hsi_images_bands"

    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    isRefrigerated = Column(Boolean, nullable=False, server_default='0', primary_key=True)
    spectral_index = Column(Integer, nullable=False, primary_key=True)

    topLeft = Column(JSONB)  # [x, y] 좌표 배열
    topRight = Column(JSONB)  # [x, y] 좌표 배열
    bottomRight = Column(JSONB)  # [x, y] 좌표 배열
    bottomLeft = Column(JSONB)  # [x, y] 좌표 배열

    filename = Column(String(255))

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated", "spectral_index"),
        ForeignKeyConstraint(["id", "seqno", "isRefrigerated"], ["hsi_sensory_eval.id", "hsi_sensory_eval.seqno", "hsi_sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint(["spectral_index"], ["spectral_info.spectral_index"], ondelete="CASCADE", onupdate="CASCADE"),
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
    meat_color = Column(Float)
    texture = Column(Float)
    surface_moisture = Column(Float)
    overall = Column(Float)

    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno", "isRefrigerated"),
        ForeignKeyConstraint(["id", "seqno", "isRefrigerated"], ["hsi_sensory_eval.id", "hsi_sensory_eval.seqno", "hsi_sensory_eval.isRefrigerated"], ondelete="CASCADE", onupdate="CASCADE"),
        ForeignKeyConstraint(["xai_gradeNum"], ["grade_info.id"], onupdate="CASCADE"),
    )


# =============================================================================
# 관계 정의 (원본 명칭 기반 back_populates 유지)
# =============================================================================

# categoryInfo - meat
CategoryInfo.meats = relationship("Meat", back_populates="categoryInfos")
Meat.categoryInfos = relationship("CategoryInfo", back_populates="meats")

# speciesInfo - categoryInfo
SpeciesInfo.categoryInfos = relationship("CategoryInfo", back_populates="speciesInfos")
CategoryInfo.speciesInfos = relationship("SpeciesInfo", back_populates="categoryInfos")

# gradeInfo - meat
GradeInfo.meats = relationship("Meat", back_populates="gradeInfos")
Meat.gradeInfos = relationship("GradeInfo", back_populates="meats")

# gradeInfo - aiSensoryEval
GradeInfo.aiSensoryEvals = relationship("AI_SensoryEval", back_populates="gradeInfos")
AI_SensoryEval.gradeInfos = relationship("GradeInfo", back_populates="aiSensoryEvals")

# sexInfo - meat
SexInfo.meats = relationship("Meat", back_populates="sexInfos")
Meat.sexInfos = relationship("SexInfo", back_populates="meats")

# statusInfo - meat
StatusInfo.meats = relationship("Meat", back_populates="statusInfos")
Meat.statusInfos = relationship("StatusInfo", back_populates="meats")

# userType - user
UserTypeInfo.users = relationship("User", back_populates="userTypeInfos", cascade="all, delete-orphan")
User.userTypeInfos = relationship("UserTypeInfo", back_populates="users")

# user - meat
User.meats = relationship("Meat", back_populates="users")
Meat.users = relationship("User", back_populates="meats")

# user - sensoryEval
User.sensoryEvals = relationship("SensoryEval", back_populates="users")
SensoryEval.users = relationship("User", back_populates="sensoryEvals")

# user - heatedMeatSensoryEval
User.heatedMeatSensoryEvals = relationship("HeatedmeatSensoryEval", back_populates="users")
HeatedmeatSensoryEval.users = relationship("User", back_populates="heatedMeatSensoryEvals")

# user - probexptData
User.probexptDatas = relationship("ProbexptData", back_populates="users")
ProbexptData.users = relationship("User", back_populates="probexptDatas")

# meat - deepAgingInfo
Meat.deepAgingInfos = relationship("DeepAgingInfo", back_populates="meats", cascade="all, delete-orphan")
DeepAgingInfo.meats = relationship("Meat", back_populates="deepAgingInfos")

# deepAgingInfo - SensoryEval
DeepAgingInfo.sensoryEvals = relationship("SensoryEval", back_populates="deepAgingInfos", cascade="all, delete-orphan")
SensoryEval.deepAgingInfos = relationship("DeepAgingInfo", back_populates="sensoryEvals")

# deepAgingInfo - heatedmeatSensoryEval
DeepAgingInfo.heatedmeatSensoryEvals = relationship("HeatedmeatSensoryEval", back_populates="deepAgingInfos", cascade="all, delete-orphan")
HeatedmeatSensoryEval.deepAgingInfos = relationship("DeepAgingInfo", back_populates="heatedmeatSensoryEvals")

# deepAgingInfo - probexptData
DeepAgingInfo.probexptDatas = relationship("ProbexptData", back_populates="deepAgingInfos", cascade="all, delete-orphan")
ProbexptData.deepAgingInfos = relationship("DeepAgingInfo", back_populates="probexptDatas")

# deepAgingInfo - OpenCVImagesInfo
DeepAgingInfo.openCVImagesInfos = relationship("OpenCVImagesInfo", back_populates="deepAgingInfos", cascade="all, delete-orphan")
OpenCVImagesInfo.deepAgingInfos = relationship("DeepAgingInfo", back_populates="openCVImagesInfos")

# deepAgingInfo - HSISensoryEval
DeepAgingInfo.hsiSensoryEvals = relationship("HSISensoryEval", back_populates="deepAgingInfo", cascade="all, delete-orphan")
HSISensoryEval.deepAgingInfo = relationship("DeepAgingInfo", back_populates="hsiSensoryEvals")

# sensoryEval - aiSensoryEval
SensoryEval.aiSensoryEvals = relationship("AI_SensoryEval", back_populates="sensoryEvals", cascade="all, delete-orphan")
AI_SensoryEval.sensoryEvals = relationship("SensoryEval", back_populates="aiSensoryEvals")

# heatedmeatSensoryEval - aiHeatedmeatSensoryEval
HeatedmeatSensoryEval.aiHeatedmeatSensoryEvals = relationship("AI_HeatedmeatSensoryEval", back_populates="heatedmeatSensoryEvals", cascade="all, delete-orphan")
AI_HeatedmeatSensoryEval.heatedmeatSensoryEvals = relationship("HeatedmeatSensoryEval", back_populates="aiHeatedmeatSensoryEvals")

# HSISensoryEval - HSIImagesBands
HSISensoryEval.hsiImagesBands = relationship("HSIImagesBands", back_populates="hsiSensoryEval", cascade="all, delete-orphan")
HSIImagesBands.hsiSensoryEval = relationship("HSISensoryEval", back_populates="hsiImagesBands")

# SpectralInfo - HSIImagesBands
SpectralInfo.hsiImagesBands = relationship("HSIImagesBands", back_populates="spectralInfo", cascade="all, delete-orphan")
HSIImagesBands.spectralInfo = relationship("SpectralInfo", back_populates="hsiImagesBands")

# HSISensoryEval - AI_HSISensoryEval
HSISensoryEval.aiHSISensoryEvals = relationship("AI_HSISensoryEval", back_populates="hsiSensoryEval", cascade="all, delete-orphan")
AI_HSISensoryEval.hsiSensoryEval = relationship("HSISensoryEval", back_populates="aiHSISensoryEvals")

# GradeInfo - AI_HSISensoryEval
GradeInfo.aiHSISensoryEvals = relationship("AI_HSISensoryEval", back_populates="gradeInfo")
AI_HSISensoryEval.gradeInfo = relationship("GradeInfo", back_populates="aiHSISensoryEvals")

# HSISensoryEval - HSIImagesBands (누락된 relationship 추가)
HSISensoryEval.hsiImagesBands = relationship("HSIImagesBands", back_populates="hsiSensoryEval", cascade="all, delete-orphan")
HSIImagesBands.hsiSensoryEval = relationship("HSISensoryEval", back_populates="hsiImagesBands")

# SpectralInfo - HSIImagesBands (누락된 relationship 추가)
SpectralInfo.hsiImagesBands = relationship("HSIImagesBands", back_populates="spectralInfo", cascade="all, delete-orphan")
HSIImagesBands.spectralInfo = relationship("SpectralInfo", back_populates="hsiImagesBands")

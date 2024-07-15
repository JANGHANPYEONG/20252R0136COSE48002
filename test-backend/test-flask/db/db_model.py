# DB Model Config File
import sqlalchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
    Boolean,
    CheckConstraint, create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, scoped_session, sessionmaker

from utils import *

Base = declarative_base()


def initialize_db(app):
    try:
        # 1. DB Engine 생성
        engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
        # 2. 생성한 DB 엔진에 세션 연결
        db_session = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )
        # 3. Default 쿼리 설정
        Base.query = db_session.query_property()
        # 4. 모든 테이블 생성
        Base.metadata.create_all(bind=engine)
        # 5. DB 초기 데이터 설정
        load_initial_data(db_session)

        # db_session을 current_app에 추가
        app.db_session = db_session

        app.logger.info("Database connected successfully.")
    except Exception as e:
        app.logger.error(f"Error connecting to the database: {e}")
        raise
    else:
        print("Connect DB OKAY")
    # 6. db_session을 반환해 DB 세션 관리
    return db_session


# SET UP CONTROLLER
def load_initial_data(db_session):
    """
    초기 데이터 셋업 function
    """
    # 1. Specie
    for id, specie in enumerate(species):
        if not SpeciesInfo.query.get(id):
            temp = SpeciesInfo(id=id, value=specie)  # 0: Cattle, 1: Pig
            db_session.add(temp)
    db_session.commit()

    # 2. Cattle
    for id, large in enumerate(cattleLarge):
        for s_id, small in enumerate(cattleSmall[id]):
            index = calId(id, s_id, CATTLE)
            if not CategoryInfo.query.get(index):
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
            if not CategoryInfo.query.get(index):
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
        if not UserTypeInfo.query.get(id):
            temp = UserTypeInfo(id=id, name=Type)
            db_session.add(temp)
    db_session.commit()

    # 5. GradeNum
    for id, Type in gradeNum.items():
        if not GradeInfo.query.get(id):
            temp = GradeInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()

    # 6. SexType
    for id, Type in sexType.items():
        if not SexInfo.query.get(id):
            temp = SexInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()

    # 7. StatusType
    for id, Type in statusType.items():
        if not StatusInfo.query.get(id):
            temp = StatusInfo(id=id, value=Type)
            db_session.add(temp)
    db_session.commit()
    
    # 8. User
    default_user = User.query.get(default_user_id)

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
    
    speciesInfos = relationship("SpeciesInfo", backref="speciesInfoCategories")


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
        default=True, 
        server_default=sqlalchemy.sql.expression.false()
    )  # 유저 알람 허용 여부
    type = Column(Integer, nullable=False)  # 유저 타입 ID
    __table_args__ = (
        ForeignKeyConstraint(
            ["type"], ["userType_info.id"],
            onupdate="CASCADE"
        ),
    )
    userTypeInfos = relationship("UserTypeInfo", backref="userTypeInfos")


class Meat(Base):
    __tablename__ = "meat"
    # 1. 기본 정보
    id = Column(String(255), primary_key=True)  # 육류 관리번호
    userId = Column(
        String(255),
        nullable=False, 
        default=True,
        server_default=default_user_id
    )  # 생성한 유저 ID
    sexType = Column(Integer)  # 성별 ID
    categoryId = Column(
        Integer, ForeignKey("category_info.id"), nullable=False
    )  # 육종 ID
    gradeNum = Column(Integer)  # 등급 ID
    statusType = Column(Integer, default=True, server_default='0')  # 승인 여부 ID

    # 2. 육류 Open API 정보
    createdAt = Column(DateTime, nullable=False)  # 육류 관리번호 생성 시간
    traceNum = Column(String(255), nullable=False)  # 이력번호(혹은 묶은 번호)
    farmAddr = Column(String(255))  # 농장 주소
    farmerNm = Column(String(255))  # 농장주 이름
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
    users = relationship("User", backref="userMeats")
    categoryInfos = relationship("CategoryInfo", backref="categoryInfoMeats")
    gradeInfos = relationship("GradeInfo", backref="gradeInfoMeats")
    sexInfos = relationship("SexInfo", backref="sexInfoMeats")
    statusInfos = relationship("StatusInfo", backref="statusInfoMeats")


class DeepAgingInfo(Base):
    __tablename__ = "deepAging_info"
    
    # 1. 복합키 설정
    id = Column(
        String(255),
        primary_key=True,
    )  # 육류 관리번호
    seqno = Column(Integer, primary_key=True)  # 가공 횟수
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
    
    meats = relationship("Meat", backref="MeatdeepAgingInfos")

    
class SensoryEval(Base):
    __tablename__ = "sensory_eval"

    # 1. 복합키 설정
    id = Column(
        String(255),
        ForeignKey("meat.id"),
        primary_key=True,
    )  # 육류 관리번호
    seqno = Column(Integer, primary_key=True)  # 가공 횟수

    # 2. 관능검사 메타 데이터
    createdAt = Column(DateTime, nullable=False)  # 관능검사 생성 시간
    userId = Column(
        String(255), 
        nullable=False, 
        default=True, 
        server_default=default_user_id
    )  # 관능검사 생성한 유저 ID
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    imagePath = Column(String(255))  # 관능검사 이미지 경로

    # 3. 관능검사 측정 데이터
    marbling = Column(Float)
    color = Column(Float)
    texture = Column(Float)
    surfaceMoisture = Column(Float)
    overall = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], ["deepAging_info.id", "deepAging_info.seqno"],
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
    
    users = relationship("User", backref="userSensoryEvals")
    deepAgingInfos = relationship("DeepAgingInfo", backref="deepAgingInfoSensoryEvals")
    
    
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
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], ["sensory_eval.id", "sensory_eval.seqno"],
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
    
    SensoryEvals = relationship("SensoryEval", backref="aiSensoryEvals")
    gradeInfos = relationship("GradeInfo", backref="gradeInfoAiSensoryEvals")
    

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
        default=True,
        server_default=default_user_id
    )
    period = Column(Integer, nullable=False)  # 도축일로부터 경과된 시간
    imagePath = Column(String(255), nullable=True)  # 가열육 관능검사 이미지 경로

    # 3. 관능검사 측정 데이터
    flavor = Column(Float)
    juiciness = Column(Float)
    tenderness = Column(Float)
    umami = Column(Float)
    palatability = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], 
            ["deepAging_info.id", "deepAging_info.seqno"],
            ondelete='CASCADE', 
            onupdate='CASCADE'
        ),
        ForeignKeyConstraint(
            ["userId"], 
            ["user.userId"], 
            ondelete='SET DEFAULT', 
            onupdate='CASCADE'
        ),
        CheckConstraint('"period" >= 0', name="check_period_value"),
        CheckConstraint('"flavor" >= 1 and "flavor" <= 10', name="check_flavor_stat"),
        CheckConstraint('"juiciness" >= 1 and "juiciness" <= 10', name="check_juiciness_stat"),
        CheckConstraint('"tenderness" >= 1 and "tenderness" <= 10', name="check_tenderness_stat"),
        CheckConstraint('"umami" >= 1 and "umami" <= 10', name="check_umami_stat"),
        CheckConstraint('"palatability" >= 1 and "palatability" <= 10', name="check_palatability_stat")
    )
    
    users = relationship("User", backref="userHeatedmeatSensoryEvals")
    deepAgingInfos = relationship("DeepAgingInfo", backref="deepAgingHeatedmeatSensoryEvals")


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
    tenderness = Column(Float)
    umami = Column(Float)
    palatability = Column(Float)
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "seqno"),
        ForeignKeyConstraint(
            ["id", "seqno"], 
            ["heatedmeat_sensory_eval.id", "heatedmeat_sensory_eval.seqno"], 
            ondelete='CASCADE', 
            onupdate='CASCADE'
        ),
        CheckConstraint('"flavor" >= 1 and "flavor" <= 10', name="check_flavor_stat"),
        CheckConstraint('"juiciness" >= 1 and "juiciness" <= 10', name="check_juiciness_stat"),
        CheckConstraint('"tenderness" >= 1 and "tenderness" <= 10', name="check_tenderness_stat"),
        CheckConstraint('"umami" >= 1 and "umami" <= 10', name="check_umami_stat"),
        CheckConstraint('"palatability" >= 1 and "palatability" <= 10', name="check_palatability_stat")
    )
    
    heatedmeatSensoryEvals = relationship("HeatedmeatSensoryEval", backref="aiHeatedmeatSensoryEvals")


class ProbexptData(Base):
    __tablename__ = "probexpt_data"
    # 1. 복합키 설정
    id = Column(String(255), primary_key=True)
    seqno = Column(Integer, primary_key=True)
    isHeated = Column(
        Boolean, 
        primary_key=True,
        default=True,
        server_default=sqlalchemy.sql.expression.false()
    )

    # 2. 연구실 메타 데이터
    updatedAt = Column(DateTime, nullable=True)
    userId = Column(
        String(255), 
        nullable=False, 
        default=True,
        server_default=default_user_id
    )
    period = Column(Integer, nullable=True)

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
            ondelete='CASCADE', 
            onupdate='CASCADE'
        ),
        ForeignKeyConstraint(
            ['userId'],
            ['user.userId'],
            ondelete='SET DEFAULT',
            onupdate='CASCADE'
        ),
        CheckConstraint('"period" >= 0', name="check_period_value"),
        CheckConstraint('"DL" >= 0 AND "DL" <= 100', name="check_DL_percentage"),
        CheckConstraint('"CL" >= 0 AND "CL" <= 100', name="check_CL_percentage"),
        CheckConstraint('"RW" >= 0 AND "RW" <= 100', name="check_RW_percentage"),
    )
    
    users = relationship("User", backref="userProbexptDatas")
    deepAgingInfos = relationship("DeepAgingInfo", backref="deepAgingProexptDatas")
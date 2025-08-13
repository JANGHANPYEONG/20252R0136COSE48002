# 새로운 모듈 구조로 이동된 함수들 import
from .constants import *
from .logging_utils import *
from .validation import *
from .error_handlers import *

# 하위 호환성을 위한 기존 함수들 유지
def item_encoder(data_dict, item, input_data=None):
    """
    레거시 함수 - 데이터 인코딩 및 변환
    """
    datetime0_cvr = ["filmedAt", "createdAt"]
    datetime1_cvr = ["loginAt", "updatedAt"]
    datetime2_cvr = ["butcheryYmd", "birthYmd", "date"]
    str_cvr = [
        "id",
        "userId",
        "traceNum",
        "farmAddr",
        "farmerName",
        "name",
        "company",
        "jobTitle",
        "homeAddr",
        "imagePath",
        "xai_imagePath",
        "xai_gradeNum_imagePath",
    ]
    int_cvr = ["period", "minute", "seqno", "isCompleted"]
    float_cvr = [
        "marbling",
        "color",
        "texture",
        "surfaceMoisture",
        "overall",
        "flavor",
        "juiciness",
        "umami",
        "palatability",
        "L",
        "a",
        "b",
        "DL",
        "CL",
        "RW",
        "ph",
        "WBSF",
        "cardepsin_activity",
        "MFI",
        "Collagen",
        "sourness",
        "bitterness",
        "richness",
    ]
    json_cvr = ["tenderness"]
    bool_cvr = ["alarm", "isHeated"]
    
    if item in datetime0_cvr:
        data_dict[item] = convert_to_datetime(data_dict.get(item), 0)
    elif item in datetime1_cvr:
        data_dict[item] = convert_to_datetime(data_dict.get(item), 1)
    elif item in datetime2_cvr:
        data_dict[item] = convert_to_datetime(data_dict.get(item), 2)
    elif item in str_cvr:
        data_dict[item] = safe_str(data_dict.get(item))
    elif item in int_cvr:
        data_dict[item] = safe_int(data_dict.get(item))
    elif item in float_cvr:
        data_dict[item] = safe_float(data_dict.get(item))
    elif item in json_cvr:
        data_dict[item] = safe_json(data_dict.get(item))
    elif item in bool_cvr:
        data_dict[item] = safe_bool(data_dict.get(item))
    else:
        data_dict[item] = input_data


def calId(id, s_id, type):
    """
    category id 계산 함수
    Params
    1. id: 대분할 인덱스
    2. s_id: 소분할 인덱스
    3. type: 종 인덱스
    """
    return 100 * type + 10 * id + s_id


def to_dict(model_instance, query_instance=None):
    """
    SQLAlchemy 모델을 딕셔너리로 변환
    """
    if hasattr(model_instance, "__table__"):
        return {
            c.name: getattr(model_instance, c.name)
            for c in model_instance.__table__.columns
        }
    else:
        cols = query_instance.column_descriptions
        return {cols[i]["name"]: model_instance[i] for i in range(len(cols))}


def transfer_folder_image(s3_conn, firestore_conn, db_session, id, new_meat, folder):
    """
    Firebase Storage -> S3 이미지 전송
    Params
    1. id: meat.id
    2. new_meat: New Meat data object
    Return
    None
    """
    try:
        if not firestore_conn.firestorage2server(
            f"{folder}", id
        ) or not s3_conn.server2s3(f"{folder}", id):
            new_meat.imagePath = None
            raise Exception("Failed to transfer meat image")

        new_meat.imagePath = s3_conn.get_image_url(s3_conn.bucket, f"{folder}/{id}")
        db_session.merge(new_meat)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise Exception(e)

# 하위 호환성을 위한 별칭들
species = SPECIES
cattleLarge = CATTLE_LARGE_PARTS
pigLarge = PIG_LARGE_PARTS
cattleSmall = CATTLE_SMALL_PARTS
pigSmall = PIG_SMALL_PARTS
regions = [
    "강원",
    "경기",
    "경상남",
    "경상북",
    "광주",
    "대구",
    "대전",
    "부산",
    "서울",
    "세종",
    "울산",
    "인천",
    "전라남",
    "전라북",
    "제주",
    "충청남",
    "충청북",
]
usrType = {0: "Normal", 1: "Researcher", 2: "Manager", 3: None}
sexType = {0: "수", 1: "암", 2: "거세", 3: None}
gradeNum = {0: "1++", 1: "1+", 2: "1", 3: "2", 4: "3", 5: None}
statusType = {0: "대기중", 1: "반려", 2: "승인"}
CATTLE = 0
PIG = 1
default_user_id = DEFAULT_USER_ID
default_user_type = DEFAULT_USER_TYPE
convert2datetime = convert_to_datetime

import glob
import pprint
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import uuid
import hashlib
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
from sqlalchemy import func, create_engine
import json
from utils import *

from .db_model import *

db = SQLAlchemy()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def find_id(species_value, primal_value, secondary_value, db_session):
    """
    category id 지정 function
    Params
    1. specie_value: "cattle" or "pig
    2. primal_value: "대분할 부위"
    3. secondary_value: "소분할 부위"
    4. db: 세션 db

    Return
    1. Category.id
    """
    # Find specie using the provided specie_value
    specie = db_session.query(SpeciesInfo).filter_by(value=species_value).first()

    # If the specie is not found, return an appropriate message
    if not specie:
        raise Exception("Invalid species data")

    # Find category using the provided primal_value, secondary_value, and the specie id
    category = (
        db_session.query(CategoryInfo)
        .filter_by(
            primalValue=primal_value,
            secondaryValue=secondary_value,
            speciesId=specie.id,
        )
        .first()
    )

    # If the category is not found, return an appropriate message
    if not category:
        raise Exception("Invalid primal or secondary value")

    # If everything is fine, return the id of the found category
    return category.id


def decode_id(id, db_session):
    result = {"specie_value": None, "primal_value": None, "secondary_value": None}
    category = db_session.query(CategoryInfo).filter_by(id=id).first()
    specie = db_session.query(SpeciesInfo).filter_by(id=category.speciesId).first()
    result["specie_value"] = specie.value
    result["primal_value"] = category.primalValue
    result["secondary_value"] = category.secondaryValue
    return result["specie_value"], result["primal_value"], result["secondary_value"]

def calculate_period(db_session, id):
    butchery = db_session.query(Meat).get(id).butcheryYmd
    current = datetime.now()
    
    diff = current - butchery
    return diff.days


def calculate_period(db_session, id):
    butchery_date = db_session.query(Meat).get(id).butcheryYmd
    current_date = datetime.now()
    
    diff = current_date - butchery_date
    return diff.days


# CREATE
def create_meat(db_session, meat_data: dict):
    # 1. SexType 테이블에서 성별 정보 ID 가져오기
    sex_type = db_session.query(SexInfo).filter_by(value=meat_data.get("sexType")).first()

    # 2. GradeNum 테이블에서 등급 정보 ID 가져오기
    grade_num = (
        db_session.query(GradeInfo).filter_by(value=meat_data.get("gradeNum")).first()
    )
    # 3. meat_data에 없는 not null 필드 추가
    meat_data['createdAt'] = datetime.now().strftime('%Y-%m-%d')
    
    # 4, meat_data에 있는 필드 수정
    meat_data['id'] = meat_data.pop('meatId')
    for field in list(meat_data.keys()):
        if field == "sexType":
            try:
                item_encoder(meat_data, field, sex_type.id)
            except Exception as e:
                raise Exception("Invalid sex_type id")
        elif field == "gradeNum":
            try:
                item_encoder(meat_data, field, grade_num.id)
            except Exception as e:
                raise Exception("Invalid grade_num id")
        elif (
            field == "specieValue"
            or field == "primalValue"
            or field == "secondaryValue"
        ):
            item_encoder(
                meat_data,
                "categoryId",
                find_id(
                    meat_data.get("specieValue"),
                    meat_data.get("primalValue"),
                    meat_data.get("secondaryValue"),
                    db_session,
                ),
            )
        else:
            item_encoder(meat_data, field)

    # 5. meat_data에 없어야 하는 필드 삭제
    meat_data.pop("specieValue")
    meat_data.pop("primalValue")
    meat_data.pop("secondaryValue")

    # Create a new Meat object
    try:
        new_meat = Meat(**meat_data)
    except Exception as e:
        raise Exception("Wrong meat DB field items" + str(e))
    return new_meat


def create_DeepAging(meat_data: dict):
    if meat_data is None:
        raise Exception("Invalid Deep Aging meat_data")
    for field in meat_data.keys():
        item_encoder(meat_data, field)
    meat_data["deepAgingId"] = str(uuid.uuid4())
    try:
        new_deepAging = DeepAgingInfo(**meat_data)
    except Exception as e:
        raise Exception("Wrong DeepAging DB field items: " + str(e))
    return new_deepAging


def create_SensoryEval(db_session, meat_data: dict, sensory_data, seqno, id, userId):
    """
    db: SQLAlchemy db
    freshmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    freshmeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    # 1. freshmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    meat_data['id'] = id
    meat_data.pop('meatId')
    meat_data['createdAt'] = datetime.now().strftime('%Y-%m-%d')
    meat_data['period'] = calculate_period(db_session, id)
    meat_data.pop('sensoryData')
    meat_data['userId'] = userId
    
    for field, val in sensory_data.items():
        meat_data[field] = val

    # 2. freshmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_sensory_eval = SensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong sensory eval DB field items" + str(e))
    return new_sensory_eval


def create_HeatemeatSensoryEval(sensory_data: dict, id: str, seqno: int):
    """
    db: SQLAlchemy db
    heatedmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    heatedMeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    # 1. heatedmeat_data에 없는 필드 추가
    sensory_data["id"] = id
    sensory_data["seqno"] = seqno
    # 2. heatedmeat_data에 있는 필드 수정
    for field in sensory_data.keys():
        item_encoder(sensory_data, field)

    # Create a new Meat object
    try:
        new_heatedmeat = HeatedmeatSensoryEval(**sensory_data)
        return new_heatedmeat
    except Exception as e:
        raise Exception("Wrong heatedmeat sensory eval DB field items" + str(e))


def create_ProbexptData(probexpt_data: dict, id: str, seqno: int, is_heated: bool):
    """
    db: SQLAlchemy db
    probexpt_data: 실험실 데이터
    id: 원육 id
    seqno: 처리육의 seqno
    is_heated: 가열/비가열 여부
    """
    # 1. probexpt_data에 없는 필드 추가
    probexpt_data["id"] = id
    probexpt_data["seqno"] = seqno
    probexpt_data["isHeated"] = is_heated

    # 2. probexpt_data에 있는 필드 수정
    for field in probexpt_data.keys():
        item_encoder(probexpt_data, field)

    # Create a new Probexpt object
    try:
        new_probexpt_data = ProbexptData(**probexpt_data)
        return new_probexpt_data
    except Exception as e:
        raise Exception("Wrong probexpt data DB field items" + str(e))


# API MiddleWare
def create_specific_std_meat_data(db_session, s3_conn, firestore_conn, data, meat_id, is_post):
    try:
        if is_post:
            # 1. DB merge
            new_meat = create_meat(db_session=db_session, meat_data=data)
            new_meat.statusType = 0
            
            db_session.merge(new_meat)
            db_session.commit()
            
            # 2. Firestore -> S3
            transfer_folder_image(
                s3_conn=s3_conn,
                firestore_conn=firestore_conn,
                db_session=db_session,
                id=meat_id,
                new_meat=new_meat,
                folder="qr_codes",
            )

        else: 
            existing_meat = db_session.query(Meat).get(meat_id)
            if existing_meat.statusType == 2:
                return None
                
            new_category = db_session.query(CategoryInfo).filter(
                CategoryInfo.primalValue == data.get("primalValue"),
                CategoryInfo.secondaryValue == data.get("secondaryValue")
            ).first()
            existing_meat.categoryId = new_category.id
            
            db_session.add(existing_meat)
            db_session.commit()

    except Exception as e:
        db_session.rollback()
        raise e

    return meat_id


def create_raw_meat_deep_aging_info(db_session, meat_id, seqno):
    new_meat = db_session.query(Meat).get(meat_id)
    new_deep_aging = {
        "id": meat_id,
        "seqno": seqno,
        "date": new_meat.createdAt,
        "minute": 0
    }
    try:
        deep_aging_data = DeepAgingInfo(**new_deep_aging)
        db_session.add(deep_aging_data)
        db_session.commit()
        return f"{meat_id}-{seqno}"
    except Exception as e:
        db_session.rollback()
        raise e


def create_specific_deep_aging_data(db_session, data):
    # 2. 기본 데이터 받아두기
    id = data["meatId"]
    seqno = data["seqno"]

    meat = db_session.query(Meat).get(id) # DB에 있는 육류 정보
    deep_aging = db_session.query(DeepAgingInfo).filter_by(id=id, seqno=seqno).first() # DB에 있는 딥에이징 정보
    if not meat:
        return None
    if deep_aging:
        return False
    
    new_deep_aging = {
        "id": id,
        "seqno": seqno,
        "date": data["deepAging"]["date"],
        "minute": data["deepAging"]["minute"]
    }
    try:
        deep_aging_data = DeepAgingInfo(**new_deep_aging)
        db_session.add(deep_aging_data)
        db_session.commit()
        return f"{id}-{seqno}"
    except Exception as e:
        db_session.rollback()
        raise e


def create_specific_sensory_eval(db_session, s3_conn, firestore_conn, data, is_post):
    # 기본 데이터 받아오기
    meat_id = safe_str(data.get("meatId"))
    seqno = safe_int(data.get("seqno"))
    need_img = safe_bool(data.get("imgAdded"))
    data.pop('imgAdded')
    sensory_data = data.get("sensoryData")

    # meat_id가 넘어오지 않았을 때 / 없는 meat_id일 때
    if not meat_id:
        return {"msg": "No Meat ID data sent", "code": 400}
    
    meat = db_session.query(Meat).get(meat_id)
    if not meat:
        return {"msg": "Meat Data Does Not Exist", "code": 400}
    
    # 해당 회차의 deepAging_info 레코드가 존재하는지 확인
    deep_aging = db_session.query(DeepAgingInfo).filter_by(id=meat_id, seqno=seqno).first()
    if not deep_aging:
        return {"msg": "Deep Aging Info Does Not Exist", "code": 400}
    
    existing_sensory = db_session.query(SensoryEval).filter_by(id=meat_id, seqno=seqno).first()
    # POST 요청
    try:
        if is_post:
            # 기존 관능 평가 데이터가 존재할 때 에러 처리
            if existing_sensory:
                return {"msg": f"Sensory Evaluation Already Exists {meat_id}-{seqno}", "code": 400}
            
            user_id = safe_str(data.get("userId"))
            # sensory_eval 생성
            if any(value is not None for value in sensory_data.values()):
                new_sensory_eval = create_SensoryEval(db_session, data, sensory_data, seqno, meat_id, user_id)
                db_session.add(new_sensory_eval)
                db_session.commit()

                if need_img:
                    transfer_folder_image(
                        s3_conn,
                        firestore_conn,
                        db_session,
                        f"{meat_id}-{seqno}",
                        new_sensory_eval,
                        "sensory_evals",
                    )
                db_session.commit()
                return {"msg": f"Success to Create Sensory Evaluation {meat_id}-{seqno}", "code": 200}
            else:
                return {"msg": f"No Sensory Data to Create Sensory Evaluation", "code": 400}
        # PATCH 요청
        else:
            # 기존 관능 평가 데이터가 존재하지 않을 때 에러 처리
            if not existing_sensory:
                return {"msg": f"Sensory Evaluation Does Not Exist {meat_id}-{seqno}", "code": 400}
            
            existing_user = existing_sensory.userId
            if seqno == 0:
                if meat.statusType == 2:
                    return {"msg": "Already Confirmed Meat", "code": 400}
                meat.statusType == 0
                db_session.merge(meat)
                db_session.commit()
                
            # sensory_eval 생성
            if any(value is not None for value in sensory_data.values()):
                new_sensory_eval = create_SensoryEval(db_session, data, sensory_data, seqno, meat_id, existing_user)
                db_session.merge(new_sensory_eval)

                if need_img:
                    transfer_folder_image(
                        s3_conn,
                        firestore_conn,
                        db_session,
                        f"{meat_id}-{seqno}",
                        new_sensory_eval,
                        "sensory_evals",
                    )
                db_session.commit()
                return {"msg": f"Success to Update Sensory Evaluation {meat_id}-{seqno}", "code": 200}
            else:
                return {"msg": f"No Sensory Data to Update Sensory Evaluation", "code": 400}
    except Exception as e:
        db_session.rollback()
        raise e


def create_specific_heatedmeat_seonsory_eval(db_session, firestore_conn, s3_conn, data, is_post):
    # 2. 기본 데이터 받아두기
    id = data["meatId"]
    seqno = data["seqno"]
    need_img = data["imgAdded"]

    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    deep_aging_info = get_DeepAging(db_session, id, seqno)
    if not (meat and deep_aging_info):
        return ({"msg": "Meat or Deep Aging Data Does NOT Exists", "code": 400})
    
    try:
        sensory_data = data["heatedmeatSensoryData"]
        sensory_data["filmedAt"] = data["filmedAt"]
        sensory_data["createdAt"] = convert2string(datetime.now(), 1)
        existed_sensory_data = get_HeatedmeatSensoryEval(db_session, id, seqno)

        if existed_sensory_data: # 수정
            if is_post: # 수정인데 POST 메서드
                return ({"msg": "Heatedmeat Sensory Data Already Exists", "code": 400})
            
            if seqno == 0 and meat.statusType == 2:
                return ({"msg": "Already Confirmed Data", "code": 400})
            elif seqno == 0 and meat.statusType != 2:
                meat.statusType = 0
                db_session.merge(meat)
            sensory_data["userId"] = existed_sensory_data["userId"]
            new_sensory_data = create_HeatemeatSensoryEval(sensory_data, id, seqno)
            db_session.merge(new_sensory_data)
            
        else: # 생성
            if not is_post: # 생성인데 PATCH 메서드
                return ({"msg": "Heatedmeat Sensory Data Does NOT Exists", "code": 400})
            sensory_data["userId"] = data["userId"]
            sensory_data["period"] = calculate_period(db_session, id)
            new_sensory_data = create_HeatemeatSensoryEval(sensory_data, id, seqno)
            db_session.add(new_sensory_data)

        if need_img:
            transfer_folder_image(
                s3_conn,
                firestore_conn,
                db_session,
                f"{id}-{seqno}",
                new_sensory_data,
                "heatedmeat_sensory_evals",
            )
        db_session.commit()
        return ({"msg": f"Success to {'POST' if is_post else 'PATCH'} Heatedmeat Sensory Data {id}-{seqno}", "code": 200})
    except Exception as e:
        db_session.rollback()
        raise e


def create_specific_probexpt_data(db_session, data, is_post):
    # 2. 기본 데이터 받아두기
    id = data["meatId"]
    seqno = data["seqno"]
    is_heated = data["isHeated"]

    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    deep_aging_info = get_DeepAging(db_session, id, seqno)
    if not (meat and deep_aging_info):
        return ({"msg": "Meat or Deep Aging Data Does NOT Exists", "code": 400})
    
    try:
        probexpt_data = data["probexptData"]
        probexpt_data["updatedAt"] = convert2string(datetime.now(), 1)
        existed_probexpt_data = get_ProbexptData(db_session, id, seqno, is_heated)

        if existed_probexpt_data: # 수정
            if is_post: # 수정이지만 POST 메서드
                return ({"msg": "Probexpt Data Already Exists", "code": 400})
            
            if seqno == 0 and meat.statusType == 2:
                return ({"msg": "Already Confirmed Data", "code": 400})
            elif seqno == 0 and meat.statusType != 2:
                meat.statusType = 0
                db_session.merge(meat)
            probexpt_data["userId"] = existed_probexpt_data["userId"]
            new_probexpt_data = create_ProbexptData(probexpt_data, id, seqno, is_heated)
            db_session.merge(new_probexpt_data)
            db_session.commit()
            return ({"msg": f"Success to PATCH Probexpt Data {id}-{seqno}-{'heated' if is_heated else 'unheated'}", "code": 200})
        else: # 생성
            if not is_post: # 생성이지만 PATCH 메서드
                return ({"msg": "Probexpt Data Does NOT Exists", "code": 400})
            probexpt_data["userId"] = data["userId"]
            probexpt_data["period"] = calculate_period(db_session, id)
            new_probexpt_data = create_ProbexptData(probexpt_data, id, seqno, is_heated)
            db_session.add(new_probexpt_data)
            db_session.commit()
            return ({"msg": f"Success to POST Probexpt Data {id}-{seqno}-{'heated' if is_heated else 'unheated'}", "code": 200})
    except Exception as e:
        db_session.rollback()
        raise e

# GET
def get_meat(db_session, id):
    # 1. 원육 데이터 조회
    meat = db_session.query(Meat).filter_by(id = id).first()

    if meat is None:
        return None
    result = to_dict(meat)
    result['meatId'] = result.pop('id')
    sexType = db_session.query(SexInfo).filter_by(id = result["sexType"]).first()
    gradeNum = db_session.query(GradeInfo).filter_by(id = result["gradeNum"]).first()
    statusType = (
        db_session.query(StatusInfo)
        .filter_by(id = result["statusType"])
        .first()
    )
    
    # 2. 참조관계 또는 날짜 데이터 형식 변환
    result["sexType"] = sexType.value
    (
        result["specieValue"],
        result["primalValue"],
        result["secondaryValue"],
    ) = decode_id(result["categoryId"], db_session)
    del result["categoryId"]

    result["gradeNum"] = gradeNum.value
    result["statusType"] = statusType.value
    result["createdAt"] = convert2string(result["createdAt"], 1)
    result["butcheryYmd"] = convert2string(result["butcheryYmd"], 2)
    result["birthYmd"] = convert2string(result["birthYmd"], 2)

    # 3. 유저 정보 추가
    user = get_user(db_session, meat.userId)
    result["userName"] = user.name
    result["userType"] = usrType[user.type]
    result["company"] = user.company

    # 4. 딥에이징 정보 - 관능데이터, 실험실데이터
    number_of_deep_aging_data = (db_session.query(func.max(DeepAgingInfo.seqno))
                                 .filter_by(id = id)
                                 .scalar())
    if number_of_deep_aging_data is None:
        number_of_deep_aging_data = -1
    result["deepAgingInfo"] = []
    for sequence in range(0, number_of_deep_aging_data + 1):
        deep_aging_data = get_DeepAging(db_session, id, sequence)
        if not deep_aging_data:
            continue
        result["deepAgingInfo"].append({
            "date": convert2string(deep_aging_data.date, 2) if sequence != 0 and deep_aging_data else None,
            "minute": deep_aging_data.minute if sequence != 0 and deep_aging_data else None,
            "seqno": f"{sequence}",
            "sensory_eval": get_SensoryEval(db_session, id, sequence),
            "heatedmeat_sensory_eval": get_HeatedmeatSensoryEval(db_session, id, sequence),
            "probexpt_data": get_ProbexptData(db_session, id, sequence, False),
            "heatedmeat_probexpt_data": get_ProbexptData(db_session, id, sequence, True),
        })

    return result


def get_SensoryEval(db_session, id, seqno):
    sensory_eval_data = (
        db_session.query(SensoryEval)
        .filter(
            SensoryEval.id == id,
            SensoryEval.seqno == seqno,
        )
        .first()
    )
    if sensory_eval_data:
        sensory_eval = to_dict(sensory_eval_data)
        sensory_eval["meatId"] = sensory_eval.pop("id")
        sensory_eval["filmedAt"] = convert2string(sensory_eval["filmedAt"], 1)
        sensory_eval["createdAt"] = convert2string(sensory_eval["createdAt"], 1)
        sensory_eval["userName"] = get_user(db_session, sensory_eval["userId"]).name
        return sensory_eval
    else:
        return None


def get_DeepAging(db_session, id, seqno):
    deep_aging_data = (
        db_session.query(DeepAgingInfo)
        .filter(
            DeepAgingInfo.id == id,
            DeepAgingInfo.seqno == seqno,
        )
        .first()
    )
    return deep_aging_data


def get_HeatedmeatSensoryEval(db_session, id, seqno):
    heated_meat_data = (
        db_session.query(HeatedmeatSensoryEval)
        .filter(
            HeatedmeatSensoryEval.id == id,
            HeatedmeatSensoryEval.seqno == seqno,
        )
        .first()
    )
    if heated_meat_data:
        heated_meat = to_dict(heated_meat_data)
        heated_meat["meatId"] = heated_meat.pop("id")
        heated_meat["filmedAt"] = convert2string(heated_meat["filmedAt"], 1)
        heated_meat["createdAt"] = convert2string(heated_meat["createdAt"], 1)
        heated_meat["userName"] = get_user(db_session, heated_meat["userId"]).name
        # del heated_meat["imagePath"]
        return heated_meat
    else:
        return None


def get_ProbexptData(db_session, id, seqno, is_heated):
    probexpt_data = (
        db_session.query(ProbexptData)
        .filter(
            ProbexptData.id == id,
            ProbexptData.seqno == seqno,
            ProbexptData.isHeated == is_heated,
        )
        .first()
    )
    if probexpt_data:
        probexpt = to_dict(probexpt_data)
        probexpt["meatId"] = probexpt.pop("id")
        probexpt["updatedAt"] = convert2string(probexpt["updatedAt"], 1)
        probexpt["userName"] = get_user(db_session, probexpt["userId"]).name
        del probexpt["isHeated"]
        return probexpt
    else:
        return None


def get_range_meat_data(
    db_session,
    offset,
    count,
    start=None,
    end=None,
    specie_value=None,
    farmAddr=None,
    userId=None,
    type=None,
    createdAt=None,
    statusType=None,
    company=None,
):
    if (count is not None) and (offset is not None):
        count = safe_int(count)
        offset = safe_int(offset)
        offset = offset*count
    start = convert2datetime(start, 0)
    end = convert2datetime(end, 0)

    # Base Query
    query = db_session.query(Meat)

    if specie_value != 2:
        query = query.join(CategoryInfo).filter(CategoryInfo.speciesId == specie_value)

    # Sorting and Filtering
    # if farmAddr is not None:
    #     if farmAddr:  # true: 가나다순 정렬
    #         query = query.order_by(Meat.farmAddr.asc())
    #     else:  # false: 역순
    #         query = query.order_by(Meat.farmAddr.desc())
    # if userId is not None:
    #     if userId:  # true: 알파벳 오름차순 정렬
    #         query = query.order_by(Meat.userId.asc())
    #     else:  # false: 알파벳 내림차순 정렬
    #         query = query.order_by(Meat.userId.desc())
    # if type is not None:
    #     if type:  # true: 숫자 오름차순 정렬
    #         query = query.order_by(User.type.asc())
    #     else:  # false: 숫자 내림차순 정렬
    #         query = query.order_by(User.type.desc())
    # if company is not None:
    #     if company:  # true: 가나다순 정렬
    #         query = query.order_by(User.company.asc())
    #     else:  # false: 역순
    #         query = query.order_by(User.company.desc())
    # if createdAt is not None:
    #     if createdAt:  # true: 최신순
    #         query = query.order_by(Meat.createdAt.desc())
    #     else:  # false: 역순
    #         query = query.order_by(Meat.createdAt.asc())
    # if statusType is not None:
    #     if statusType:  # true: 숫자 오름차순 정렬
    #         query = query.order_by(Meat.statusType.asc())
    #     else:  # false: 숫자 내림차순 정렬
    #         query = query.order_by(Meat.statusType.desc())

    # 기간 설정 쿼리
    db_total_len = query.count()
    if start is not None and end is not None:
        query = query.filter(Meat.createdAt.between(start, end))
        db_total_len = query.filter(
            Meat.createdAt.between(start, end)
        ).count()
    query = query.order_by(Meat.createdAt.desc())
    if (count is not None) and (offset is not None):
        query = query.offset(offset).limit(count)

    # 탐색
    meat_data = query.all()
    meat_result = {}
    id_result = [data.id for data in meat_data]
    for id in id_result:
        meat_result[id] = get_meat(db_session, id)
        userTemp = get_user(db_session, meat_result[id].get("userId"))
        if userTemp:
            meat_result[id]["userName"] = userTemp.name
            meat_result[id]["company"] = userTemp.company
            meat_result[id]["userType"] = usrType[userTemp.type]
        else:
            meat_result[id]["userName"] = userTemp
            meat_result[id]["company"] = userTemp
            meat_result[id]["userType"] = userTemp
        del meat_result[id]["deepAgingInfo"]

    result = {
        "DB Total len": db_total_len,
        "id_list": id_result,
        "meat_dict": meat_result,
    }

    return result


# UPDATE

# DELETE
def delete_user(db_session, user):
    try:
        # 로컬 데이터베이스에서 유저 삭제
        db_session.delete(user)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise Exception(str(e))


# USER
def create_user(db_session, user_data: dict):
    try:
        for field, value in user_data.items():
            if field == "type":
                user_type = db_session.query(UserTypeInfo).filter_by(name=value).first()
                if user_type:  # check if user_type exists
                    item_encoder(user_data, field, user_type.id)
                else:
                    item_encoder(user_data, field, 3)
            else:
                item_encoder(user_data, field)
        new_user = User(**user_data)

        db_session.add(new_user)
        db_session.commit()
    except Exception as e:
        raise Exception(str(e))


def update_user(db_session, user_data: dict):
    try:
        user_id = user_data.get("userId")
        history = (
            db_session.query(User).filter_by(userId=user_id).first()
        )
        # 1. 기존 유저 없음
        if not history:
            return jsonify({"message": f"No User ID {user_id}"}), 400

        # 2. 기존 유저 있음
        for field, value in user_data.items():
            if field == "type":
                user_type = db_session.query(UserTypeInfo).filter_by(name=value).first()
                if user_type:  # check if user_type exists
                    item_encoder(user_data, field, user_type.id)
                else:
                    item_encoder(user_data, field, 3)

            else:
                item_encoder(user_data, field)

        for attr, value in user_data.items():
            setattr(history, attr, value)

        db_session.merge(history)
        db_session.commit()
        return history

    except Exception as e:
        db_session.rollback()
        raise Exception(str(e))

def get_all_user(db_session):
    try:
        users = db_session.query(User).all()
        for user in users:
            time = convert2datetime(user.createdAt, 1)
            user.createdAt = convert2string(time, 0)
        return users
    except Exception as e:
        raise Exception(str(e))

def get_user(db_session, user_id):
    try:
        user_data = db_session.query(User).filter(User.userId == user_id).first()
        if user_data is not None:
            time = convert2datetime(user_data.createdAt, 1)
            user_data.createdAt = convert2string(time, 0)
        return user_data
    except Exception as e:
        raise Exception(str(e))


def _get_users_by_type(db_session):
    try:
        # UserType 별로 분류될 유저 정보를 담을 딕셔너리
        user_dict = {}

        # 모든 유저 정보를 조회
        users = db_session.query(User).all()

        # 조회된 유저들에 대하여
        for user in users:
            # 해당 유저의 UserType을 조회
            user_type_info = db_session.query(UserTypeInfo).get(user.type)

            # user_type_info가 존재하지 않으면 예외를 발생시킵니다.
            if not user_type_info:
                raise Exception(f"UserTypeInfo not found for type {user.type}")

            # UserType 이름을 가져옵니다.
            user_type = user_type_info.name

            # user_dict에 해당 UserType key가 없다면, 새로운 리스트 생성
            if user_type not in user_dict:
                user_dict[user_type] = []

            # UserType에 해당하는 key의 value 리스트에 유저 id 추가
            user_dict[user_type].append(user.userId)

        return user_dict
    except Exception as e:
        raise Exception(str(e))


def _getMeatDataByUserId(db_session, userId, offset, count, start, end):
    try:
        start = convert2datetime(start, 0)
        end = convert2datetime(end, 0)
        meats = (
            db_session.query(Meat)
            .filter(
                Meat.userId == userId,
                Meat.createdAt.between(start, end)
            )
            .order_by(Meat.createdAt.desc())
            .offset(offset).limit(count)
            .all()
        )

        result = []
        if meats:
            for meat in meats:
                result.append({
                    "meatId": meat.id,
                    "createdAt": convert2string(meat.createdAt, 1),
                    "statusType": statusType[meat.statusType]
                })
            
        return {"meat_dict": result}
    except Exception as e:
        raise Exception(str(e))


def _getMeatDataByUserType(db_session, userType):
    userType_value = db_session.query(UserTypeInfo).filter_by(name=userType).first()
    if userType_value:
        userType = userType_value.id
    else:
        return (
            jsonify({"msg": "No userType in DB  (Normal, Researcher, Manager, None)"}),
            404,
        )

    # First, get all users of the given user type
    users = db_session.query(User).filter_by(type=userType).all()
    user_ids = [user.userId for user in users]

    # Then, get all meats that were created by the users of the given user type
    meats = Meat.query.filter(Meat.userId.in_(user_ids)).all()

    if meats:
        result = []
        for meat in meats:
            temp = get_meat(db_session, meat.id)
            user_temp = get_user(db_session, temp.get("userId"))
            if user_temp:
                temp["name"] = user_temp.get("name")
            else:
                temp["name"] = user_temp
            del temp["processedmeat"]
            del temp["rawmeat"]
            result.append(temp)
        return jsonify(result), 200
    else:
        return (
            jsonify({"message": "No meats found for the given userType."}),
            404,
        )


def _getMeatDataByStatusType(db_session, varified):
    meats_db = Meat.query.all()
    meat_list = []
    if varified == 2:  # 승인
        varified = "승인"
    elif varified == 1:  # 반려
        varified = "반려"
    elif varified == 0:
        varified = "대기중"
    for meat in meats_db:
        temp = get_meat(db_session, meat.id)
        del temp["processedmeat"]
        del temp["rawmeat"]
        if temp.get("statusType") == varified:
            meat_list.append(temp)
    return jsonify({f"{varified}": meat_list}), 200


def _getMeatDataByRangeStatusType(
    db_session, status_type, offset, count, specie_value, start=None, end=None
):
    status_type = safe_int(status_type)
    offset = safe_int(offset)
    count = safe_int(count)
    # Specie_value별로 Base query를 다르게 설정 - 소, 돼지, 전체
    if specie_value == '소':
        query = (
            db_session.query(Meat)
            .filter(
                Meat.statusType == status_type,
                Meat.categoryId < 100
            )
        )
    elif specie_value == '돼지':
        query = (
            db_session.query(Meat)
            .filter(
                Meat.statusType == status_type,
                Meat.categoryId >= 100
            )
        )
    else:
        query = (
            db_session.query(Meat)
            .filter(
                Meat.statusType == status_type
            )
        )

    # Date Filter
    if start and end:
        query = query.filter(
            Meat.createdAt.between(start, end)
        ).order_by(Meat.createdAt.desc())
        
        db_total_len = query.count()
    query = query.offset(offset * count).limit(count)

    result = []
    meat_data = query.all()

    for meat in meat_data:
        temp = get_meat(db_session, meat.id)
        user_temp = get_user(db_session, temp["userId"])

        if user_temp:
            temp["userName"] = user_temp.name
            temp["company"] = user_temp.company
            temp["userType"] = usrType[user_temp.type]
        else:
            temp["userName"] = user_temp
            temp["company"] = user_temp
            temp["userType"] = user_temp

        del temp["deepAgingInfo"]
        result.append(temp)

    if status_type == 2:
        status_type = "승인"
    elif status_type == 1:
        status_type = "반려"
    else:
        status_type = "대기중"
    return (
        jsonify(
            {
                "DB Total len": db_total_len,
                f"{status_type}": result,
            }
        ),
        200,
    )


def _getMeatDataByTotalStatusType(db_session):
    result = {}
    result["승인"] = _getMeatDataByStatusType("2")[0].get_json().get("승인")
    result["반려"] = _getMeatDataByStatusType("1")[0].get_json().get("반려")
    result["대기중"] = _getMeatDataByStatusType("0")[0].get_json().get("대기중")
    return jsonify(result), 200


def _getTexanomyData(db_session):
    species_all = db_session.query(SpeciesInfo).all()
    result = {}
    for species in species_all:
        categories = (
            db_session.query(CategoryInfo)
            .filter_by(speciesId=species.id)
            .all()
        )
        category_dict = {}
        for category in categories:
            if category.primalValue not in category_dict:
                category_dict[category.primalValue] = [category.secondaryValue]
            else:
                category_dict[category.primalValue].append(category.secondaryValue)

        result[species.value] = category_dict
    return jsonify(result), 200


def _getPredictionData(db_session, id, seqno):
    result = get_AI_SensoryEval(db_session, id, seqno)
    if result:
        return jsonify(result), 200
    else:
        return jsonify({"msg": "No data in AI Sensory Evaluate DB"}), 404


def get_AI_SensoryEval(db_session, id, seqno):
    ai_sensoryEval = (
        db_session.query(AI_SensoryEval)
        .filter(
            AI_SensoryEval.id == id,
            AI_SensoryEval.seqno == seqno,
        )
        .first()
    )
    if ai_sensoryEval:
        ai_sensoryEval_history = to_dict(ai_sensoryEval)
        ai_sensoryEval_history["createdAt"] = convert2string(
            ai_sensoryEval_history["createdAt"], 1
        )
        return ai_sensoryEval_history
    else:
        return None


def _updateConfirmData(db_session, id):
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat and meat.statusType != 2:
        meat.statusType = 2
        db_session.merge(meat)
        db_session.commit()
        return jsonify({"msg": "Success to update StatusType"}), 200
    else:
        return jsonify({"msg": "No Data In Meat DB or Already Confirmed"}), 404


def _updateRejectData(db_session, id):
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat and meat.statusType != 1:
        meat.statusType = 1
        db_session.merge(meat)
        db_session.commit()
        return jsonify({"msg": "Success to update StatusType"}), 200
    else:
        return jsonify({"msg": "No Data In Meat DB or Already Rejected"}), 404


def _addSpecificPredictData(db_session, data):
    id = data.get("id")
    seqno = data.get("seqno")
    # Find SensoryEval data
    sensory_eval = db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).first()

    # If no SensoryEval found, abort
    if not sensory_eval:
        return jsonify({"msg": "No Sensory Eval Data In DB"}), 404

    # Call 2nd team's API
    response = requests.post(
        f"{os.getenv('ML_server_base_url')}/predict",
        data=json.dumps({"image_path": sensory_eval.imagePath}),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )

    # If the response was unsuccessful, abort
    if response.status_code != 200:
        return jsonify({"msg": "Failed To Get Response From Prediction Server"}), 404

    # Decode the response data
    response_data = response.json()
    # Merge the response data with the existing data
    data.update(response_data)

    # Change the key name from 'gradeNum' to 'xai_gradeNum'
    if "gradeNum" in data:
        data["xai_gradeNum"] = data.pop("gradeNum")
    data["createdAt"] = ""
    try:
        # Create a new SensoryEval
        new_sensory_eval = create_AI_SensoryEval(db_session, data, seqno, id)

        # Add new_sensory_eval to the session
        db_session.merge(new_sensory_eval)

        # Commit the session to save the changes
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    # Return the new data
    return jsonify(data), 200
    # 의문점1 : 이거 시간 오바 안 뜨려나?
    # 의문점2 : 로딩창 안 뜨나


def create_AI_SensoryEval(db_session, meat_data: dict, seqno: int, id: str):
    """
    db: SQLAlchemy db
    freshmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    freshmeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid AI_Sensory_Evaluate data")
    # 2. Get the ID of the record in the GradeNum table
    xai_grade_num = (
        db_session.query(GradeInfo)
        .filter_by(value=meat_data.get("xai_gradeNum"))
        .first()
    )
    # 1. freshmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)

    # 2. freshmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "id":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "xai_gradeNum":
            try:
                item_encoder(meat_data, field, xai_grade_num.id)
            except Exception as e:
                raise Exception("Invalid xai_grade_num id")
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_SensoryEval = AI_SensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong AI sensory eval DB field items" + str(e))
    return new_SensoryEval


def _deleteSpecificMeatData(db_session, s3_conn, id):
    # 1. 육류 DB 체크
    meat = db_session.query(Meat).get(id)
    if meat is None:
        return {"msg": f"Meat Data {id} Does Not Exist", "code": 400}
    try:
        sensory_eval_image_list = s3_conn.get_files_with_id("sensory_evals", id)
        heatedmeat_sensory_eval = s3_conn.get_files_with_id("heatedmeat_sensory_evals", id)
        
        # 육류 데이터 삭제
        db_session.delete(meat)
        db_session.commit()
        
        # 원육 QR 이미지 삭제
        s3_conn.delete_image("qr_codes", f"{id}.png")
            
        # 처리육 관능 이미지 삭제
        for sensory_image in sensory_eval_image_list:
            s3_conn.delete_image("sensory_evals", sensory_image)

        # 가열육 관능 이미지 삭제
        for heatedmeat_image in heatedmeat_sensory_eval:
            s3_conn.delete_image("heatedmeat_sensory_evals", heatedmeat_image)
            
        return {"msg": f"Success to Delete Meat {id}", "code": 200}
    except Exception as e:
        db_session.rollback()
        return {"msg": f"Fail to Delete Meat: {str(e)}", "code": 400}


def deleteMeatByIDList(db_session, s3_conn, id_list: list):
    success_list = []
    fail_list = []

    for meat_id in id_list:
        result = _deleteSpecificMeatData(db_session, s3_conn, meat_id)
        if result["code"] == 200:
            success_list.append(meat_id)
        else:
            fail_list.append(meat_id)

    return success_list, fail_list


def _deleteSpecificDeepAgingData(db_session, s3_conn, id, seqno):
    # 1. 육류 DB 체크
    meat = db_session.query(Meat).get(id)
    deep_aging_info = get_DeepAging(db_session, id, seqno)

    if not (meat and deep_aging_info):
        return ({"msg": f"No Meat or Deep Aging data found with the given ID and Seqno: {id}, {seqno}", "code": 400})
    try:
        s3_conn.delete_image("heatedmeat_sensory_evals", f"{id}-{seqno}.png")
        s3_conn.delete_image("sensory_evals", f"{id}-{seqno}.png")

        db_session.delete(deep_aging_info)

        db_session.commit()
        return ({"msg": f"{id}-{seqno} Deep Aging Data Has Been Deleted", "code": 200})
    except Exception as e:
        db_session.rollback()
        return e


def get_num_of_processed_raw(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    
    try:
        processed_meats_subquery = (
            db_session.query(DeepAgingInfo.id)
            .filter(DeepAgingInfo.seqno > 0)
            .group_by(DeepAgingInfo.id)
            .subquery()
        )
        processed_meats_select = processed_meats_subquery.select()

        # 1. Category.specieId가 0이면서 DeepAgingInfo.seqno 값이 0인 데이터, 1 이상인 데이터
        fresh_cattle_count = (
            db_session.query(Meat)
            .join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
            .filter(
                CategoryInfo.speciesId == 0,
                ~Meat.id.in_(processed_meats_select),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2
            )
            .count()
        )

        processed_cattle_count = (
            db_session.query(Meat)
            .join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
            .filter(
                CategoryInfo.speciesId == 0,
                Meat.id.in_(processed_meats_select),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2
            )
            .count()
        )

        # 2. Category.specieId가 1이면서 DeepAgingInfo.seqno 값이 0인 데이터, 1 이상인 데이터
        fresh_pig_count = (
            db_session.query(Meat)
            .join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
            .filter(
                CategoryInfo.speciesId == 1,
                ~Meat.id.in_(processed_meats_select),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .count()
        )
        
        processed_pig_count = (
            db_session.query(Meat)
            .join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
            .filter(
                CategoryInfo.speciesId == 1,
                Meat.id.in_(processed_meats_select),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .count()
        )

        # 3. 전체 데이터에서 DeepAgingInfo.seqno 값이 0인 데이터, 1 이상인인 데이터
        fresh_meat_count = (
            db_session.query(Meat)
            .filter(
                ~Meat.id.in_(processed_meats_select),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .count()
        )

        processed_meat_count = (
            db_session.query(Meat)
            .filter(
                Meat.id.in_(processed_meats_select),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .count()
        )

        # Returning the counts in JSON format
        return ({
            "cattle_counts": {
                "raw": fresh_cattle_count,
                "processed": processed_cattle_count,
            },
            "pig_counts": {
                "raw": fresh_pig_count,
                "processed": processed_pig_count,
            },
            "total_counts": {
                "raw": fresh_meat_count,
                "processed": processed_meat_count,
            }
        })
 
    except Exception as e:
        raise Exception("Something Wrong with DB" + str(e))


def get_num_of_cattle_pig(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 1)  # Start Time
    end = convert2datetime(end, 1)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    cow_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 0,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    pig_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 1,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    return jsonify({"cattle_count": cow_count, "pig_count": pig_count}), 200


def get_num_of_primal_part(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time

    try:
        # 1. Category.specieId가 0일때 해당 Category.primalValue 별로 육류의 개수를 추출
        cow_count = (
            db_session.query((func.count(Meat.id)).label('counts'), CategoryInfo.primalValue)
            .join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
            .filter(
                CategoryInfo.speciesId == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .group_by(CategoryInfo.primalValue)
            .all()
        )
        beef = {f"{count.primalValue}": count.counts for count in cow_count}
        # logger.info(f'소의 부위별 고기 개수: {count_by_primal_value_beef}')

        # 2. Category.specieId가 1일때 해당 Category.primalValue 별로 육류의 개수를 추출
        pig_count = (
            db_session.query((func.count(Meat.id)).label('counts'), CategoryInfo.primalValue)
            .join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
            .filter(
                CategoryInfo.speciesId == 1,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .group_by(CategoryInfo.primalValue)
            .all()
        )
        pork = {f"{count.primalValue}": count.counts for count in pig_count}
        # logger.info(f'돼지의 부위별 고기 개수: {count_by_primal_value_port')

        # Returning the counts in JSON format
        return ({
            "beef_counts_by_primal_value": beef,
            "pork_counts_by_primal_value": pork,
        })
    
    except Exception as e:
        raise Exception("Something Wrong with DB" + str(e))


def get_num_by_farmAddr(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    
    try:
        result = {}
        for speciesId in [0, 1, 2]:  # 0 for cattle, 1 for pig
            query = (
                db_session.query(Meat)
                .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
                .filter(
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
            )
            if speciesId != 2:
                query.filter(CategoryInfo.speciesId == speciesId)

            region_counts = {}
            for region in regions:
                count = query.filter(Meat.farmAddr.like(f"{region}%")).count()
                region_counts[region] = count
                
            if speciesId == 0:
                result["cattle_counts_by_region"] = region_counts
            elif speciesId == 1:
                result["pig_counts_by_region"] = region_counts
            else:
                result["total_counts_by_region"] = region_counts

        return result
    
    except Exception as e:
        raise Exception("Something Wrong with DB" + str(e))


def get_probexpt_of_rawmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404
    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["sourness", "bitterness", "umami", "richness"]:
        avg = (
            db_session.query(func.avg(getattr(ProbexptData, field)))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        max_value = (
            db_session.query(func.max(getattr(ProbexptData, field)))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        min_value = (
            db_session.query(func.min(getattr(ProbexptData, field)))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )

        # 실제로 존재하는 값들 찾기
        unique_values_query = (
            db_session.query(getattr(ProbexptData, field))
            .join(Meat, Meat.id == ProbexptData.id)
            .filter(
                ProbexptData.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .distinct()
        )
        unique_values = [value[0] for value in unique_values_query.all()]

        stats[field] = {
            "avg": avg,
            "max": max_value,
            "min": min_value,
            "unique_values": unique_values,
        }

    return jsonify(stats)


def get_probexpt_of_processedmeat(db_session, seqno, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    seqno = safe_int(seqno)
    if seqno:
        for field in ["sourness", "bitterness", "umami", "richness"]:
            avg = (
                db_session.query(func.avg(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(ProbexptData, field))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [value[0] for value in unique_values_query.all()]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": unique_values,
            }
    else:
        for field in ["sourness", "bitterness", "umami", "richness"]:
            avg = (
                db_session.query(func.avg(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(ProbexptData, field)))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(ProbexptData, field))
                .join(Meat, Meat.id == ProbexptData.id)
                .filter(
                    ProbexptData.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [value[0] for value in unique_values_query.all()]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": unique_values,
            }

    return jsonify(stats)


def get_sensory_of_meat(db_session, start, end, species, grade, is_raw):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
        query = (
            db_session.query(
                (func.avg(getattr(SensoryEval, field)).label('average')),
                (func.max(getattr(SensoryEval, field)).label('maximum')),
                (func.min(getattr(SensoryEval, field)).label('minimum')),
            )
            .join(DeepAgingInfo, DeepAgingInfo.id == SensoryEval.id and DeepAgingInfo.seqno == SensoryEval.seqno)
            .join(Meat, Meat.id == DeepAgingInfo.id)
            .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
            .filter(
                CategoryInfo.speciesId == species,
                Meat.gradeNum == grade,
                Meat.statusType == 2,
            )
        )
        query = (
            query.filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
            ) 
            if is_raw 
            else query.filter(
                SensoryEval.seqno != 0,
                SensoryEval.createdAt.between(start, end),
            )
        )
        query = query.one()
        average = query.average
        maximum = query.maximum
        minimum = query.minimum

        # 실제로 존재하는 값들 찾기
        uniques_query = (
            db_session.query(getattr(SensoryEval, field))
            .join(DeepAgingInfo, DeepAgingInfo.id == SensoryEval.id and DeepAgingInfo.seqno == SensoryEval.seqno)
            .join(Meat, Meat.id == DeepAgingInfo.id)
            .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
            .filter(
                CategoryInfo.speciesId == species,
                Meat.gradeNum == grade,
                Meat.statusType == 2,
            )
        )
        uniques_query = (
            uniques_query.filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
            )
            if is_raw
            else uniques_query.filter(
                SensoryEval.seqno != 0,
                SensoryEval.createdAt.between(start, end),
            )
        )
        uniques = [value[0] for value in uniques_query.distinct().all()]

        stats[field] = {
            "avg": average,
            "max": maximum,
            "min": minimum,
            "unique_values": sorted(uniques),
        }

    return stats


# def get_sensory_of_processedmeat(db_session, seqno, start, end):
#     # 기간 설정
#     start = convert2datetime(start, 0)  # Start Time
#     end = convert2datetime(end, 0)  # End Time
#     if start is None or end is None:
#         return jsonify({"msg": "Wrong start or end data"}), 404

#     stats = {}
#     seqno = safe_int(seqno)
#     if seqno:
#         # 각 필드의 평균값, 최대값, 최소값 계산
#         for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
#             avg = (
#                 db_session.query(func.avg(getattr(SensoryEval, field)))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno == seqno,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .scalar()
#             )
#             max_value = (
#                 db_session.query(func.max(getattr(SensoryEval, field)))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno == seqno,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .scalar()
#             )
#             min_value = (
#                 db_session.query(func.min(getattr(SensoryEval, field)))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno == seqno,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .scalar()
#             )

#             # 실제로 존재하는 값들 찾기
#             unique_values_query = (
#                 db_session.query(getattr(SensoryEval, field))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno == seqno,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .distinct()
#             )
#             unique_values = [
#                 value[0] for value in unique_values_query.all() if value[0] is not None
#             ]

#             stats[field] = {
#                 "avg": avg,
#                 "max": max_value,
#                 "min": min_value,
#                 "unique_values": (
#                     sorted(unique_values) if unique_values else unique_values
#                 ),
#             }
#     else:
#         # 각 필드의 평균값, 최대값, 최소값 계산
#         for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
#             avg = (
#                 db_session.query(func.avg(getattr(SensoryEval, field)))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno != 0,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .scalar()
#             )
#             max_value = (
#                 db_session.query(func.max(getattr(SensoryEval, field)))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno != 0,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .scalar()
#             )
#             min_value = (
#                 db_session.query(func.min(getattr(SensoryEval, field)))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno != 0,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .scalar()
#             )

#             # 실제로 존재하는 값들 찾기
#             unique_values_query = (
#                 db_session.query(getattr(SensoryEval, field))
#                 .join(Meat, Meat.id == SensoryEval.id)
#                 .filter(
#                     SensoryEval.seqno != 0,
#                     Meat.createdAt.between(start, end),
#                     Meat.statusType == 2,
#                 )
#                 .distinct()
#             )
#             unique_values = [
#                 value[0] for value in unique_values_query.all() if value[0] is not None
#             ]

#             stats[field] = {
#                 "avg": avg,
#                 "max": max_value,
#                 "min": min_value,
#                 "unique_values": sorted(unique_values),
#             }

#     return jsonify(stats)


def get_sensory_of_raw_heatedmeat(db_session, start, end, species, grade, is_raw):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["flavor", "juiciness", "tenderness", "umami", "palatability"]:
        query = (
            db_session.query(
                (func.avg(getattr(HeatedmeatSensoryEval, field)).label('average')),
                (func.max(getattr(HeatedmeatSensoryEval, field)).label('maximum')),
                (func.min(getattr(HeatedmeatSensoryEval, field)).label('minimum')),
            )
            .join(DeepAgingInfo, DeepAgingInfo.id == HeatedmeatSensoryEval.id and DeepAgingInfo.seqno == HeatedmeatSensoryEval.seqno)
            .join(Meat, Meat.id == DeepAgingInfo.id)
            .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
            .filter(
                CategoryInfo.speciesId == species,
                Meat.gradeNum == grade,
                Meat.statusType == 2,
            )
        )
        query = (
            query.filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
            ) 
            if is_raw 
            else query.filter(
                HeatedmeatSensoryEval.seqno != 0,
                HeatedmeatSensoryEval.createdAt.between(start, end),
            )
        )
        query = query.one()
        average = query.average
        maximum = query.maximum
        minimum = query.minimum

        # 실제로 존재하는 값들 찾기
        uniques_query = (
            db_session.query(getattr(HeatedmeatSensoryEval, field))
            .join(DeepAgingInfo, DeepAgingInfo.id == HeatedmeatSensoryEval.id and DeepAgingInfo.seqno == HeatedmeatSensoryEval.seqno)
            .join(Meat, Meat.id == DeepAgingInfo.id)
            .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
            .filter(
                CategoryInfo.speciesId == species,
                Meat.gradeNum == grade,
                Meat.statusType == 2,
            )
        )
        uniques_query = (
            uniques_query.filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
            )
            if is_raw
            else uniques_query.filter(
                HeatedmeatSensoryEval.seqno != 0,
                HeatedmeatSensoryEval.createdAt.between(start, end),
            )
        )
        uniques = [value[0] for value in uniques_query.distinct().all()]

        stats[field] = {
            "avg": average,
            "max": maximum,
            "min": minimum,
            "unique_values": sorted(uniques),
        }

    return stats


def get_sensory_of_processed_heatedmeat(db_session, seqno, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    seqno = safe_int(seqno)
    if seqno:
        for field in ["flavor", "juiciness", "tenderness", "umami", "palability"]:
            avg = (
                db_session.query(func.avg(getattr(HeatedmeatSensoryEval, field)))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(HeatedmeatSensoryEval, field)))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(
                    func.min(
                        getattr(HeatedmeatSensoryEval, field),
                        Meat.createdAt.between(start, end),
                        Meat.statusType == 2,
                    )
                )
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(HeatedmeatSensoryEval.seqno == seqno)
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(HeatedmeatSensoryEval, field))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [
                value[0] for value in unique_values_query.all() if value[0] is not None
            ]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": sorted(unique_values),
            }
    else:
        for field in ["flavor", "juiciness", "tenderness", "umami", "palability"]:
            avg = (
                db_session.query(func.avg(getattr(HeatedmeatSensoryEval, field)))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(HeatedmeatSensoryEval, field)))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(HeatedmeatSensoryEval, field)))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(HeatedmeatSensoryEval, field))
                .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
                .filter(
                    HeatedmeatSensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .distinct()
            )
            unique_values = [
                value[0] for value in unique_values_query.all() if value[0] is not None
            ]

            stats[field] = {
                "avg": avg,
                "max": max_value,
                "min": min_value,
                "unique_values": sorted(unique_values),
            }

    return jsonify(stats)


def get_probexpt_of_processed_heatedmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # Get all SensoryEval records
    sensory_evals = (
        SensoryEval.query.join(Meat, Meat.id == SensoryEval.id)
        .filter(
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .order_by(SensoryEval.id, SensoryEval.seqno)
        .all()
    )

    result = {}

    # Keep track of the accumulated minutes for each id
    accumulated_minutes = {}

    for sensory_eval in sensory_evals:
        deep_aging = (
            db_session.query(DeepAgingInfo)
            .filter_by(deepAgingId=sensory_eval.deepAgingId)
            .first()
        )

        # If no matching DeepAging record was found, skip this SensoryEval

        # Get the corresponding ProbexptData record
        probexpt_data = ProbexptData.query.filter_by(
            id=sensory_eval.id, seqno=sensory_eval.seqno
        ).first()

        # If no matching ProbexptData record was found, skip this SensoryEval
        if not probexpt_data:
            continue

        # Create a dictionary of ProbexptData fields
        probexpt_data_dict = {
            "sourness": probexpt_data.sourness,
            "bitterness": probexpt_data.bitterness,
            "umami": probexpt_data.umami,
            "richness": probexpt_data.richness,
        }

        # If the seqno is 0, set the minute to 0, otherwise, add the current DeepAging minute to the accumulated minutes
        if sensory_eval.seqno == 0:
            accumulated_minutes[sensory_eval.id] = 0
        else:
            # If the id is not yet in the accumulated_minutes dictionary, initialize it to the current minute
            if sensory_eval.id not in accumulated_minutes:
                accumulated_minutes[sensory_eval.id] = deep_aging.minute
            else:
                accumulated_minutes[sensory_eval.id] += deep_aging.minute

        # Add the ProbexptData fields to the result under the accumulated minutes
        if accumulated_minutes[sensory_eval.id] not in result:
            result[accumulated_minutes[sensory_eval.id]] = {}

        result[accumulated_minutes[sensory_eval.id]][
            f"({sensory_eval.id},{sensory_eval.seqno})"
        ] = probexpt_data_dict

    return result

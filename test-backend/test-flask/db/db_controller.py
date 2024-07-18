import pprint
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import uuid
import hashlib
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
from sqlalchemy import func, create_engine
import json

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


def create_SensoryEval(meat_data: dict, seqno: int, id: str, deepAgingId: int):
    """
    db: SQLAlchemy db
    freshmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    freshmeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid Sensory_Evaluate data")
    # 1. freshmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)
    item_encoder(meat_data, "deepAgingId", deepAgingId)
    # 2. freshmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "freshmeatId":  # 여기 있어도 걍 입력된걸 써라~
            pass
        elif field == "deepAgingId":
            pass
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_SensoryEval = SensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong sensory eval DB field items" + str(e))
    return new_SensoryEval


def create_HeatemeatSensoryEval(meat_data: dict, seqno: int, id: str):
    """
    db: SQLAlchemy db
    heatedmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    heatedMeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    # 1. heatedmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)
    # 2. heatedmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":
            pass
        elif field == "id":
            pass
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_heatedmeat = HeatedmeatSensoryEval(**meat_data)
    except Exception as e:
        raise Exception("Wrong heatedmeat sensory eval DB field items" + str(e))
    return new_heatedmeat


def create_ProbexptData(meat_data: dict, seqno: int, id: str):
    """
    db: SQLAlchemy db
    heatedmeat_data: 모든 필드의 데이터가 문자열로 들어왔다고 가정!!
    seqno: 신선육 관능검사 seqno
    heatedMeatId: 가열육 관능검사 seqno
    probexpt_seqno: 실험(전자혀) 관능 검사 seqno
    type: 0(신규 생성) or 1(기존 수정)
    """
    if meat_data is None:
        raise Exception("Invalid Heatedmeat Sensory Evaluate data")
    # 1. heatedmeat_data에 없는 필드 추가
    item_encoder(meat_data, "seqno", seqno)
    item_encoder(meat_data, "id", id)
    # 2. heatedmeat_data에 있는 필드 수정
    for field in meat_data.keys():
        if field == "seqno":
            pass
        elif field == "id":
            pass
        else:
            item_encoder(meat_data, field)
    # Create a new Meat object
    try:
        new_probexptdata = ProbexptData(**meat_data)
    except Exception as e:
        raise Exception("Wrong heatedmeat sensory eval DB field items" + str(e))
    return new_probexptdata


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


def create_raw_meat_deep_aging_info(db_session, meat_id):
    new_meat = db_session.query(Meat).get(meat_id)
    new_deep_aging = {
        "id": meat_id,
        "seqno": 0,
        "date": new_meat.createdAt,
        "minute": 0
    }
    try:
        deep_aging_data = DeepAgingInfo(**new_deep_aging)
        db_session.add(deep_aging_data)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e


def create_specific_deep_aging_meat_data(db_session, s3_conn, firestore_conn, data):
    # 2. 기본 데이터 받아두기
    id = data.get("id")
    seqno = data.get("seqno")
    deepAging_data = data.get("deepAging")
    data.pop("deepAging", None)
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No Id in Request Data")
    sensory_eval = (
        db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).first()
    )  # DB에 있는 육류 정보
    try:
        if deepAging_data is not None:
            if meat:  # 승인 정보 확인
                if meat.statusType != 2:
                    raise Exception("Not Confirmed Meat Data")
            if sensory_eval:  # 기존 Deep Aging을 수정하는 경우
                deepAgingId = sensory_eval.deepAgingId
                existing_DeepAging = db_session.query(DeepAgingInfo).get(deepAgingId)
                if existing_DeepAging:
                    for key, value in deepAging_data.items():
                        setattr(existing_DeepAging, key, value)
                    # for key, value in data.items():
                    #     setattr(sensory_eval, key, value)
                    new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                    db_session.merge(new_SensoryEval)
                else:
                    raise Exception("No Deep Aging Data found for update")
            else:  # 새로운 Deep aging을 추가하는 경우
                new_DeepAging = create_DeepAging(deepAging_data)
                deepAgingId = new_DeepAging.deepAgingId
                db_session.add(new_DeepAging)
                db_session.commit()
                new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                db_session.merge(new_SensoryEval)

            db_session.commit()
            transfer_folder_image(
                s3_conn,
                firestore_conn,
                db_session,
                f"{id}-{seqno}",
                new_SensoryEval,
                "sensory_evals",
            )
            
        else:
            raise Exception("No deepaging data in request")
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id)


def create_specific_sensoryEval(db_session, s3_conn, firestore_conn, data):
    # 2. 기본 데이터 받아두기
    id = safe_str(data.get("id"))
    seqno = safe_int(data.get("seqno"))
    deepAging_data = data.get("deepAging")
    data.pop("deepAging", None)
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No ID data sent for update")

    sensory_eval = (
        db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).first()
    )  # DB에 있는 육류 정보
    try:
        if seqno != 0:  # 가공육 관능검사
            if sensory_eval:  # 기존 Deep Aging을 수정하는 경우
                deepAgingId = sensory_eval.deepAgingId
                new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                db_session.merge(new_SensoryEval)
            else:  # 새로운 Deep aging을 추가하는 경우
                new_DeepAging = create_DeepAging(deepAging_data)
                deepAgingId = new_DeepAging.deepAgingId
                db_session.add(new_DeepAging)
                db_session.commit()
                new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
                db_session.merge(new_SensoryEval)
        else:  # 신선육 관능검사
            if meat:  # 수정하는 경우
                if meat.statusType == 2:
                    raise Exception("Already confirmed meat data")
                meat.statusType = 0
                db_session.merge(meat)
            deepAgingId = None
            new_SensoryEval = create_SensoryEval(data, seqno, id, deepAgingId)
            db_session.merge(new_SensoryEval)
            
        db_session.commit()
        transfer_folder_image(
            s3_conn,
            firestore_conn,
            db_session,
            f"{id}-{seqno}",
            new_SensoryEval,
            "sensory_evals",
        )
    except Exception as e:
        db_session.rollback()
        logger.exception(str(e))
        raise e
    return jsonify(id)


def create_specific_heatedmeat_seonsory_data(db_session, data):
    # 2. 기본 데이터 받아두기
    meat_id = safe_str(data.get("meatId"))
    seqno = safe_int(data.get("seqno"))
    meat = db_session.query(Meat).get(meat_id)  # DB에 있는 육류 정보
    if meat:  # 승인 정보 확인
        if meat.statusType != 2:
            raise Exception("Not confirmed meat data")
    if meat_id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No ID data sent for update")
    try:
        new_HeatedmeatSensoryEval = create_HeatemeatSensoryEval(data, seqno, meat_id)
        db_session.merge(new_HeatedmeatSensoryEval)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(meat_id)


def create_specific_probexpt_data(db_session, data):
    # 2. 기본 데이터 받아두기
    id = safe_str(data.get("id"))
    seqno = safe_int(data.get("seqno"))
    meat = db_session.query(Meat).get(id)  # DB에 있는 육류 정보
    if meat:  # 승인 정보 확인
        if meat.statusType != 2:
            raise Exception("Not confirmed meat data")
    if id == None:  # 1. 애초에 id가 없는 request
        raise Exception("No ID data sent for update")
    try:
        new_ProbexptData = create_ProbexptData(data, seqno, id)
        db_session.merge(new_ProbexptData)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise e
    return jsonify(id)


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
            f"{sequence}":{
                "sensory_eval": get_SensoryEval(db_session, id, sequence),
                "heatedmeat_sensory_eval": get_HeatedmeatSensoryEval(db_session, id, sequence),
                "probexpt_data": get_ProbexptData(db_session, id, sequence, False),
                "heatedmeat_probexpt_data": get_ProbexptData(db_session, id, sequence, True),
            }
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
    if count and offset:
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
    if offset and count:
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
            user.createdAt = convert2string(user.createdAt, 0)
        return users
    except Exception as e:
        raise Exception(str(e))

def get_user(db_session, user_id):
    try:
        user_data = db_session.query(User).filter(User.userId == user_id).first()
        if user_data is not None:
            user_data.createdAt = convert2string(user_data.createdAt, 0)
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


def _getMeatDataByUserId(db_session, userId):
    meats = db_session.query(Meat).filter_by(userId=userId).all()
    if meats:
        result = []
        for meat in meats:
            temp = get_meat(db_session, meat.id)
            del temp["processedmeat"]
            del temp["rawmeat"]
            result.append(temp)
        return jsonify(result), 200
    else:
        return jsonify({"message": "No meats found for the given userId."}), 404


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
            userTemp = get_user(db_session, temp.get("userId"))
            if userTemp:
                temp["name"] = userTemp.get("name")
            else:
                temp["name"] = userTemp
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
    meat = db_session.query(Meat).filter_by(id=id).one()
    if meat is None:
        return jsonify({"msg": f"No meat data found with the given ID: {id}"}), 404
    try:
        sensory_evals = db_session.query(SensoryEval).filter_by(id=id).all()
        heatedmeat_evals = (
            db_session.query(HeatedmeatSensoryEval).filter_by(id=id).all()
        )
        probexpt_datas = db_session.query(ProbexptData).filter_by(id=id).all()
        # 가열육 데이터 삭제
        for heatedmeat_eval in heatedmeat_evals:
            seqno = heatedmeat_eval.seqno
            db_session.delete(heatedmeat_eval)
            s3_conn.delete_image("heatedmeat_sensory_evals", f"{id}-{seqno}")

        # 실험 데이터 삭제
        for probexpt_data in probexpt_datas:
            db_session.delete(probexpt_data)

        # 관능 데이터 삭제 및 관능 이미지 삭제
        for sensory_eval in sensory_evals:
            seqno = sensory_eval.seqno
            db_session.delete(sensory_eval)
            s3_conn.delete_image("sensory_evals", f"{id}-{seqno}")

        # 육류 데이터 삭제
        db_session.delete(meat)
        db_session.commit()

        # 큐알 삭제
        s3_conn.delete_image("qr_codes", f"{id}")
        db_session.commit()
        return jsonify({"delete Id": id}), 200
    except Exception as e:
        db_session.rollback()
        raise e


def _deleteSpecificDeepAgingData(db_session, s3_conn, id, seqno):
    # 1. 육류 DB 체크
    meat = db_session.query(Meat).get(id)

    if meat is None:
        return jsonify({"msg": f"No meat data found with the given ID: {id}"}), 404
    try:
        sensory_evals = (
            db_session.query(SensoryEval).filter_by(id=id, seqno=seqno).all()
        )
        heatedmeat_evals = (
            db_session.query(HeatedmeatSensoryEval).filter_by(id=id, seqno=seqno).all()
        )
        probexpt_datas = (
            db_session.query(ProbexptData).filter_by(id=id, seqno=seqno).all()
        )

        for heatedmeat_eval in heatedmeat_evals:
            db_session.delete(heatedmeat_eval)
            s3_conn.delete_image("heatedmeat_sensory_evals", f"{id}-{seqno}")

        for probexpt_data in probexpt_datas:
            db_session.delete(probexpt_data)

        for sensory_eval in sensory_evals:
            db_session.delete(sensory_eval)
            s3_conn.delete_image("sensory_evals", f"{id}-{seqno}")

        db_session.commit()
        return jsonify({"delete Id": id, "delete Seqno": seqno}), 200
    except Exception as e:
        db_session.rollback()
        return e


def get_num_of_processed_raw(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # Subquery to find meats which have processed data
    processed_meats_subquery = (
        db_session.query(Meat.id)
        .join(SensoryEval)
        .filter(SensoryEval.seqno > 0)
        .subquery()
    )
    processed_meats_select = processed_meats_subquery.select()

    # 1. Category.specieId가 0이면서 SensoryEval.seqno 값이 0인 데이터, 1인 데이터
    fresh_cattle_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 0,
            ~Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    processed_cattle_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 0,
            Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )

    # 2. Category.specieId가 1이면서 SensoryEval.seqno 값이 0인 데이터, 1인 데이터
    fresh_pig_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 1,
            ~Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )
    processed_pig_count = (
        Meat.query.join(CategoryInfo)
        .filter(
            CategoryInfo.speciesId == 1,
            Meat.id.in_(processed_meats_select),
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .count()
    )

    # 3. 전체 데이터에서 SensoryEval.seqno 값이 0인 데이터, 1인 데이터
    fresh_meat_count = Meat.query.filter(
        ~Meat.id.in_(processed_meats_select),
        Meat.createdAt.between(start, end),
        Meat.statusType == 2,
    ).count()

    processed_meat_count = Meat.query.filter(
        Meat.id.in_(processed_meats_select),
        Meat.createdAt.between(start, end),
        Meat.statusType == 2,
    ).count()

    # Returning the counts in JSON format
    return (
        jsonify(
            {
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
                },
            }
        ),
        200,
    )


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
    print(start, end)
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404
    # 1. Category.specieId가 0일때 해당 Category.primalValue 별로 육류의 개수를 추출
    count_by_primal_value_beef = (
        db_session.query(CategoryInfo.primalValue, func.count(Meat.id))
        .join(Meat, Meat.categoryId == CategoryInfo.id)
        .filter(
            CategoryInfo.speciesId == 0,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .group_by(CategoryInfo.primalValue)
        .all()
    )
    # logger.info(f'소의 부위별 고기 개수: {count_by_primal_value_beef}')

    # 2. Category.specieId가 1일때 해당 Category.primalValue 별로 육류의 개수를 추출
    count_by_primal_value_pork = (
        db_session.query(CategoryInfo.primalValue, func.count(Meat.id))
        .join(Meat, Meat.categoryId == CategoryInfo.id)
        .filter(
            CategoryInfo.speciesId == 1,
            Meat.createdAt.between(start, end),
            Meat.statusType == 2,
        )
        .group_by(CategoryInfo.primalValue)
        .all()
    )

    # Returning the counts in JSON format
    return (
        jsonify(
            {
                "beef_counts_by_primal_value": dict(count_by_primal_value_beef),
                "pork_counts_by_primal_value": dict(count_by_primal_value_pork),
            }
        ),
        200,
    )


def get_num_by_farmAddr(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404
    regions = [
        "강원",
        "경기",
        "경남",
        "경북",
        "광주",
        "대구",
        "대전",
        "부산",
        "서울",
        "세종",
        "울산",
        "인천",
        "전남",
        "전북",
        "제주",
        "충남",
        "충북",
    ]
    result = {}

    for speciesId in [0, 1]:  # 0 for cattle, 1 for pig
        region_counts = {}
        for region in regions:
            region_like = "%".join(list(region))
            count = (
                db_session.query(Meat)
                .join(CategoryInfo, CategoryInfo.id == Meat.categoryId)
                .filter(
                    CategoryInfo.speciesId == speciesId,
                    Meat.farmAddr.like(f"%{region_like}%"),
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .count()
            )
            region_counts[region] = count
        if speciesId == 0:
            result["cattle_counts_by_region"] = region_counts
        else:
            result["pig_counts_by_region"] = region_counts

    # For total data
    total_region_counts = {}
    for region in regions:
        count = (
            db_session.query(Meat)
            .filter(
                Meat.farmAddr.like(f"%{region}%"),
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .count()
        )
        total_region_counts[region] = count
    result["total_counts_by_region"] = total_region_counts

    return jsonify(result), 200


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


def get_sensory_of_rawmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
        avg = (
            db_session.query(func.avg(getattr(SensoryEval, field)))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        max_value = (
            db_session.query(func.max(getattr(SensoryEval, field)))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        min_value = (
            db_session.query(func.min(getattr(SensoryEval, field)))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )

        # 실제로 존재하는 값들 찾기
        unique_values_query = (
            db_session.query(getattr(SensoryEval, field))
            .join(Meat, Meat.id == SensoryEval.id)
            .filter(
                SensoryEval.seqno == 0,
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
            "unique_values": sorted(unique_values),
        }

    return jsonify(stats)


def get_sensory_of_processedmeat(db_session, seqno, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    stats = {}
    seqno = safe_int(seqno)
    if seqno:
        # 각 필드의 평균값, 최대값, 최소값 계산
        for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
            avg = (
                db_session.query(func.avg(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(SensoryEval, field))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno == seqno,
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
                "unique_values": (
                    sorted(unique_values) if unique_values else unique_values
                ),
            }
    else:
        # 각 필드의 평균값, 최대값, 최소값 계산
        for field in ["marbling", "color", "texture", "surfaceMoisture", "overall"]:
            avg = (
                db_session.query(func.avg(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            max_value = (
                db_session.query(func.max(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )
            min_value = (
                db_session.query(func.min(getattr(SensoryEval, field)))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
                    Meat.createdAt.between(start, end),
                    Meat.statusType == 2,
                )
                .scalar()
            )

            # 실제로 존재하는 값들 찾기
            unique_values_query = (
                db_session.query(getattr(SensoryEval, field))
                .join(Meat, Meat.id == SensoryEval.id)
                .filter(
                    SensoryEval.seqno != 0,
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


def get_sensory_of_raw_heatedmeat(db_session, start, end):
    # 기간 설정
    start = convert2datetime(start, 0)  # Start Time
    end = convert2datetime(end, 0)  # End Time
    if start is None or end is None:
        return jsonify({"msg": "Wrong start or end data"}), 404

    # 각 필드의 평균값, 최대값, 최소값 계산
    stats = {}
    for field in ["flavor", "juiciness", "tenderness", "umami", "palability"]:
        avg = (
            db_session.query(func.avg(getattr(HeatedmeatSensoryEval, field)))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        max_value = (
            db_session.query(func.max(getattr(HeatedmeatSensoryEval, field)))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
                Meat.createdAt.between(start, end),
                Meat.statusType == 2,
            )
            .scalar()
        )
        min_value = (
            db_session.query(func.min(getattr(HeatedmeatSensoryEval, field)))
            .join(Meat, Meat.id == HeatedmeatSensoryEval.id)
            .filter(
                HeatedmeatSensoryEval.seqno == 0,
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
                HeatedmeatSensoryEval.seqno == 0,
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

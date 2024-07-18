from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_controller import (
    create_raw_meat_deep_aging_info,
    create_specific_sensory_eval,
    create_specific_std_meat_data,
    # create_specific_sensoryEval,
    create_specific_probexpt_data,
    create_specific_deep_aging_data,
    create_specific_heatedmeat_seonsory_data,
    _addSpecificPredictData,
    get_meat,
)
from utils import *

add_api = Blueprint("add_api", __name__)


# 특정 육류의 기본 정보 생성 및 수정
@add_api.route("/", methods=["POST", "PATCH"])
def add_specific_meat_data():
    db_session = current_app.db_session
    s3_conn = current_app.s3_conn
    firestore_conn = current_app.firestore_conn
    try:
        data = request.get_json()
        meat_id = data.get("meatId")
        meat = get_meat(db_session, meat_id)
        
        if request.method == "POST": # 기본 원육 정보 생성(POST)
            if meat:
                return jsonify({"msg": "Already Existing Meat"}), 400
                
            new_meat_id = create_specific_std_meat_data(
                db_session, s3_conn, firestore_conn, data, meat_id, is_post=1
            )
            if new_meat_id:
                create_raw_meat_deep_aging_info(db_session, new_meat_id, seqno=0)
                return jsonify({"msg": "Success to store Raw Meat and Initial DeepAging Information"}), 200
                
        else: # 기본 원육 정보 수정(PATCH)
            if not meat:
                return jsonify({"msg": "Not Existing Meat"}), 404

            updated_meat_id = create_specific_std_meat_data(
                db_session, s3_conn, firestore_conn, data, meat_id, is_post=0
            )
            if updated_meat_id:
                return jsonify({"msg": f"Success to update Raw Meat {updated_meat_id} Information"}), 200
            else:
                return jsonify({"msg": f"Already Confirmed Meat Data"}), 400

    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 딥 에이징 이력 생성
@add_api.route("/deep-aging-data", methods=["POST"])
def add_specific_deepAging_data():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        if not (data["meatId"] and data["seqno"] and data["deepAging"]):
            return jsonify({"msg": "Failed to Create Deep Aging Data"}), 400
        deep_aging_id = create_specific_deep_aging_data(db_session, data)
        if deep_aging_id:
            return jsonify({"msg": f"Success to Create Deep Aging Data {deep_aging_id}"}), 200
        elif deep_aging_id is None:
            return jsonify({"msg": f"Meat {data['meatId']} Does NOT Exists"}), 404
        else:
            return jsonify({"msg": f"Seqno {data['seqno']} Deep Aging Info. Already Exists"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 관능 검사 결과 생성 및 수정
@add_api.route("/sensory-eval", methods=["POST", "PATCH"])
def add_specific_sensory_eval():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        s3_conn = current_app.s3_conn
        firestore_conn = current_app.firestore_conn
        
        if request.method == "POST":
            sensory_data = create_specific_sensory_eval(db_session, s3_conn, firestore_conn, data, is_post=1)
        else:
            sensory_data = create_specific_sensory_eval(db_session, s3_conn, firestore_conn, data, is_post=0)
        return {"msg": sensory_data["msg"], "code": sensory_data["code"]}
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# POST일 때는 app - imagePath, createdAt, period 새로 추가
# PATCH일 때는 app, web - 현재 코드 그대로
# 특정 육류의 가열육 관능 검사 결과 생성 및 수정
@add_api.route("/heatedmeat-eval", methods=["POST", "PATCH"])
def add_specific_heatedmeat_sensory_data():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        if request.method == "POST":
            return jsonify({"msg": "Failed to POST Heatedmeat Sensory Data"}), 400
        elif request.method == "PATCH":
            return jsonify({"msg": "Failed to PATCH Heatedmeat Sensory Data"}), 400
        
        return create_specific_heatedmeat_seonsory_data(db_session, data), 200
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 실험실 데이터 생성 및 수정
@add_api.route("/probexpt-data", methods=["POST", "PATCH"])
def add_specific_probexpt_data():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        if request.method == "POST":
            is_post = True
            for key in ("meatId", "seqno", "isHeated", "userId", "probexptData"):
                if key not in data.keys() or data[key] is None:
                    return jsonify({"msg": "Failed to Create Probexpt Data"}), 400

        elif request.method == "PATCH":
            is_post = False
            for key in ("meatId", "seqno", "isHeated", "probexptData"):
                if key not in data.keys() or data[key] is None:
                    return jsonify({"msg": "Failed to Create Probexpt Data"}), 400

        probexpt_data = create_specific_probexpt_data(db_session, data, is_post)
        return jsonify({"msg": probexpt_data["msg"]}), probexpt_data["code"]
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 예측 데이터 생성 및 수정
@add_api.route("/predict-data", methods=["GET", "POST"])
def add_specific_predict_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            if data:
                return _addSpecificPredictData(db_session, data)
            else:
                return jsonify({"msg": "No data in Request."}), 401
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

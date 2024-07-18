from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_controller import (
    create_raw_meat_deep_aging_info,
    create_specific_std_meat_data,
    create_specific_sensoryEval,
    create_specific_probexpt_data,
    create_specific_deep_aging_meat_data,
    create_specific_heatedmeat_seonsory_data,
    _addSpecificPredictData,
    get_meat,
)
from utils import *
import uuid

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
                create_raw_meat_deep_aging_info(db_session, new_meat_id)
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


# 특정 육류의 딥 에이징 이력 생성 및 수정
@add_api.route("/deep-aging-data", methods=["GET", "POST"])
def add_specific_deepAging_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            s3_conn = current_app.s3_conn
            firestore_conn = current_app.firestore_conn
            data = request.get_json()
            # print(data)
            try:
                return (
                    create_specific_deep_aging_meat_data(
                        db_session, s3_conn, firestore_conn, data
                    ),
                    200,
                )
            except Exception as e:
                return jsonify({"msg": "Image Path Not Found", "details": str(e)}), 400
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


# 특정 육류의 관능 검사 결과 생성 및 수정
@add_api.route("/sensory-eval", methods=["GET", "POST"])
def add_specific_sensory_eval():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            s3_conn = current_app.s3_conn
            firestore_conn = current_app.firestore_conn
            data = request.get_json()
            try:
                return (
                    create_specific_sensoryEval(db_session, s3_conn, firestore_conn, data),
                    200,
                )
            except Exception as e:
                return jsonify({"msg": "Image Path Not Found", "details": str(e)}), 400
                
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


# POST일 때는 app - imagePath, createdAt, period 새로 추가
# PATCH일 때는 app, web - 현재 코드 그대로
# 특정 육류의 가열육 관능 검사 결과 생성 및 수정
@add_api.route("/heatedmeat-eval", methods=["POST", "PATCH"])
def add_specific_heatedmeat_sensory_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            if data:
                return create_specific_heatedmeat_seonsory_data(db_session, data), 200
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


# 특정 육류의 실험실 데이터 생성 및 수정
@add_api.route("/probexpt-data", methods=["GET", "POST"])
def add_specific_probexpt_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            if data:
                return create_specific_probexpt_data(db_session, data), 200
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

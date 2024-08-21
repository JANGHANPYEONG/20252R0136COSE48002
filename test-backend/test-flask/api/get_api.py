from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_model import Meat, User
from db.db_controller import (
    get_range_meat_data,
    get_meat,
    _getMeatDataByUserId,
    _getMeatDataByUserType,
    _getMeatDataByRangeStatusType,
    _getTexanomyData,
    _getPredictionData,
    get_OpenCVresult
)
from utils import *

get_api = Blueprint("get_api", __name__)


# 전체 육류 데이터 출력
@get_api.route("/", methods=["GET"])
def getMeatData():
    try:
        db_session = current_app.db_session
        offset = request.args.get("offset")
        count = request.args.get("count")
        start = request.args.get("start")
        end = request.args.get("end")
        specie = request.args.get("specieValue")
        if specie == '전체':
            specie_value = 2
        else:
            specie_value = species.index(specie)
        return jsonify(get_range_meat_data(db_session, offset, count, start, end, specie_value)), 200
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 ID에 해당하는 육류 데이터 출력
@get_api.route("/by-meat-id", methods=["GET"])
def getMeatDataById():
    try:
        db_session = current_app.db_session
        meat_id = request.args.get("meatId")
        if meat_id is None:
            return jsonify({"msg": "Invalid Meat ID"}), 400
        result = get_meat(db_session, meat_id)
        if result:
            return jsonify(result), 200
        else:
            return jsonify({"msg": f"No Meat data found for {meat_id}"}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# ID를 부분적으로 포함하는 육류 데이터 출력
@get_api.route("/by-partial-id", methods=["GET", "POST"])
def getMeatDataByPartialId():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            part_id = request.args.get("part_id")
            meats_with_statusType_2 = (
                db_session.query(Meat).filter_by(statusType=2).all()
            )
            meat_list = []
            for meat in meats_with_statusType_2:
                meat_list.append(meat.id)

            part_id_meat_list = [meat for meat in meat_list if part_id in meat]
            return jsonify({part_id: part_id_meat_list})
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


# 범위에 해당하는 육류 데이터 출력
@get_api.route("/by-range-data", methods=["GET", "POST"])
def getMeatDataByRangeData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            offset = request.args.get("offset")
            count = request.args.get("count")
            start = request.args.get("start")
            end = request.args.get("end")
            # filter
            farmAddr = safe_bool(request.args.get("farmAddr"))
            userId = safe_bool(request.args.get("userId"))
            type = safe_bool(request.args.get("type"))
            createdAt = safe_bool(request.args.get("createdAt"))
            statusType = safe_bool(request.args.get("statusType"))
            company = safe_bool(request.args.get("company"))
            return (
                get_range_meat_data(
                    db_session,
                    offset,
                    count,
                    start,
                    end,
                    farmAddr,
                    userId,
                    type,
                    createdAt,
                    statusType,
                    company,
                ),
                200,
            )
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


# 유저 아이디에 해당하는 육류 데이터 출력
@get_api.route("/by-user-id", methods=["GET"])
def getMeatDataByUserId():
    try:
        db_session = current_app.db_session
        userId = request.args.get("userId")
        offset = safe_int(request.args.get("offset"))
        count = safe_int(request.args.get("count"))
        start = request.args.get("start")
        end = request.args.get("end")
        if not (userId and start and end) or offset is None or count is None:
            return jsonify("Invalid parameter"), 400
        meat_by_user = _getMeatDataByUserId(db_session, userId, offset, count, start, end)
        return jsonify(meat_by_user), 200
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 유저 타입에 해당하는 육류 데이터 출력
@get_api.route("/by-user-type", methods=["GET", "POST"])
def getMeatDataByUserType():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            userType = request.args.get("userType")
            if userType:
                return _getMeatDataByUserType(db_session, userType)

            else:
                return jsonify("No userType in parameter"), 401
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


# 전체 유저별로 생성해낸 육류 데이터 출력
@get_api.route("/by-user-total", methods=["GET", "POST"])
def getMeatDataByUser():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            users = db_session.query(User).all()

            user_meats = {}
            for user in users:
                response, _ = _getMeatDataByUserId(db_session, user.userId)
                user_meats[user.userId] = response.get_json()
            return jsonify(user_meats), 200
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


# # 육류 승인 여부별 육류 데이터 출력
# @get_api.route("/by-status", methods=["GET", "POST"])
# def getMeatDataByStatusType():
#     try:
#         if request.method == "GET":
#             db_session = current_app.db_session
#             statusType_value = safe_int(request.args.get("statusType"))
#             if statusType_value:
#                 return _getMeatDataByStatusType(db_session, statusType_value)
#             else:
#                 return jsonify("No statusType in parameter"), 401
#         else:
#             return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
#     except Exception as e:
#         logger.exception(str(e))
#         return (
#             jsonify(
#                 {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
#             ),
#             505,
#         )


# 육류 승인 여부별 범위 육류 데이터 출력
@get_api.route("/by-status", methods=["GET"])
def getMeatDataByRangeStatusType():
    try:
        db_session = current_app.db_session
        status_type = request.args.get("statusType")
        offset = request.args.get("offset")
        count = request.args.get("count")
        start_str = request.args.get("start")
        end_str = request.args.get("end")
        specie_value = request.args.get("specieValue")

        start = convert2datetime(start_str, 0)
        end = convert2datetime(end_str, 0)
        if status_type is not None and specie_value is not None:
            return _getMeatDataByRangeStatusType(
                db_session, status_type, offset, count, specie_value, start, end
            )
        else:
            return jsonify("Invalid statusType or specieValue in parameter"), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# # 육류 승인 여부별 전체 육류 데이터 출력
# @get_api.route("/by-status-total", methods=["GET", "POST"])
# def getMeatDataByTotalStatusType():
#     try:
#         if request.method == "GET":
#             db_session = current_app.db_session
#             return _getMeatDataByTotalStatusType(db_session)

#         else:
#             return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
#     except Exception as e:
#         logger.exception(str(e))
#         return (
#             jsonify(
#                 {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
#             ),
#             505,
#         )


# Texanomy 하드코딩 기본 데이터 출력
@get_api.route("/default-data", methods=["GET"])
def getTexanomyData():
    try:
        db_session = current_app.db_session
        return _getTexanomyData(db_session)
    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 예측 데이터 조회
@get_api.route("/predict-data", methods=["GET"])
def getPredictionData():
    try:
        db_session = current_app.db_session
        meat_id = safe_str(request.args.get("meatId"))
        seqno = safe_int(request.args.get("seqno"))
        if meat_id and seqno is not None:
            return _getPredictionData(db_session, meat_id, seqno)
        else:
            return jsonify("Invalid id or seqno parameter"), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )
        

# opencv 결과 조회    
@get_api.route("/opencv-image", methods=["GET"])
def getOpenCVData():
    try:
        db_session = current_app.db_session
        meat_id = request.args.get("meatId")
        if meat_id:
            result = get_OpenCVresult(db_session, meat_id)
            if result:
                return jsonify({"msg": "Success to get OpenCV Result", "result": result}), 200
            else:
                return jsonify({"msg": "There Does Not Exist OpenCV Result"}), 404
        return jsonify({"msg": f"Meat Data {meat_id} Does Not Exist"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

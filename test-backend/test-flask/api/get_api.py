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
    _getMeatDataByStatusType,
    _getMeatDataByRangeStatusType,
    _getMeatDataByTotalStatusType,
    _getTexanomyData,
    _getPredictionData,
    get_user
)
from utils import *

get_api = Blueprint("get_api", __name__)


# 전체 육류 데이터 출력
@get_api.route("/", methods=["GET", "POST"])
def getMeatData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            offset = request.args.get("offset")
            count = request.args.get("count")
            return (
                get_range_meat_data(db_session, offset=offset, count=count)
                .get_json()
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


# 특정 ID에 해당하는 육류 데이터 출력
@get_api.route("/by-id", methods=["GET", "POST"])
def getMeatDataById():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = request.args.get("id")
            if id is None:
                raise Exception("Invalid Meat ID")
            result = get_meat(db_session, id)
            if result:
                user = get_user(db_session, result["userId"])["name"]
                result["name"] = user
                for k, v in result["rawmeat"].items():
                    try:
                        result["rawmeat_data_complete"] = (
                            all(
                                v is not None
                                for v in result["rawmeat"][
                                    "heatedmeat_sensory_eval"
                                ].values()
                            )
                            and all(
                                v is not None
                                for v in result["rawmeat"]["probexpt_data"].values()
                            )
                            and all(
                                (k == "deepAgingId" or v is not None)
                                for k, v in result["rawmeat"]["sensory_eval"].items()
                            )
                        )
                        userId = v["userId"]
                        user = get_user(db_session, userId)["name"]
                        v["name"] = user
                    except:
                        result["rawmeat_data_complete"] = False

                result["processedmeat_data_complete"] = {}

                for k, v in result["processedmeat"].items():
                    try:
                        result["processedmeat_data_complete"][k] = all(
                            all(vv is not None for vv in inner_v.values())
                            for inner_v in v.values()
                        )
                        for vv in v.values():
                            userId = vv["userId"]
                            user = get_user(db_session, userId)["name"]
                            vv["name"] = user
                    except:
                        result["processedmeat_data_complete"][k] = False
                if not result["processedmeat_data_complete"]:
                    result["processedmeat_data_complete"] = False
                    

                return jsonify(result)
            else:
                raise Exception(f"No Meat data found for {id}")
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
@get_api.route("/by-user-id", methods=["GET", "POST"])
def getMeatDataByUserId():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            userId = request.args.get("userId")
            if not userId:
                return jsonify("No userId in parameter"), 401
            else:
                return _getMeatDataByUserId(db_session, userId)
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


# 육류 승인 여부별 육류 데이터 출력
@get_api.route("/by-status", methods=["GET", "POST"])
def getMeatDataByStatusType():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            statusType_value = safe_int(request.args.get("statusType"))
            if statusType_value:
                return _getMeatDataByStatusType(db_session, statusType_value)
            else:
                return jsonify("No statusType in parameter"), 401
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


# 육류 승인 여부별 범위 육류 데이터 출력
@get_api.route("/by-status-range", methods=["GET", "POST"])
def getMeatDataByRangeStatusType():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            statusType_value = safe_int(request.args.get("statusType"))
            offset = safe_int(request.args.get("offset"))
            count = safe_int(request.args.get("count"))
            start_str = request.args.get('start')
            end_str = request.args.get('end')

            start = convert2datetime(start_str, 0)
            end = convert2datetime(end_str, 0)
            if statusType_value:
                return _getMeatDataByRangeStatusType(
                    db_session, statusType_value, offset, count, start, end
                )
            else:
                return jsonify("No statusType in parameter"), 401
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


# 육류 승인 여부별 전체 육류 데이터 출력
@get_api.route("/by-status-total", methods=["GET", "POST"])
def getMeatDataByTotalStatusType():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            return _getMeatDataByTotalStatusType(db_session)

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


# Texanomy 하드코딩 기본 데이터 출력
@get_api.route("/default-data", methods=["GET", "POST"])
def getTexanomyData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            return _getTexanomyData(db_session)

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


# 예측 데이터 조회
@get_api.route("/predict-data", methods=["GET", "POST"])
def getPredictionData():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = safe_str(request.args.get("id"))
            seqno = safe_str(request.args.get("seqno"))
            if id and seqno:
                return _getPredictionData(db_session, id, seqno)
            else:
                return jsonify("No id or seqno parameter"), 401

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

from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_controller import _deleteSpecificDeepAgingData, deleteMeatByIDList
from utils import *


delete_api = Blueprint("delete_api", __name__)


# 전체 육류 데이터 삭제
@delete_api.route("/", methods=["DELETE"])
def deleteTotalMeatData():
    try:
        db_session = current_app.db_session
        s3_conn = current_app.s3_conn
        id_list = request.get_json().get("id")
        
        if id_list:
            _, fail = deleteMeatByIDList(db_session, s3_conn, id_list)
            if not fail:
                return jsonify({"msg": "Success to Delete ID List"}), 200
            else:
                return jsonify({"msg": f"Fail to Delete ID List: {', '.join([id for id in fail])}"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

# 특정 육류 데이터 삭제
# @delete_api.route("/id", methods=["GET", "POST"])
# def deleteSpecificMeatData():
#     try:
#         if request.method == "GET":
#             db_session = current_app.db_session
#             s3_conn = current_app.s3_conn
#             firestore_conn = current_app.firestore_conn
#             id = safe_str(request.args.get("id"))
#             if id:
#                 return _deleteSpecificMeatData(db_session, s3_conn, firestore_conn, id)
#             else:
#                 return jsonify("No id parameter"), 401

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

# 특정 딥에이징 이력 삭제
@delete_api.route("/deep-aging", methods=["DELETE"])
def deleteDeepAgingData():
    try:
        db_session = current_app.db_session
        s3_conn = current_app.s3_conn
        id = safe_str(request.args.get("meatId"))
        seqno = safe_int(request.args.get("seqno"))
        if id and seqno:
            delete_deep_aging_data = _deleteSpecificDeepAgingData(db_session, s3_conn, id, seqno)
            return jsonify({"msg": delete_deep_aging_data["msg"]}), delete_deep_aging_data["code"]
        else:
            return jsonify({"msg": "Invalid id and seqno"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

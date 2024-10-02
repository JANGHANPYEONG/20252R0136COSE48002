from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_controller import _updateConfirmData, _updateRejectData
from utils import *

update_api = Blueprint("update_api", __name__)

# 육류 데이터 승인 API
@update_api.route("/confirm", methods=["PATCH"])
def updateConfirmData():
    try:
        db_session = current_app.db_session
        meat_id = safe_str(request.args.get("meatId"))
        if meat_id:
            return _updateConfirmData(db_session, meat_id)
        else:
            return jsonify({"msg": "No meatId parameter"}), 400
    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

# 육류 데이터 반려 API
@update_api.route("/reject", methods=["PATCH"])
def updateRejectData():
    try:
        db_session = current_app.db_session
        meat_id = safe_str(request.args.get("meatId"))
        if meat_id:
            return _updateRejectData(db_session, meat_id)
        else:
            return jsonify({"msg": "No meatId parameter"}), 400
    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

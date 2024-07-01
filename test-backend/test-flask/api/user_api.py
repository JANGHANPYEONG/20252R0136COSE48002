import logging

from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from db.db_model import User
from db.db_controller import create_user, get_user, _get_users_by_type, update_user
import hashlib
import firebase_admin
from firebase_admin import credentials, auth
from datetime import datetime
from utils import logger

user_api = Blueprint("user_api", __name__)

# Initialize logger
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# 로거 설정
logger = logging.getLogger(__name__)


# Firebase Admin SDK 초기화
cred = credentials.Certificate('serviceAccountKey.json')  # Firebase 서비스 계정 키 파일 경로
firebase_admin.initialize_app(cred)


@user_api.route("/login", methods=["GET"])
def login_user():
    try:
        # 쿼리 파라미터에서 userId 가져오기
        user_id = request.args.get('userId')
        logger.info(f"Received userId: {user_id}")

        if not user_id:
            return jsonify({"msg": "userId is required"}), 400

        # 사용자 데이터베이스에서 userId 확인
        user = User.query.filter_by(userId=user_id).first()

        if not user:
            return jsonify({"msg": "User not found"}), 404

        return jsonify({"msg": "Login successful", "userId": user.userId, "name": user.name, "type": user.type}), 200

    except Exception as e:
        logger.exception("Exception: %s", e)
        return jsonify({"msg": "Server Error"}), 500


# 유저 등록 API
@user_api.route("/register", methods=["GET", "POST"])
def register_user_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            user = create_user(db_session, data)

            db_session.add(user)
            db_session.commit()
            return jsonify({"msg": f"{data['userId']}"}), 200
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


@user_api.route("/get", methods=["GET", "POST"])
def read_user_data():
    try:
        db_session = current_app.db_session
        if request.method == "GET":
            userId = request.args.get("userId")
            if userId:
                result = get_user(db_session, userId)
            else:
                result = _get_users_by_type(db_session)

            # Ensure result is serializable
            if isinstance(result, dict):
                response_data = result
            else:
                response_data = result._asdict()

            # Remove None values from response_data
            response_data = {k: v for k, v in response_data.items() if v is not None}

            return jsonify(response_data), 200
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except AttributeError as e:
        logger.exception("AttributeError: %s", e)
        return jsonify(
            {
                "msg": "Server Error - Attribute Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        ), 505
    except Exception as e:
        logger.exception(str(e))
        return jsonify(
            {
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        ), 505

# 유저 정보 수정 API
@user_api.route("/update", methods=["GET", "POST"])
def update_user_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            user = update_user(db_session, data)

            db_session.merge(user)
            db_session.commit()
            return jsonify(get_user(db_session, data.get("userId"))), 200
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

# 유저 아이디 중복 체크 API
@user_api.route("/duplicate_check", methods=["GET", "POST"])
def check_duplicate():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = request.args.get("userId")
            user = db_session.query(User).filter_by(userId=id).first()
            if user is None:
                return jsonify({"msg": "None Duplicated Id"}), 200
            else:
                return jsonify({"msg": "Duplicated Id"}), 401
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

# 유저 비밀번호 체크 API
@user_api.route("/pwd-check", methods=["GET", "POST"])
def check_pwd():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            id = data.get("userId")
            password = data.get("password")
            user = db_session.query(User).filter_by(userId=id).first()
            if user is None:
                return (
                    jsonify(
                        {
                            "msg": f"No user data in Database",
                            "userId": id,
                        }
                    ),
                    404,
                )
            if user.password != hashlib.sha256(password.encode()).hexdigest():
                return (
                    jsonify(
                        {
                            "msg": f"Invalid password for userId",
                            "userId": id,
                        }
                    ),
                    401,
                )

            return jsonify(get_user(db_session, id)), 200
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

# 유저 정보 삭제 API
@user_api.route("/delete", methods=["GET", "POST"])
def delete_user():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            id = request.args.get("userId")
            user = db_session.query(User).filter_by(userId=id).first()
            if user is None:
                return (
                    jsonify(
                        {
                            "msg": f"No user data in Database",
                            "userId": id,
                        }
                    ),
                    404,
                )
            try:
                db_session.delete(user)
                db_session.commit()
                return (
                    jsonify(
                        {
                            f"msg": f"User with userId has been deleted",
                            "userId": id,
                        }
                    ),
                    200,
                )
            except:
                db_session.rollback()
                raise Exception("Deleted Failed")

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 401
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )



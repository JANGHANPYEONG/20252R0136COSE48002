import logging

from flask import Blueprint, jsonify, request, current_app
from db.db_model import User
from db.db_controller import create_user, get_user, _get_users_by_type, update_user

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth as firebase_auth
from datetime import datetime
from utils import logger, usrType

user_api = Blueprint("user_api", __name__)

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    default_app = firebase_admin.initialize_app(cred)

# Firestore 데이터베이스를 가져옵니다.
firebase_db = firestore.client()

# Initialize logger
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


# 로거 설정
logger = logging.getLogger(__name__)


# 유저 전체 리스트 조회 API
@user_api.route("/", methods=["GET"])
def read_user_list():
    db_session = current_app.db_session
    try:
        users = db_session.query(User).all()
        user_list = []
        for user in users:
            user_data = {
                "userId": user.userId,
                "createdAt": user.createdAt,
                "updatedAt": user.updatedAt,
                "loginAt": user.loginAt,
                "name": user.name,
                "company": user.company,
                "jobTitle": user.jobTitle,
                "homeAddr": user.homeAddr,
                "alarm": user.alarm,
                "type": user.type,
            }
            user_list.append(user_data)

        return jsonify(user_list), 200
    except:
        return jsonify({"msg": "User Not found"}), 404


# 유저 로그인 API
@user_api.route("/login", methods=["GET"])
def login_user():
    try:
        # 쿼리 파라미터에서 userId 가져오기
        user_id = request.args.get("userId")
        logger.info(f"Received userId: {user_id}")

        if not user_id:
            return jsonify({"msg": "userId is required"}), 400

        # 사용자 데이터베이스에서 userId 확인
        user = User.query.filter_by(userId=user_id).first()

        if not user:
            return jsonify({"msg": "User not found"}), 404
        return (
            jsonify(
                {
                    "msg": "Login successful",
                    "userId": user.userId,
                    "createdAt": user.createdAt,
                    "updatedAt": user.updatedAt,
                    "name": user.name,
                    "company": user.company,
                    "jobTitle": user.jobTitle,
                    "homeAddr": user.homeAddr,
                    "alarm": user.alarm,
                    "type": usrType[user.type],
                }
            ),
            200,
        )

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

            # Check if user already exists
            existing_user = (
                db_session.query(User).filter_by(userId=data["userId"]).first()
            )
            if existing_user:
                return jsonify({"msg": "User already exists"}), 400

            user = create_user(db_session, data)
            db_session.add(user)
            db_session.commit()

            # Save user to Firebase Firestore - firebase에 등록은 프론트에서 처리
            # firebase_db.collection('users').document(data['userId']).set(data)

            return (
                jsonify({"msg": f"User {data['userId']} registered successfully"}),
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


# 유저 상세 정보 조회 API
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
        return (
            jsonify(
                {
                    "msg": "Server Error - Attribute Error",
                    "time": datetime.now().strftime("%H:%M:%S"),
                }
            ),
            505,
        )
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )


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
@user_api.route("/duplicate-check", methods=["GET"])
def check_duplicate():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            userId = request.args.get("userId")
            user = db_session.query(User).filter_by(userId=userId).first()
            if user is None:
                return jsonify({"msg": "None Duplicated Id"}), 200
            else:
                return jsonify({"msg": "Duplicated Id"}), 403
        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 403
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 유저 정보 삭제 API
@user_api.route("/delete", methods=["GET", "POST"])
def delete_user():
    try:
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
            # Firebase에서 유저 삭제
            user_record = firebase_auth.get_user_by_email(id)
            firebase_auth.delete_user(user_record.uid)

            # 로컬 데이터베이스에서 유저 삭제
            db_session.delete(user)
            db_session.commit()
            return (
                jsonify(
                    {
                        "msg": f"User with userId {id} has been deleted",
                        "userId": id,
                    }
                ),
                200,
            )
        except Exception as e:
            db_session.rollback()
            logger.exception(str(e))
            return jsonify({"msg": "Delete Failed", "error": str(e)}), 500

    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

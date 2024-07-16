import logging

from flask import Blueprint, jsonify, request, current_app
from db.db_model import User
from db.db_controller import create_user, get_user, _get_users_by_type, update_user, get_all_user, delete_user

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import auth as firebase_auth
from datetime import datetime
from utils import logger, to_dict, usrType

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
        users = get_all_user(db_session)
        user_list = []
        for user in users:
            user_data = {
                "name": user.name,
                "userId": user.userId,
                "type": user.type,                
                "company": user.company,
                "createdAt": user.createdAt,
            }
            user_list.append(user_data)

        return jsonify(user_list), 200
    except:
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 유저 로그인 API
@user_api.route("/login", methods=["GET"])
def login_user():
    db_session = current_app.db_session
    try:
        # 쿼리 파라미터에서 userId 가져오기
        user_id = request.args.get("userId")
        logger.info(f"Received userId: {user_id}")

        if not user_id:
            return jsonify({"msg": "userId is required"}), 400

        # 사용자 데이터베이스에서 userId 확인
        user = get_user(db_session, user_id)

        if not user:
            return jsonify({"msg": "User not found"}), 404
        return (
            jsonify(
                {
                    "userId": user.userId,
                    "name": user.name,
                    "homeAddr": user.homeAddr,
                    "company": user.company,
                    "jobTitle": user.jobTitle,
                    "type": usrType[user.type],
                    "alarm": user.alarm,
                    "createdAt": user.createdAt,
                    "msg": "Login successful",
                }
            ),
            200,
        )

    except Exception as e:
        logger.exception("Exception: %s", e)
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

      
# 유저 등록 API
@user_api.route("/register", methods=["POST"])
def register_user_data():
    db_session = current_app.db_session
    try:
        data = request.get_json()
        user_id = data["userId"]

        # Check if user already exists
        existing_user = get_user(db_session, user_id)
        if existing_user:
            return jsonify({"msg": "User already exists"}), 400
        data["createdAt"] = datetime.now()

        create_user(db_session, data)

        # Save user to Firebase Firestore - firebase에 등록은 프론트에서 처리
        # firebase_db.collection('users').document(data['userId']).set(data)

        return (
            jsonify({"msg": f"User {user_id} registered successfully"}),
            200,
        )
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 유저 상세 정보 조회 API
# @user_api.route("/get", methods=["GET", "POST"])
# def read_user_data():
#     try:
#         db_session = current_app.db_session
#         if request.method == "GET":
#             userId = request.args.get("userId")
#             if userId:
#                 result = get_user(db_session, userId)
#             else:
#                 result = _get_users_by_type(db_session)

#             # Ensure result is serializable
#             if isinstance(result, dict):
#                 response_data = result
#             else:
#                 response_data = result._asdict()

#             # Remove None values from response_data
#             response_data = {k: v for k, v in response_data.items() if v is not None}

#             return jsonify(response_data), 200
#         else:
#             return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
#     except AttributeError as e:
#         logger.exception("AttributeError: %s", e)
#         return (
#             jsonify(
#                 {
#                     "msg": "Server Error - Attribute Error",
#                     "time": datetime.now().strftime("%H:%M:%S"),
#                 }
#             ),
#             505,
#         )
#     except Exception as e:
#         logger.exception(str(e))
#         return (
#             jsonify(
#                 {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
#             ),
#             505,
#         )


# 유저 정보 수정 API
@user_api.route("/update", methods=["PATCH"])
def update_user_data():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        data["updatedAt"] = datetime.now().strftime("%Y-%m-%d")
        update_user(db_session, data)

        
        updated_user = get_user(db_session, data.get("userId"))

        return (
            jsonify(
                {
                    "userId": updated_user.userId,
                    "name": updated_user.name,
                    "homeAddr": updated_user.homeAddr,
                    "company": updated_user.company,
                    "jobTitle": updated_user.jobTitle,
                    "alarm": updated_user.alarm,
                    "type": usrType[updated_user.type],
                    "updatedAt": updated_user.updatedAt,
                    "createdAt": updated_user.createdAt
                }
            ), 
            200,
        )
    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 유저 아이디 중복 체크 API
@user_api.route("/duplicate-check", methods=["GET"])
def check_duplicate():
    try:
        db_session = current_app.db_session
        user_id = request.args.get("userId")
        user = get_user(db_session, user_id)
        if user is None:
            return jsonify({"isDuplicated": False}), 200
        else:
            return jsonify({"isDuplicated": True}), 200
    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 유저 정보 삭제 API
@user_api.route("/delete", methods=["DELETE"])
def delete_user_data():
    try:
        db_session = current_app.db_session
        user_id = request.args.get("userId")
        user = get_user(db_session, user_id)
        if not user:
            return (
                jsonify(
                    {
                        "msg": f"No user data in Database",
                        "userId": user_id,
                    }
                ),
                401,
            )
        delete_user(db_session, user)
        return (
            jsonify(
                {
                    "msg": f"User with userId {user_id} has been deleted",
                    "userId": user_id,
                }
            ),
            200,
        )
    except Exception as e:
        # logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

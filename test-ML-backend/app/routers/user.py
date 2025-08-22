"""
FastAPI용 사용자 관리 라우터

- 원본 Flask 블루프린트(user_api)의 엔드포인트를 FastAPI 라우터로 마이그레이션
- DB 세션은 FastAPI의 app.state를 통해 주입
- Firebase 인증/인가 로직 통합
- 사용자 CRUD 작업 구현

- 경로 맵핑(원본과 동일 의도):
  GET          /user                  : 전체 사용자 리스트 조회
  GET          /user/login            : 사용자 로그인
  POST         /user/register         : 사용자 등록
  PATCH        /user/update           : 사용자 정보 수정
  GET          /user/duplicate-check  : 사용자 ID 중복 체크
  DELETE       /user/delete           : 사용자 삭제
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse

# 원본 비즈니스 로직 함수
from app.db.db_controller import create_user, get_user, update_user, get_all_user, delete_user

# Firebase 관련
import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth

# 유틸
from app.utils.utils import logger, usrType

router = APIRouter()

# Firebase 초기화 (앱이 없을 때만)
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        default_app = firebase_admin.initialize_app(cred)
    except FileNotFoundError:
        # serviceAccountKey.json이 없으면 기본 초기화
        default_app = firebase_admin.initialize_app()

# Firestore 데이터베이스
firebase_db = firestore.client()

# 로거 설정
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------
# 내부 유틸: app.state에서 공용 리소스 꺼내기
# --------------------------------------------------------------------------
def _require_state_attr(request: Request, name: str) -> Any:
    """
    FastAPI의 app.state에 등록된 리소스를 가져옴.
    미등록 시 500 에러로 안내.
    """
    if not hasattr(request.app.state, name):
        raise HTTPException(
            status_code=500,
            detail=f"Server is not configured: missing app.state.{name}",
        )
    return getattr(request.app.state, name)

# --------------------------------------------------------------------------
# 사용자 관리 엔드포인트
# --------------------------------------------------------------------------

@router.get("", summary="전체 사용자 리스트 조회")
async def read_user_list(request: Request):
    """
    - 원본: GET /
    - 모든 사용자의 기본 정보를 반환
    """
    try:
        db_session = _require_state_attr(request, "db_session")
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

        return JSONResponse(user_list, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.get("/login", summary="사용자 로그인")
async def login_user(request: Request, userId: Optional[str] = Query(None)):
    """
    - 원본: GET /login
    - userId 쿼리 파라미터로 사용자 인증
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        
        if not userId:
            return JSONResponse({"msg": "userId is required"}, status_code=400)

        logger.info(f"Received userId: {userId}")

        # 사용자 데이터베이스에서 userId 확인
        user = get_user(db_session, userId)

        if not user:
            return JSONResponse({"msg": "User not found"}, status_code=404)

        return JSONResponse(
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
            },
            status_code=200,
        )

    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.post("/register", summary="사용자 등록")
async def register_user_data(request: Request, data: Dict[str, Any]):
    """
    - 원본: POST /register
    - 새로운 사용자 등록
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        
        user_id = data.get("userId")
        if not user_id:
            return JSONResponse({"msg": "userId is required"}, status_code=400)

        # Check if user already exists
        existing_user = get_user(db_session, user_id)
        if existing_user:
            return JSONResponse({"msg": "User already exists"}, status_code=400)

        create_user(db_session, data)

        # Firebase에 등록은 프론트에서 처리
        # firebase_db.collection('users').document(data['userId']).set(data)

        return JSONResponse(
            {"msg": f"User {user_id} registered successfully"},
            status_code=200,
        )
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.patch("/update", summary="사용자 정보 수정")
async def update_user_data(request: Request, data: Dict[str, Any]):
    """
    - 원본: PATCH /update
    - 기존 사용자 정보 수정
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        
        data["updatedAt"] = datetime.now().strftime("%Y-%m-%d")
        update_user(db_session, data)

        updated_user = get_user(db_session, data.get("userId"))

        return JSONResponse(
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
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.get("/duplicate-check", summary="사용자 ID 중복 체크")
async def check_duplicate(request: Request, userId: Optional[str] = Query(None)):
    """
    - 원본: GET /duplicate-check
    - userId 중복 여부 확인
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        
        if not userId:
            return JSONResponse({"msg": "userId is required"}, status_code=400)
            
        user = get_user(db_session, userId)
        if user is None:
            return JSONResponse({"isDuplicated": False}, status_code=200)
        else:
            return JSONResponse({"isDuplicated": True}, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.delete("/delete", summary="사용자 삭제")
async def delete_user_data(request: Request, userId: Optional[str] = Query(None)):
    """
    - 원본: DELETE /delete
    - 사용자 및 관련 데이터 삭제
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        
        if not userId:
            return JSONResponse({"msg": "userId is required"}, status_code=400)
            
        user = get_user(db_session, userId)
        if not user:
            return JSONResponse(
                {
                    "msg": f"No user data in Database",
                    "userId": userId,
                },
                status_code=400,
            )
            
        delete_user(db_session, user)
        
        # Firebase에서 유저 삭제
        try:
            user_record = firebase_auth.get_user_by_email(userId)
            firebase_auth.delete_user(user_record.uid)
        except Exception as firebase_error:
            logger.warning(f"Firebase user deletion failed: {firebase_error}")
        
        return JSONResponse(
            {
                "msg": f"User with userId {userId} has been deleted",
                "userId": userId,
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        ) 
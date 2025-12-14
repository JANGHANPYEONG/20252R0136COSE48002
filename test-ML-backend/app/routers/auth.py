"""
Firebase ID 토큰을 검증하고 사용자 프로필을 조회/자동 등록하는 인증 라우터.

FastAPI `app.state.db_session`에 의존하여 DB에서 사용자 정보를 조회하며,
화이트리스트 여부에 따라 관리자 권한을 부여한 뒤 기본 프로필을 생성할 수 있다.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.config import settings
from app.core.security import verify_firebase_token
from app.db.db_controller import create_user, get_user
from app.utils.utils import usrType

router = APIRouter()


@router.get("/me", summary="내 프로필 조회 (ID 토큰 기반)")
def me(request: Request, token=Depends(verify_firebase_token)):
    db_session = getattr(request.app.state, "db_session", None)
    if db_session is None:
        raise HTTPException(
            status_code=500,
            detail="Server is not configured: missing app.state.db_session",
        )

    email = token.get("email") or token["uid"]
    user = get_user(db_session, email)

    # 없으면 옵션에 따라 자동 등록
    if not user and settings.ALLOW_AUTO_PROVISION:
        whitelist = {
            e.strip().lower()
            for e in settings.ADMIN_WHITELIST.split(",")
            if e.strip()
        }
        is_admin = email.lower() in whitelist
        data = {
            "userId": email,
            "name": token.get("name") or email.split("@")[0],
            "company": "",
            "jobTitle": "Admin" if is_admin else "User",
            "type": 1 if is_admin else 0,  # 1=Admin, 0=Normal
            "alarm": False,
            "createdAt": datetime.now().strftime("%Y-%m-%d"),
        }
        create_user(db_session, data)
        user = get_user(db_session, email)

    if not user:
        raise HTTPException(status_code=404, detail="User not found in DB")

    return {
        "userId": user.userId,
        "name": user.name,
        "homeAddr": user.homeAddr,
        "company": user.company,
        "jobTitle": user.jobTitle,
        "type": usrType[user.type],
        "alarm": user.alarm,
        "createdAt": user.createdAt,
    }

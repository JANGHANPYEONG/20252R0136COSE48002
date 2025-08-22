from fastapi import APIRouter, Depends, Request, HTTPException
from datetime import datetime
from app.core.security import verify_firebase_token
from app.core.config import settings
from app.db.db_controller import get_user, create_user
from app.utils.utils import usrType

router = APIRouter()

@router.get("/me", summary="내 프로필 조회 (ID 토큰 기반)")
def me(request: Request, token = Depends(verify_firebase_token)):
    db_session = getattr(request.app.state, "db_session", None)
    if db_session is None:
        raise HTTPException(status_code=500, detail="Server is not configured: missing app.state.db_session")

    email = token.get("email") or token["uid"]
    user = get_user(db_session, email)

    # ✅ 없으면 자동 등록(옵션)
    if not user and settings.ALLOW_AUTO_PROVISION:
        wl = {e.strip().lower() for e in settings.ADMIN_WHITELIST.split(",") if e.strip()}
        is_admin = (email.lower() in wl)
        data = {
            "userId": email,
            "name": token.get("name") or email.split("@")[0],
            "company": "",
            "jobTitle": "Admin" if is_admin else "User",
            "type": 1 if is_admin else 0,  # 1=Admin, 0=Normal (프로젝트 매핑에 맞춤)
            "alarm": False,
            "createdAt": datetime.now().strftime("%Y-%m-%d"),
        }
        create_user(db_session, data)
        user = get_user(db_session, email)

    if not user:
        # 자동 등록 OFF거나, 생성 실패
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

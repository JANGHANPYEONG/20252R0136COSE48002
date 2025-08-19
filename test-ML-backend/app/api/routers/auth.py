# app/routers/auth.py
from fastapi import APIRouter, Depends, Request, HTTPException
from app.core.security import verify_firebase_token
from app.db.db_controller import get_user
from app.utils.utils import usrType

router = APIRouter()

@router.get("/me", summary="내 프로필 조회 (ID 토큰 기반)")
def me(request: Request, token = Depends(verify_firebase_token)):
    db_session = getattr(request.app.state, "db_session", None)
    if db_session is None:
        raise HTTPException(status_code=500, detail="Server is not configured: missing app.state.db_session")

    email_or_uid = token.get("email") or token["uid"]
    user = get_user(db_session, email_or_uid)
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

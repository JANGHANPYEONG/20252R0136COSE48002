# app/deps.py
from fastapi import Request, HTTPException, status
from firebase_admin import auth as admin_auth

def verify_firebase_token(request: Request):
    h = request.headers.get("Authorization", "")
    if not h.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = h.split(" ", 1)[1]
    try:
        return admin_auth.verify_id_token(token)  # uid/email 등 포함
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# app/firebase_auth.py
import os, firebase_admin
from firebase_admin import credentials

def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

init_firebase()  # import 시 1회 초기화

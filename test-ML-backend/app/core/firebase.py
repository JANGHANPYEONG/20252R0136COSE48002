import os, json, firebase_admin
from firebase_admin import credentials

def init_firebase():
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
        with open(cred_path) as f:
            print("[Firebase] project_id =", json.load(f)["project_id"])
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
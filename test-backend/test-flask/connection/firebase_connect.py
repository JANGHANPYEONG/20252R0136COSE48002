from flask import send_file
import firebase_admin  # Firestore init
from datetime import datetime  # 시간 출력용
from firebase_admin import firestore, storage
import io
import os


# FireBase Data(FireStore & FireStorage)
class FireBase_:
    def __init__(self,KEY_PATH):
        try:
            # 1. Making FireStore Connection
            cred = firebase_admin.credentials.Certificate(KEY_PATH)
            firebase_admin.initialize_app(cred)
            self.firebase_db = firestore.client()
            self.fix_data_state = dict()  # 바뀐게 있는 데이터 저장

            # 2. Making FireStorage Connection
            self.bucket = storage.bucket(os.getenv("FIREBASE_BUCKET_ADDRESS"))
        except Exception as e:
            print(e)
        else:
            print("Firebase OKAY")
        # 2-1. 저장할 이미지 디렉토리가 없다면 생성합니다.
        os.makedirs("images/sensory_evals", exist_ok=True)
        os.makedirs("images/qr_codes", exist_ok=True)
        os.makedirs("images/heatedmeat_sensory_evals", exist_ok=True)

    def firestorage2server(self, type, item_id):
        """
        Firebase Storage -> Flask server
        Params
        1. type : "meats" or "qr_codes"
        2. item_id: meat.id (육류 관리번호)

        Return
        1. True: 전송 성공
        2. False: 전송 실패
        """
        blob = self.bucket.blob(f"{type}/{item_id}.png")
        if blob.exists():
            blob.download_to_filename(f"./images/{type}/{item_id}.png")
            return True
        else:
            print(f"No such file in Firebase Storage: {type}/{item_id}.png")
            return False

    def delete_from_firestorage(self, folder, item_id):
        # 1. blob 지정
        blob = self.bucket.blob(f"{folder}/{item_id}.png")

        # 2. delete blob
        if blob.exists():
            blob.delete()
            print(f"Deleted file: {folder}/{item_id}.png")
        else:
            print(f"No such file to delete: {folder}/{item_id}.png")
    
    def server2firestorage(
        self, filepath, blob_name
    ):  # Firebase Storage에 image 데이터 넣기 (Storage <- Flask Server)
        blob = self.bucket.blob(blob_name)
        blob.upload_from_filename(filename=filepath, content_type="image/png")

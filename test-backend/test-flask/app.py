# 서버 메인 파일
import sys

from flask import Flask, current_app
from flask_cors import CORS
from dotenv import load_dotenv
import os

from flask_sqlalchemy import SQLAlchemy

from db.db_model import initialize_db
from connection.firebase_connect import FireBase_
from connection.s3_connect import S3_

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 환경 변수 다운로드
load_dotenv()  

app = Flask(__name__)
    
# RDS DB 연결
db_uri = os.getenv("DB_URI")
if not db_uri:
    raise RuntimeError("DB_URI 환경 변수가 설정되지 않았습니다.")
app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
CORS(app)


def initialize_services(app):
    with app.app_context():
        # 1. DB Session Connection
        initialize_db(app)

        # 2. S3 Connection
        s3_conn = S3_(
            s3_bucket_name=os.getenv("S3_BUCKET_NAME"),
            service_name="s3",
            region_name=os.getenv("S3_REGION_NAME"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        current_app.s3_conn = s3_conn

        # 3. Firebase Connection
        firebase_conn = FireBase_("serviceAccountKey.json")
        current_app.firestore_conn = firebase_conn
        
        # Firestore 초기화
        current_app.firestore_db = firebase_conn.firebase_db
    
    
# 서비스 초기화
initialize_services(app)
    
# API Blueprint Connection
from api.user_api import user_api
from api.add_api import add_api
from api.get_api import get_api
from api.update_api import update_api
from api.delete_api import delete_api
from api.statistic_api import statistic_api
    
app.register_blueprint(user_api, url_prefix="/user")  # user 관련 API
app.register_blueprint(add_api, url_prefix="/meat/add")  # 육류 정보 생성 API
app.register_blueprint(get_api, url_prefix="/meat/get")  # 육류 정보 조회 API
app.register_blueprint(update_api, url_prefix="/meat/update")  # 육류 정보 수정 API
app.register_blueprint(delete_api, url_prefix="/meat/delete")  # 육류 정보 삭제 API
app.register_blueprint(statistic_api, url_prefix="/meat/statistic")  # 통계 데이터 조회 API

@app.route("/")
def hello_world():
    return "Hello, World!"

# Flask 실행
if __name__ == "__main__":
    app.run(debug=True, port=8080)
    
import firebase_admin
import psycopg2 as pg2
from firebase_admin import credentials
from firebase_admin import auth
from dotenv import load_dotenv
from datetime import datetime
import os

# .env 파일 로드
load_dotenv()


# DB 상의 전체 유저 수 가져오기
def get_user_count_from_RDS():
    conn = pg2.connect(database=os.getenv("DATABASE_NAME"),
                        host=os.getenv("DATABASE_HOST"),
                        port=os.getenv("DATABASE_PORT"),
                        user=os.getenv("DATABASE_USER"),
                        password=os.getenv("DATABASE_PASSWORD"))
    try:
        cur = conn.cursor()
        cur.execute('SELECT COUNT(DISTINCT "userId") FROM "user"')
        cnt = cur.fetchone()[0]
    finally:
        cur.close()
        conn.close()
    return cnt

# Firebase Admin SDK 초기화
cred = credentials.Certificate("/home/ubuntu/Deeplant-Dev/deeplant-admin/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# firebase 상의 전체 유저 수 가져오기
def get_user_count_from_Firebase():
    page = auth.list_users()
    total_users = 0
    while page:
        total_users += len(page.users)
        page = page.get_next_page()
    return total_users


if __name__ == "__main__": 
    db_user = get_user_count_from_RDS()
    firebase_user = get_user_count_from_Firebase()
    
    time = datetime.now()
    print(f"--------------- {time.strftime('%Y년 %m월 %d일')} ---------------")
    print(f"User in RDS: {db_user}\nUser in Firebase: {firebase_user}")
    if db_user == firebase_user:
        print("User Count Match!")
    else:
        print(f"There Exists Diff from RDS and Firebase User Info\n RDS user count - Firebase user count = {db_user - firebase_user}\n\n")

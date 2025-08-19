import os

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://user:pw@host:5432/dbname")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2")
CONCURRENCY = int(os.getenv("CONCURRENCY", "4"))  # 동시 예측 개수 제한
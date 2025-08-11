"""
FastAPI용 외부 서비스 연결 관리 모듈
"""
import os
from typing import Optional
from ..core.config import settings
from ..connection.firebase_connect import FireBase_
from ..connection.s3_connect import S3_

class ConnectionManager:
    """
    외부 서비스 연결을 관리하는 클래스
    """
    def __init__(self):
        self._firebase_conn: Optional[FireBase_] = None
        self._s3_conn: Optional[S3_] = None
        self._db_session = None
        
    def get_firebase_connection(self) -> FireBase_:
        """
        Firebase 연결을 반환합니다.
        """
        if self._firebase_conn is None:
            try:
                # serviceAccountKey.json 파일 경로 확인
                key_path = "serviceAccountKey.json"
                if not os.path.exists(key_path):
                    raise FileNotFoundError(f"Firebase service account key not found: {key_path}")
                
                self._firebase_conn = FireBase_(key_path)
                print("Firebase connection established successfully")
            except Exception as e:
                print(f"Error establishing Firebase connection: {e}")
                raise
        return self._firebase_conn
    
    def get_s3_connection(self) -> S3_:
        """
        S3 연결을 반환합니다.
        """
        if self._s3_conn is None:
            try:
                self._s3_conn = S3_(
                    s3_bucket_name=settings.S3_BUCKET_NAME,
                    service_name="s3",
                    region_name=settings.S3_REGION_NAME,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                )
                print("S3 connection established successfully")
            except Exception as e:
                print(f"Error establishing S3 connection: {e}")
                raise
        return self._s3_conn
    
    def set_db_session(self, db_session):
        """
        데이터베이스 세션을 설정합니다.
        """
        self._db_session = db_session
    
    def get_db_session(self):
        """
        데이터베이스 세션을 반환합니다.
        """
        return self._db_session
    
    def close_connections(self):
        """
        모든 연결을 종료합니다.
        """
        if self._firebase_conn:
            # Firebase 연결 종료 로직 (필요시)
            pass
        if self._s3_conn:
            # S3 연결 종료 로직 (필요시)
            pass
        if self._db_session:
            self._db_session.remove()

# 전역 연결 관리자 인스턴스
connection_manager = ConnectionManager()

def get_connection_manager() -> ConnectionManager:
    """
    연결 관리자 인스턴스를 반환합니다.
    """
    return connection_manager

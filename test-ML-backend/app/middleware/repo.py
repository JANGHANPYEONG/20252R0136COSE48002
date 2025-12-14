# repo.py
from typing import Optional, TypedDict

class MeatRecord(TypedDict, total=False):
    traceNo: str
    # 둘 중 하나만 채워지면 됨
    image_path: str        # EBS 로컬 경로 (예: "/data/meat/L017.../img.png")
    s3_bucket: str         # S3 버킷
    s3_key: str            # S3 오브젝트 키
    meta: dict             # (선택) 도축번호, 업로드시각 등

class DataRepository:
    def __init__(self, db_url: str):
        self.db_url = db_url

    def get_by_trace(self, trace_no: str) -> Optional[MeatRecord]:
        """
        traceNo로 레코드를 조회한다.
        팀 DB 스키마에 맞게 실제 쿼리 구현하세요.
        """
        if trace_no.startswith("L"):
            return {
                "traceNo": trace_no,
                "image_path": f"/data/meat/{trace_no}/image.png",
                "meta": {"slaughterNo": "2025-08-01-1234"}
            }
        return None

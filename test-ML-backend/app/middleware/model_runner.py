# model_runner.py
from __future__ import annotations
import os
from typing import Dict, Any, Tuple
from settings import AWS_REGION
from repo import MeatRecord

# (선택) S3 읽기 지원
import boto3

# ---- 기존 파이프라인을 감싸는 래퍼 ----
# 예: from my_pipeline import run_inference
# run_inference(image_path="/path/..") -> Dict[str, Any]
# run_inference(image_bytes=b"...")    -> Dict[str, Any]
def run_inference(*, image_path: str | None = None, image_bytes: bytes | None = None) -> Dict[str, Any]:
    """
    여기를 '이미 존재하는 파이프라인 함수'로 연결하세요.
    이미지 경로 또는 바이트 중 하나만 주면 됩니다.
    반환 형식은 팀 표준(JSON 직렬화 가능한 dict)으로.
    """
    # ---- TODO: 실제 파이프라인 호출로 교체 ----
    # 아래는 데모용 더미 결과
    return {"overall": 7.1, "color": 7.2, "aroma": 6.8, "texture": 6.9, "juiciness": 6.5, "flavor": 7.1}

class ModelRunner:
    def __init__(self):
        self._s3 = boto3.client("s3", region_name=AWS_REGION)

    def _load_from_eBS(self, path: str) -> Tuple[str, bytes | None]:
        if not os.path.exists(path):
            raise FileNotFoundError(f"이미지 파일 없음: {path}")
        # 파이프라인이 파일 경로를 받는다면 bytes 불필요
        return path, None

    def _load_from_s3(self, bucket: str, key: str) -> Tuple[str | None, bytes]:
        obj = self._s3.get_object(Bucket=bucket, Key=key)
        return None, obj["Body"].read()

    def predict_record(self, rec: MeatRecord) -> Dict[str, Any]:
        """
        DB 레코드 → 파이프라인 입력 구성 → 예측 결과 dict 반환
        """
        if rec.get("image_path"):
            path, content = self._load_from_eBS(rec["image_path"])
            return run_inference(image_path=path, image_bytes=content)
        elif rec.get("s3_bucket") and rec.get("s3_key"):
            path, content = self._load_from_s3(rec["s3_bucket"], rec["s3_key"])
            return run_inference(image_path=path, image_bytes=content)
        else:
            raise ValueError("이미지 위치 정보가 없습니다(image_path 또는 s3_bucket/key).")

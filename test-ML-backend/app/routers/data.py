# app/routers/data_upload.py
from __future__ import annotations

import json
import re
from typing import List, Optional

from fastapi import APIRouter, Form, HTTPException, Depends, Request
from sqlalchemy.orm import Session
import boto3
from botocore.config import Config

from app.db.database import get_db
from app.db.db_model import Meat, SensoryEval, HSIImagesBands, HSISensoryEval, AI_HSISensoryEval, AI_SensoryEval
from app.utils import safe_int, safe_float, safe_str, convert_to_datetime
from app.core.config import settings

router = APIRouter()

# S3 클라이언트 설정
s3_client = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.S3_REGION_NAME,
    config=Config(signature_version='s3v4')
)

@router.get("/upload/presigned-url")
async def get_presigned_url(
    filename: str,
    content_type: str = "image/jpeg",
    expiration: int = 3600,  # 1시간 기본값
):
    """
    S3 업로드를 위한 presigned URL을 생성합니다.
    
    Args:
        filename: 업로드할 파일명 (예: hash_430nm.jpg)
        content_type: 파일의 MIME 타입
        expiration: URL 만료 시간 (초)
    
    Returns:
        presigned_url: S3 업로드용 URL
        fields: multipart form fields
        bucket: S3 버킷명
        key: S3 키 (경로)
    """
    try:
        # 파일명 검증 (HSI 이미지 패턴 확인)
        if not WL_PAT.search(filename):
            raise HTTPException(
                status_code=400, 
                detail="Invalid filename format. Expected pattern: hash_wavelengthnm.jpg"
            )
        
        # S3 키 생성 (고정 경로 사용)
        s3_key = f"train_dataset/HSI/{filename}"
        
        # presigned POST URL 생성 (multipart form upload용)
        presigned_post = s3_client.generate_presigned_post(
            Bucket=settings.S3_BUCKET_NAME,
            Key=s3_key,
            Fields={
                'Content-Type': content_type,
            },
            Conditions=[
                {'Content-Type': content_type},
                ['content-length-range', 0, 10485760],  # 최대 10MB
            ],
            ExpiresIn=expiration
        )
        
        return {
            "presigned_url": presigned_post['url'],
            "fields": presigned_post['fields'],
            "bucket": settings.S3_BUCKET_NAME,
            "key": s3_key,
            "filename": filename,
            "expires_in": expiration
        }
        
    except Exception as e:
        print(f"[ERROR] Failed to generate presigned URL: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")

# *_430nm.jpg 같은 패턴에서 파장 추출
WL_PAT = re.compile(r'(?<!\d)(\d{3,4})nm(?!\w)', re.IGNORECASE)

def _to_bool(val) -> Optional[bool]:
    if isinstance(val, bool):
        return val
    if val is None:
        return None
    s = str(val).strip().lower()
    if s in {"y", "yes", "true", "1"}:
        return True
    if s in {"n", "no", "false", "0"}:
        return False
    return None

def _pack_xy(pt):
    """(x, y) -> 32bit int 로 패킹 (x:상위 16비트, y:하위 16비트)"""
    if not pt:
        return None
    # pt가 리스트/튜플/(x,y) 문자열 등일 수 있어 보정
    if isinstance(pt, str):
        # "(1992, 941)" 같은 문자열일 수 있음
        pt = pt.strip().strip("()").split(",")
    try:
        x = int(pt[0])
        y = int(pt[1])
    except Exception:
        return None
    x = max(0, min(x, 0xFFFF))
    y = max(0, min(y, 0xFFFF))
    return (x << 16) | y

@router.post("/ingest/row-upload")
async def ingest_row_upload(
    request: Request,
    payload: str = Form(..., description="한 행의 JSON(문자열)"),
    overwrite: bool = Form(False, description="동일 키 존재 시 덮어쓰기 여부"),
    db: Session = Depends(get_db),
):
    """
    프론트엔드에서 S3 업로드 완료 후 호출하는 API입니다.
    JSON payload에서 ID와 filename을 받아서 DB에 기록합니다.
    """
    # 로깅 추가
    print(f"[DEBUG] Received request:")
    print(f"[DEBUG] payload: {payload}")
    print(f"[DEBUG] overwrite: {overwrite}")
    
    # Request body 전체 로깅
    print(f"[DEBUG] Request content type: {request.headers.get('content-type')}")
    print(f"[DEBUG] Request headers: {dict(request.headers)}")
    
    # -------------------------------
    # 1) JSON 파싱 + 최소 검증
    # -------------------------------
    try:
        obj = json.loads(payload)
        print(f"[DEBUG] Parsed JSON: {obj}")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parse error: {e}")
        raise HTTPException(status_code=400, detail=f"payload JSON parse error: {e}")

    try:
        user_id = safe_str(obj.get("userId"))  # 루트
        row_id = safe_str(obj.get("rowId"))    # 선택
        meat = obj["meat"]
        
        # 프론트엔드에서 생성한 ID를 받음
        uid = safe_str(obj.get("id"))  # 프론트엔드에서 생성한 해시 ID
        if not uid:
            raise HTTPException(status_code=400, detail="missing field: id")
        
        trace_num = safe_str(meat["traceNum"])
        sample_num = safe_str(meat["sampleNum"])
        seqno = safe_int(meat.get("seqno", 1))  # 가공 횟수, 기본값 1
        
        # 프론트엔드에서 S3 업로드 완료한 filename들을 받음
        hsi_filenames = obj.get("hsiFilenames", [])  # S3에 업로드된 HSI 파일명들
        if not hsi_filenames:
            raise HTTPException(status_code=400, detail="missing field: hsiFilenames")
        
        hsi_meta = meat.get("hsi") or {}
        expected_count = safe_int(hsi_meta.get("expectedCount"))
        is_refrig_meta = _to_bool(hsi_meta.get("isRefrigerated"))
        edge_points = (meat.get("edgePoint") or {})
        
        print(f"[DEBUG] Extracted data:")
        print(f"[DEBUG]   user_id: {user_id}")
        print(f"[DEBUG]   row_id: {row_id}")
        print(f"[DEBUG]   uid: {uid}")
        print(f"[DEBUG]   trace_num: {trace_num}")
        print(f"[DEBUG]   sample_num: {sample_num}")
        print(f"[DEBUG]   hsi_filenames: {hsi_filenames}")
        print(f"[DEBUG]   expected_count: {expected_count}")
        print(f"[DEBUG]   edge_points: {edge_points}")
        
    except KeyError as e:
        print(f"[ERROR] Missing field: {e}")
        raise HTTPException(status_code=400, detail=f"missing field: {e}")

    # 선택: 기대 개수 검증 (정책에 맞게 강제/완화)
    if expected_count is not None and expected_count > 0:
        print(f"[DEBUG] Expected HSI images: {expected_count}, actual: {len(hsi_filenames)}")
        # 강제하고 싶으면 if len(hsi_filenames) != expected_count: raise ...
        # 지금은 경고만
        pass

    # -------------------------------
    # 2) S3 경로 구성
    # -------------------------------
    # 고정된 S3 경로 사용: /train_dataset/HSI/
    s3_bucket = settings.S3_BUCKET_NAME
    s3_prefix = "train_dataset/HSI"
    
    def to_uri(filename: str) -> str:
        return f"s3://{s3_bucket}/{s3_prefix}/{filename}"
    
    def to_key(filename: str) -> str:
        return f"{s3_prefix}/{filename}"
    
    # 대표 이미지 (첫 번째 HSI 이미지)
    representative_name = hsi_filenames[0] if hsi_filenames else None
    representative_uri = to_uri(representative_name) if representative_name else None
    print(f"[DEBUG] Representative image: {representative_name} -> {representative_uri}")

    # 파장 수집(이번 요청 범위에서) → 순서대로 spectral_index 할당
    wavelengths = []
    for filename in hsi_filenames:
        m = re.search(r'_(\d{3,4})nm\.png$', filename, re.I)
        if m:
            wavelengths.append(int(m.group(1)))
    wavelengths = sorted(set(wavelengths))
    print(f"[DEBUG] Wavelengths found: {wavelengths}")

    def spectral_index_for_nm(nm: int) -> Optional[int]:
        # 파장을 순서대로 spectral_index 할당 (0부터 시작)
        try:
            return wavelengths.index(nm)
        except ValueError:
            return None

    # 냉장여부: 메타 우선, 없으면 period 기반 추정(예시)
    period = None
    if meat.get("period"):
        try:
            # "Day7" → 7
            period = safe_int(str(meat.get("period")).strip().lower().replace("day", ""))
        except Exception:
            period = None
    is_refrig = is_refrig_meta if is_refrig_meta is not None else (True if (period and period > 1) else False)
    print(f"[DEBUG] Period: {period}, is_refrig: {is_refrig}")

    # -------------------------------
    # 3) DB upsert/insert (트랜잭션)
    # -------------------------------
    try:
        print(f"[DEBUG] Starting database operations...")
        
        # ── Meat upsert ───────────────────────────────────────────
        meat_row = db.query(Meat).filter(Meat.id == uid).one_or_none()
        if meat_row is None:
            meat_row = Meat(
                id=uid,
                userId=user_id,
                categoryId=None,
                gradeNum=safe_str(meat.get("gradeNum")),
                statusType=None,
                createdAt=convert_to_datetime(None, 1),   # util에 맞게 현재시간
                updatedAt=convert_to_datetime(None, 1),
                traceNum=trace_num,
                farmAddr=None,
                farmerName=None,
                butcheryYmd=convert_to_datetime(meat.get("butcheryDate"), 2),
                birthYmd=None,
                imagePath=None,
            )
            db.add(meat_row)
            print(f"[DEBUG] Created new Meat record: {uid}")
        else:
            meat_row.gradeNum = safe_str(meat.get("gradeNum"))
            meat_row.updatedAt = convert_to_datetime(None, 1)
            if representative_uri:
                meat_row.imagePath = representative_uri   # ✅ 갱신
            print(f"[DEBUG] Updated existing Meat record: {uid}")

        # ── SensoryEval insert ───────────────────────────────────
        meat_sensory = SensoryEval(
            id=uid,
            seqno=seqno,  # payload에서 받은 가공 횟수
            isRefrigerated=is_refrig,
            createdAt=convert_to_datetime(None, 1),
            userId=user_id,
            period=period,
            filmedAt=convert_to_datetime(meat.get("picturedDate"), 2),
            imagePath=None,  # HSI 이미지이므로 None
            weight_kg=None,
            marbling=safe_float(meat.get("marbling")),
            color=safe_float(meat.get("meatColor")),
            texture=safe_float(meat.get("texture")),
            surfaceMoisture=safe_float(meat.get("surfaceMoisture")),
            overall=safe_float(meat.get("total")),
            manufactureYmd=convert_to_datetime(meat.get("manufactureDate"), 2),
            expireYmd=convert_to_datetime(meat.get("expirationDate"), 2),
        )
        db.add(meat_sensory)
        print(f"[DEBUG] Added SensoryEval record: {uid}")

        # MeatImage 테이블은 사용하지 않음 - SensoryEval.imagePath와 HSIImagesBands.filename에 직접 저장
        print(f"[DEBUG] Skipping MeatImage table, using existing tables")

        # ── HSIImagesBands rows ─────────────────────────────────
        #   각 파장별 좌표와 s3 uri 저장
        bands_rows: List[HSIImagesBands] = []
        for filename in hsi_filenames:
            m2 = re.search(r'_(\d{3,4})nm\.png$', filename, re.I)
            if not m2:
                continue
            nm = int(m2.group(1))
            sp_idx = spectral_index_for_nm(nm)

            suffix = f"({nm}nm)"
            tl = _pack_xy(edge_points.get(f"TL {suffix}"))
            tr = _pack_xy(edge_points.get(f"TR {suffix}"))
            bl = _pack_xy(edge_points.get(f"BL {suffix}"))
            br = _pack_xy(edge_points.get(f"BR {suffix}"))

            bands_rows.append(
                HSIImagesBands(
                    id=uid,
                    seqno=seqno,                     # SensoryEval과 동일한 seqno
                    isRefrigerated=is_refrig,        # boolean NN
                    spectral_index=sp_idx,           # NOT NULL이면 None 방지
                    filename=to_uri(filename),       # ✅ S3 경로(URI)
                    topLeft=tl,
                    topRight=tr,
                    bottomLeft=bl,
                    bottomRight=br,
                )
            )
        print(f"[DEBUG] Created {len(bands_rows)} HSIImagesBands records")

        # ── HSISensoryEval insert ───────────────────────────────────
        hsi_sensory = HSISensoryEval(
            id=uid,
            seqno=seqno,  # SensoryEval과 동일한 seqno
            isRefrigerated=is_refrig,
            createdAt=convert_to_datetime(None, 1),
            xai_imagePath=None,
            xai_gradeNum=None,
            xai_gradeNum_imagePath=None,
            Marbling=safe_float(meat.get("marbling")),
            Meat_Color=safe_float(meat.get("meatColor")),
            Texture=safe_float(meat.get("texture")),
            Surface_Moisture=safe_float(meat.get("surfaceMoisture")),
            Total=safe_float(meat.get("total")),
        )
        db.add(hsi_sensory)
        print(f"[DEBUG] Added HSISensoryEval record: {uid}")

        # ── AI_HSISensoryEval insert ───────────────────────────────────
        ai_hsi_sensory = AI_HSISensoryEval(
            id=uid,
            seqno=seqno,  # SensoryEval과 동일한 seqno
            isRefrigerated=is_refrig,
            createdAt=convert_to_datetime(None, 1),
            xai_imagePath=None,
            xai_gradeNum=None,
            xai_gradeNum_imagePath=None,
            Marbling=None,  # AI 예측 결과이므로 현재는 None
            Meat_Color=None,
            Texture=None,
            Surface_Moisture=None,
            Total=None,
        )
        db.add(ai_hsi_sensory)
        print(f"[DEBUG] Added AI_HSISensoryEval record: {uid}")

        # ── AI_SensoryEval insert ───────────────────────────────────
        ai_sensory = AI_SensoryEval(
            id=uid,
            seqno=seqno,  # SensoryEval과 동일한 seqno
            isRefrigerated=is_refrig,
            createdAt=convert_to_datetime(None, 1),
            xai_imagePath=None,
            xai_gradeNum=None,
            xai_gradeNum_imagePath=None,
            marbling=None,  # AI 예측 결과이므로 현재는 None
            color=None,
            texture=None,
            surfaceMoisture=None,
            overall=None,
        )
        db.add(ai_sensory)
        print(f"[DEBUG] Added AI_SensoryEval record: {uid}")

        db.add_all(bands_rows)
        db.commit()
        print(f"[DEBUG] Database commit successful")

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"db error: {e}")

    # -------------------------------
    # 4) 정상 응답
    # -------------------------------
    result = {
        "ok": True,
        "id": uid,
        "userId": user_id,
        "rowId": row_id,
        "traceNum": trace_num,
        "sampleNum": sample_num,
        "hsiFilenames": hsi_filenames,
        "s3": f"s3://{s3_bucket}/{s3_prefix}/",
        "imagePath": representative_uri,  # ✅ 대표 이미지 경로
    }
    print(f"[DEBUG] Returning success response: {result}")
    return result
# app/routers/data_upload.py
from __future__ import annotations

import io
import json
import re
import tempfile
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image

# utils 업로더 불러오기
from app.utils.s3_uploader import upload_local_to_s3_prefix

router = APIRouter()

# *_430nm.jpg 같은 패턴에서 파장 추출
WL_PAT = re.compile(r'(?<!\d)(\d{3,4})nm(?!\w)', re.IGNORECASE)

# Base62 유틸 (sha256 → int → base62 → 앞 20자)
import hashlib, string
_BASE62 = string.digits + string.ascii_letters

def _base62(n: int) -> str:
    if n == 0:
        return _BASE62[0]
    out = []
    while n > 0:
        n, r = divmod(n, 62)
        out.append(_BASE62[r])
    return ''.join(reversed(out))

def make_hash(trace_num: str, sample_num: str, length: int = 20) -> str:
    raw = f"{trace_num}-{sample_num}"
    digest = hashlib.sha256(raw.encode()).digest()
    num = int.from_bytes(digest, 'big')
    return _base62(num)[:length]

def _looks_rgb(name: str) -> bool:
    n = (name or "").lower()
    return "rgb" in n

def _ensure_jpg(image_bytes: bytes) -> bytes:
    """이미지를 열어 JPEG로 변환해서 바이트로 반환"""
    im = Image.open(io.BytesIO(image_bytes))
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    out = io.BytesIO()
    im.save(out, format="JPEG", quality=95)
    return out.getvalue()


@router.post("/ingest/row-upload")
async def ingest_row_upload(
    payload: str = Form(..., description="한 행의 JSON(문자열)"),
    images: Optional[List[UploadFile]] = File(
        None, description="이 행에 해당하는 이미지들(RGB 1 + HSI 여러 장)"
    ),
    s3: str = Form(..., description="업로드 대상 S3 경로(prefix). 예: s3://bucket/prefix"),
    overwrite: bool = Form(False, description="동일 키 존재 시 덮어쓰기 여부"),
):
    """
    한 행(JSON) + 여러 이미지 파일을 받아서,
    규칙에 맞춰 파일명을 {hash}_{wavelength}.jpg / {hash}_rgb.jpg 로 바꾼 뒤
    app.utils.s3_uploader.upload_local_to_s3_prefix 로 S3에 업로드합니다.
    """

    # 1) JSON 파싱(최소 검증)
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"payload JSON parse error: {e}")

    # 필수 값 확인
    try:
        meat = obj["meat"]
        trace_num = str(meat["traceNum"]).strip()
        sample_num = str(meat["sampleNum"]).strip()
        rgb_names = set([n.lower() for n in (meat.get("rgbImageName") or [])])
        hsi_names = set([n.lower() for n in (meat.get("hsiImageName") or [])])
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"missing field: {e}")

    if not images or len(images) == 0:
        raise HTTPException(status_code=400, detail="no images uploaded")

    # 2) 해시 생성
    h = make_hash(trace_num, sample_num, length=20)

    # 3) 임시 디렉토리 준비
    tmpdir = tempfile.mkdtemp(prefix="rowu_")

    # 4) 업로드할 파일 만들기 (리네임/변환)
    saved_files = []  # (local_path, new_filename)
    try:
        for uf in images:
            orig_name = (uf.filename or "").strip()
            if not orig_name:
                raise HTTPException(status_code=400, detail="an image has empty filename")

            raw = await uf.read()
            # JPEG로 변환(확장자와 무관하게 규격화)
            jpg_bytes = _ensure_jpg(raw)

            # RGB 판정: 파일명이 rgb 포함 or payload의 rgbImageName에 명시된 경우
            is_rgb = _looks_rgb(orig_name) or (orig_name.lower() in rgb_names)

            new_fname = None
            if is_rgb:
                new_fname = f"{h}_rgb.jpg"
            else:
                # 파장 추출: 파일명 또는 hsiImageName 매핑
                wl = None
                m = WL_PAT.search(orig_name)
                if m:
                    wl = f"{m.group(1)}nm"
                else:
                    # payload의 hsiImageName 리스트에 있는지 확인(파일명 그대로 매칭)
                    if orig_name.lower() in hsi_names:
                        # 파일명에 파장이 없으면 규칙상 반드시 있어야 하므로 에러로 처리
                        raise HTTPException(status_code=400, detail=f"no wavelength in filename: {orig_name}")
                if not wl:
                    raise HTTPException(status_code=400, detail=f"cannot detect wavelength from filename: {orig_name}")
                new_fname = f"{h}_{wl}.jpg"

            # 로컬 저장
            out_path = f"{tmpdir}/{new_fname}"
            with open(out_path, "wb") as f:
                f.write(jpg_bytes)
            saved_files.append((out_path, new_fname))

        # 5) S3 업로드 (디렉토리 전체 업로드 → 키는 파일명 기준)
        summary = upload_local_to_s3_prefix(
            local_path=tmpdir,
            s3_path=s3,
            overwrite=overwrite,
            workers=8,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"processing error: {e}")

    return {
        "ok": True,
        "hash": h,
        "traceNum": trace_num,
        "sampleNum": sample_num,
        "saved": [name for _, name in saved_files],
        "s3": s3,
        "uploadSummary": summary,
    }
    
"""
{
  "userId": "deeplant@example.com",
  "rowId": "sheet1-42",            // 선택: 행 식별자(시트명-행번호 등). 중복 방지/추적용
  "meat": {
    "traceNum": "140119100857",  // 이력번호
    "sampleNum": "S1",  // 샘플번호
    "gradeNum": "X", // 등급
    "isDeepAging": "No",  // 딥에이징
    "butcheryDate": "2025-08-01",
    "manufactureDate": "2025-07-01",  // 제조(가공)일자
    "picturedDate": "2025-08-19",  // 촬영일자
    "period": "Day7", // 기간
    "expirationDate": "2025-08-26",  // 소비기한
    "marbling": 7,
    "meatColor": 6,
    "texture": 5,
    "surfaceMoisture": 4,
    "total": 6,
    "edgePoint": {
      "TL (430nm)": (1992, 941),
      "TR (430nm)": (2644, 941),
      "BL (430nm)": (2644, 1798),
      "BR (430nm)": (1992, 1798),
      "TL (450nm)": (1992, 941),
      "TR (450nm)": (2644, 941),
      "BL (450nm)": (2644, 1798),
      "BR (450nm)": (1992, 1798),
    },
    "hsi": {
      "wavelengthFromFilename": true,            // 예: *_430nm.jpg, *_450nm.png 등
      "expectedCount": 9  // 기대 파장 수 (= 이미지 수)
    },
    "rgbImageName": ["trace001_rgb.jpg"],
    "hsiImageName": ["trace001_430nm.jpg", "trace001_450nm.jpg"]
  }
}
"""
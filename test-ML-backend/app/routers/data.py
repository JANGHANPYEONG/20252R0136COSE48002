# app/routers/data_upload.py
from __future__ import annotations

import io
import json
import re
import tempfile
import shutil
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from PIL import Image
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.db_model import Meat, SensoryEval, HSIImagesBands
from app.utils import safe_int, safe_float, safe_str, convert_to_datetime
from app.core.config import settings

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
    payload: str = Form(..., description="한 행의 JSON(문자열)"),
    images: Optional[List[UploadFile]] = File(
        None, description="이 행에 해당하는 이미지들(RGB 1 + HSI 여러 장)"
    ),
    overwrite: bool = Form(False, description="동일 키 존재 시 덮어쓰기 여부"),
    db: Session = Depends(get_db),
):
    """
    한 행(JSON) + 여러 이미지 파일을 받아서,
    파일명을 {hash}_{wavelength}.jpg / {hash}_rgb.jpg 로 표준화한 뒤
    S3의 /train_dataset/HSI/ 경로에 업로드 완료 후 DB(Meat / SensoryEval / MeatImage / HSIImagesBands)에 기록합니다.
    """
    # 로깅 추가
    print(f"[DEBUG] Received request:")
    print(f"[DEBUG] payload: {payload}")
    print(f"[DEBUG] images count: {len(images) if images else 0}")
    print(f"[DEBUG] overwrite: {overwrite}")
    if images:
        for i, img in enumerate(images):
            print(f"[DEBUG] image[{i}]: filename={img.filename}, content_type={img.content_type}, size={img.size if hasattr(img, 'size') else 'unknown'}")
    
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
        trace_num = safe_str(meat["traceNum"])
        sample_num = safe_str(meat["sampleNum"])
        rgb_names = {safe_str(n).lower() for n in (meat.get("rgbImageName") or [])}
        hsi_names = {safe_str(n).lower() for n in (meat.get("hsiImageName") or [])}
        hsi_meta = meat.get("hsi") or {}
        expected_count = safe_int(hsi_meta.get("expectedCount"))
        is_refrig_meta = _to_bool(hsi_meta.get("isRefrigerated"))
        edge_points = (meat.get("edgePoint") or {})
        
        print(f"[DEBUG] Extracted data:")
        print(f"[DEBUG]   user_id: {user_id}")
        print(f"[DEBUG]   row_id: {row_id}")
        print(f"[DEBUG]   trace_num: {trace_num}")
        print(f"[DEBUG]   sample_num: {sample_num}")
        print(f"[DEBUG]   rgb_names: {rgb_names}")
        print(f"[DEBUG]   hsi_names: {hsi_names}")
        print(f"[DEBUG]   expected_count: {expected_count}")
        print(f"[DEBUG]   edge_points: {edge_points}")
        
    except KeyError as e:
        print(f"[ERROR] Missing field: {e}")
        raise HTTPException(status_code=400, detail=f"missing field: {e}")

    if not images:
        print(f"[ERROR] No images uploaded")
        raise HTTPException(status_code=400, detail="no images uploaded")

    # 선택: 기대 개수 검증 (정책에 맞게 강제/완화)
    if expected_count is not None and expected_count > 0:
        # RGB 1장(+), HSI expectedCount 장
        expected_total = expected_count + (1 if rgb_names else 0)
        print(f"[DEBUG] Expected total images: {expected_total}, actual: {len(images)}")
        # 강제하고 싶으면 if len(images) != expected_total: raise ...
        # 지금은 경고만
        pass

    # -------------------------------
    # 2) 해시 생성
    # -------------------------------
    uid = make_hash(trace_num, sample_num, length=20)
    print(f"[DEBUG] Generated hash: {uid}")

    # -------------------------------
    # 3) 임시 디렉토리 준비
    # -------------------------------
    tmpdir = tempfile.mkdtemp(prefix="rowu_")
    saved_files: List[tuple[str, str]] = []  # (local_path, new_filename)
    print(f"[DEBUG] Created temp dir: {tmpdir}")

    try:
        # -------------------------------
        # 4) 업로드할 파일 만들기 (리네임/변환)
        # -------------------------------
        for uf in images:
            orig_name = (uf.filename or "").strip()
            if not orig_name:
                print(f"[ERROR] Empty filename for image")
                raise HTTPException(status_code=400, detail="an image has empty filename")

            print(f"[DEBUG] Processing image: {orig_name}")
            raw = await uf.read()
            jpg_bytes = _ensure_jpg(raw)
            print(f"[DEBUG] Converted to JPEG, size: {len(jpg_bytes)} bytes")

            # RGB 판정: 파일명이 rgb 포함 or payload의 rgbImageName에 명시된 경우
            is_rgb = _looks_rgb(orig_name) or (orig_name.lower() in rgb_names)
            if is_rgb:
                new_fname = f"{uid}_rgb.jpg"
                print(f"[DEBUG] Detected as RGB image: {new_fname}")
            else:
                # 파장 추출
                m = WL_PAT.search(orig_name)
                if not m:
                    print(f"[ERROR] Cannot detect wavelength from filename: {orig_name}")
                    raise HTTPException(status_code=400, detail=f"cannot detect wavelength from filename: {orig_name}")
                wl = f"{m.group(1)}nm".lower()
                new_fname = f"{uid}_{wl}.jpg"
                print(f"[DEBUG] Detected as HSI image: {new_fname}")

            out_path = f"{tmpdir}/{new_fname}"
            with open(out_path, "wb") as f:
                f.write(jpg_bytes)
            saved_files.append((out_path, new_fname))
            print(f"[DEBUG] Saved to: {out_path}")

        # -------------------------------
        # 5) S3 업로드 (디렉토리 전체 업로드 → 키는 파일명 기준)
        # -------------------------------
        # 고정된 S3 경로 사용: /train_dataset/HSI/
        s3_path = f"s3://{settings.S3_BUCKET_NAME}/train_dataset/HSI/"
        print(f"[DEBUG] S3 upload path: {s3_path}")
        
        summary = upload_local_to_s3_prefix(
            local_path=tmpdir,
            s3_path=s3_path,
            overwrite=overwrite,
            workers=8,
        )
        print(f"[DEBUG] S3 upload summary: {summary}")

        uploaded = summary.get("uploaded", 0)
        failed = summary.get("failed", 0)
        if failed > 0 or uploaded != len(saved_files):
            print(f"[ERROR] S3 upload failed: uploaded={uploaded}, failed={failed}, expected={len(saved_files)}")
            raise HTTPException(status_code=502, detail={"msg": "s3 upload not complete", "summary": summary})

        # S3 info
        bucket = summary["bucket"]
        prefix = summary.get("prefix", "").rstrip("/")
        print(f"[DEBUG] S3 bucket: {bucket}, prefix: {prefix}")

        # 파일별 S3 key/uri 만들기
        def to_key(name: str) -> str:
            return f"{prefix}/{name}" if prefix else name

        def to_uri(name: str) -> str:
            return f"s3://{bucket}/{to_key(name)}"

        # 대표 이미지(우선 RGB → 없으면 첫 HSI)
        rgb_name = next((n for _, n in saved_files if n.endswith("_rgb.jpg")), None)
        first_hsi_name = next((n for _, n in saved_files if not n.endswith("_rgb.jpg")), None)
        representative_name = rgb_name or first_hsi_name
        representative_uri = to_uri(representative_name) if representative_name else None
        print(f"[DEBUG] Representative image: {representative_name} -> {representative_uri}")

        # 파장 수집(이번 요청 범위에서) → spectral_index 매기기
        wavelengths = []
        for _, fname in saved_files:
            if fname.endswith("_rgb.jpg"):
                continue
            m = re.search(r'_(\d{3,4})nm\.jpg$', fname, re.I)
            if m:
                wavelengths.append(int(m.group(1)))
        wavelengths = sorted(set(wavelengths))
        print(f"[DEBUG] Wavelengths found: {wavelengths}")

        def spectral_index_for_nm(nm: int) -> Optional[int]:
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
        # 6) DB upsert/insert (트랜잭션)
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
                seqno=None,
                isRefrigerated=True if period > 1 else False,
                createdAt=convert_to_datetime(None, 1),
                userId=user_id,
                period=period,
                filmedAt=convert_to_datetime(meat.get("picturedDate"), 2),
                imagePath=None,
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

            # ── MeatImage rows ───────────────────────────────────────
            image_rows: List[MeatImage] = []
            for _, fname in saved_files:
                role = "rgb" if fname.endswith("_rgb.jpg") else "hsi"
                wavelength = None
                if role == "hsi":
                    m2 = re.search(r'_(\d{3,4}nm)\.jpg$', fname, re.I)
                    wavelength = m2.group(1).lower() if m2 else None

                image_rows.append(
                    MeatImage(
                        uid=uid,
                        role=role,
                        wavelength=wavelength,          # '430nm' | None
                        bucket=bucket,
                        s3_key=to_key(fname),           # key
                        filename=fname,                 # 원파일명(리네임된)
                    )
                )
            print(f"[DEBUG] Created {len(image_rows)} MeatImage records")

            # ── HSIImagesBands rows ─────────────────────────────────
            #   RGB는 제외, 각 파장별 좌표와 s3 uri 저장
            bands_rows: List[HSIImagesBands] = []
            for _, fname in saved_files:
                if fname.endswith("_rgb.jpg"):
                    continue

                m2 = re.search(r'_(\d{3,4})nm\.jpg$', fname, re.I)
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
                        seqno=None,                      # 필요하면 의미있는 값으로
                        isRefrigerated=is_refrig,        # boolean NN
                        spectral_index=sp_idx,           # NOT NULL이면 None 방지
                        filename=to_uri(fname),          # ✅ S3 경로(URI)
                        topLeft=tl,
                        topRight=tr,
                        bottomLeft=bl,
                        bottomRight=br,
                    )
                )
            print(f"[DEBUG] Created {len(bands_rows)} HSIImagesBands records")

            db.add_all(image_rows + bands_rows)
            db.commit()
            print(f"[DEBUG] Database commit successful")

        except Exception as e:
            print(f"[ERROR] Database error: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=f"db error: {e}")

        # -------------------------------
        # 7) 정상 응답
        # -------------------------------
        result = {
            "ok": True,
            "hash": uid,
            "userId": user_id,
            "rowId": row_id,
            "traceNum": trace_num,
            "sampleNum": sample_num,
            "saved": [name for _, name in saved_files],
            "s3": s3_path,  # 고정된 S3 경로
            "imagePath": representative_uri,  # ✅ 대표 이미지 경로
            "uploadSummary": summary,
        }
        print(f"[DEBUG] Returning success response: {result}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"processing error: {e}")
    finally:
        # 임시 디렉토리 정리
        shutil.rmtree(tmpdir, ignore_errors=True)
        print(f"[DEBUG] Cleaned up temp dir: {tmpdir}")

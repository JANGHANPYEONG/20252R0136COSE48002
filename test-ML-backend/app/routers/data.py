# app/routers/data_api.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Dict, List, Optional, Tuple
from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.orm import Session
from datetime import datetime
from PIL import Image
import hashlib, string
import pandas as pd
import zipfile, tempfile, os, io, shutil, re
import boto3

from app.db.database import get_db
from app.db.db_model import Meat, CategoryInfo, SpeciesInfo
from app.db.db_controller import find_id
from app.utils import logger, safe_str, safe_int, safe_float, convert_to_datetime, DEFAULT_USER_ID

router = APIRouter()

# 설정
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
BASE62_ALPHABET = string.digits + string.ascii_letters
WAVELENGTH_PAT = re.compile(r'[_\-]([0-9]{3,4})nm(?:$|[^a-zA-Z0-9])', re.IGNORECASE)

# 유틸
def _norm(s: str) -> str:
    """
    정규화: 공백 제거 + 소문자화
    폴더/파일명과 개체명을 케이스 무시로 비교하기 위해 사용
    """
    return str(s).strip().lower()

def _tokens(name_wo_ext: str) -> List[str]:
    """
    # 파일명(확장자 제거)을 '_', '-', ' ', '.'기준으로 토큰화.
    # 예: "O1234_band-0.png" → ["o1234", "band", "0"]
    """
    return [t for t in re.split(r"[_\-\s\.]+", _norm(name_wo_ext)) if t]

def _iter_files(zdir: str) -> List[str]:
    """압축 해제된 디렉토리 밑의 모든 파일 경로 반환"""
    paths = []
    for root, _, files in os.walk(zdir):
        for f in files:
            paths.append(os.path.join(root, f))
    return paths

def base62_encode(num: int) -> str:
    """정수를 Base62 문자열로 변환"""
    if num == 0:
        return BASE62_ALPHABET[0]
    
    base62 = []
    while num > 0:
        num, rem = divmod(num, 62)
        base62.append(BASE62_ALPHABET[rem])
    return ''.join(reversed(base62))

def make_uid(serial_num: int, sample_num: str, length: int = 20) -> str:
    """
    (일련번호 + 샘플번호) -> 해시 -> Base 62 인코딩 -> 길이 제한
    """
    raw = f"{serial_num}-{sample_num}"

    # SHA-256 해시 -> 정수로 변환
    digest = hashlib.sha256(raw.encode()).digest()
    num = int.from_bytes(digest, byteorder='big')

    # Base62 인코딩
    b62 = base62_encode(num)

    # 길이 제한
    return b62[:length]

def guess_wavelength(fname: str) -> Optional[str]:
    """파일명에서 3~4자리 nm 추출: *_540nm.jpg -> '540nm'"""
    m = WAVELENGTH_PAT.search(fname)
    if m:
        return f"{m.group(1)}nm"
    return None

def read_table_from_upload(upload: UploadFile) -> pd.DataFrame:
    raw = upload.filename or ""
    data = upload.file.read()
    # 읽은 뒤 포인터 초기화 방지 위해 UploadFile.read() 대신 .file.read() 사용
    # CSV
    if raw.lower().endswith(".csv"):
        for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
            try:
                return pd.read_csv(io.BytesIO(data), encoding=enc)
            except Exception:
                continue
        raise HTTPException(status_code=400, detail="CSV 디코딩 실패(utf-8/utf-8-sig/cp949/euc-kr 시도)")
    # Excel
    if raw.lower().endswith((".xlsx", ".xls")):
        try:
            return pd.read_excel(io.BytesIO(data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"엑셀 파싱 실패: {e}")
    raise HTTPException(status_code=400, detail="지원하지 않는 테이블 형식입니다. (csv, xlsx, xls)")

def ensure_columns(df: pd.DataFrame, cols: List[str]) -> Dict[str, str]:
    """대소문자/공백 무시하여 원본 컬럼명 매핑"""
    lower_map = {_norm(c): c for c in df.columns}
    out = {}
    for c in cols:
        k = _norm(c)
        if k not in lower_map:
            raise HTTPException(status_code=400, detail=f"필수 컬럼 '{c}'이(가) 없습니다. 실제 컬럼: {list(df.columns)}")
        out[c] = lower_map[k]
    return out

def build_entity_index(df: pd.DataFrame, entity_cols_src: List[str]) -> Dict[Tuple[str, ...], Dict]:
    """엔티티 키(정규화된 튜플) -> 원본행 정보({row_idx, display, serial, sample, uid})"""
    idx = {}
    cols_map = ensure_columns(df, entity_cols_src + ["일련번호", "샘플번호"])
    ecols = [cols_map[c] for c in entity_cols_src]
    c_serial = cols_map["일련번호"]
    c_sample = cols_map["샘플번호"]

    for ridx, row in df.iterrows():
        values = [str(row.get(c, "")).strip() for c in ecols]
        if not all(values):
            continue
        key_norm = tuple(_norm(v) for v in values)
        display = "_".join(values)
        serial_no = str(row.get(c_serial, "")).strip()
        sample_no = str(row.get(c_sample, "")).strip()
        if not serial_no or not sample_no:
            # 해시 ID 생성 불가 → 스킵
            continue
        uid = make_uid(serial_no, sample_no)
        idx[key_norm] = dict(
            row_idx=int(ridx),
            display=display,
            serial_no=serial_no,
            sample_no=sample_no,
            uid=uid
        )
    if not idx:
        raise HTTPException(status_code=422, detail="엔티티/일련번호/샘플번호를 만족하는 유효 행이 없습니다.")
    return idx

def match_image_to_entity(path: str, entity_keys: List[Tuple[str, ...]]) -> Optional[Tuple[str, ...]]:
    """
    파일 경로 토큰화(부모 폴더명 포함) 후,
    '모든 엔티티 값 토큰이 포함'되는 키를 매칭.
    복수 매칭 시 가장 긴(특이) 키를 채택.
    """
    rel = os.path.basename(path)
    name_wo_ext, _ = os.path.splitext(rel)
    tokens = set(_tokens(name_wo_ext))

    # 상위 폴더명 토큰도 포함(엔티티가 폴더로 분리된 경우 대비)
    parent = os.path.dirname(path)
    while parent and parent != os.path.dirname(parent):
        tokens.update(_tokens(os.path.basename(parent)))
        parent = os.path.dirname(parent)

    candidates = []
    for key in entity_keys:
        if all(any(part in tokens for part in _tokens(kv)) for kv in key):
            candidates.append(key)

    if not candidates:
        return None
    # 가장 구체적인(엔티티 길이 길거나 토큰 매칭이 많은) 것을 우선
    candidates.sort(key=lambda k: (-len(k), k))
    return candidates[0]

def open_image_as_jpg(src_path: str) -> Image.Image:
    im = Image.open(src_path)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    elif im.mode == "L":
        im = im.convert("RGB")
    return im

def make_s3_client(
    aws_access_key_id: Optional[str],
    aws_secret_access_key: Optional[str],
    region_name: Optional[str],
):
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=region_name or os.getenv("AWS_DEFAULT_REGION"),
    )

"""
API 정보를 반환하는 API, GET method
"""
@router.get("/")
def get_data_api_info():
    return {
        "description": "Data API for managing and processing data files",
        "endpoints": [
            {"path": "/upload", "method": "POST", "description": "Upload data files (CSV/XLSX and images)"},
            {"path": "/list", "method": "GET", "description": "Get a list of all entities"},
        ]
    }

"""
데이터 업로드 API

Args:
    csv_file: 업로드할 csv, xlsx 파일
    images_zip: 업로드할 이미지 zip 파일
    entity_column: 엔티티 컬럼명, 이 값으로 csv 행과 이미지 파일을 연결
    db: SQLAlchemy 데이터베이스 세션

Returns:
    dict: 업로드, 매핑, db 저장 결과 요약

"""
@router.post("/upload")
async def upload_zip_csv_to_s3(
    csv_file: UploadFile = File(..., description="CSV/XLSX (필수 컬럼: entity들, 일련번호, 샘플번호)"),
    images_zip: UploadFile = File(..., description="이미지 ZIP"),
    entity_column: List[str] = Form(..., description="엔티티 컬럼명(1개 이상)"),
    s3_bucket: Optional[str] = Form(None, description="S3 버킷명(미지정 시 환경변수 S3_BUCKET 사용)"),
    s3_prefix: Optional[str] = Form("uploads", description="S3 키 prefix (기본: uploads)"),
    convert_to_jpg: Optional[bool] = Form(True, description="JPG 변환 여부(기본 True)"),
    overwrite: Optional[bool] = Form(False, description="동일 키 존재 시 덮어쓰기 여부"),
    aws_access_key_id: Optional[str] = Form(None),
    aws_secret_access_key: Optional[str] = Form(None),
    aws_region: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    ZIP(이미지) + CSV/XLSX 업로드 → 엔티티 매칭 → (일련번호, 샘플번호) 해시 → {hash}_{wavelength}.jpg → S3 업로드
    """
    if not entity_column:
        raise HTTPException(status_code=400, detail="entity_column은 최소 1개 이상이어야 합니다.")

    # 1) CSV/XLSX 읽기
    try:
        df = read_table_from_upload(csv_file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"테이블 파싱 실패: {e}")

    # 필수 컬럼 검증
    _ = ensure_columns(df, entity_column + ["일련번호", "샘플번호"])

    # 2) ZIP 해제
    try:
        zbytes = await images_zip.read()
        tmpdir = tempfile.mkdtemp(prefix="zipimg_")
        with zipfile.ZipFile(io.BytesIO(zbytes)) as zf:
            zf.extractall(tmpdir)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="ZIP 파일이 손상되었거나 올바르지 않습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZIP 처리 실패: {e}")

    # 3) 엔티티 인덱스 구성
    entity_idx = build_entity_index(df, entity_column)
    entity_keys = list(entity_idx.keys())

    # 4) csv 메타를 DB에 저장
    try:
        with db.begin():
            for key in entity_keys:
                info = entity_idx[key]
                meat_with_same_uid = (
                    db.query(Meat)
                    .filter(Meat.id == info["uid"])
                    .one_or_none()
                )
                if meat_with_same_uid is None:
                    new_meat = Meat(
                        id=info["uid"]
                    )
                    db.add(new_meat)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 저장 실패: {e}")
                

    # 5) 이미지 스캔 & 매칭
    all_files = _iter_files(tmpdir)
    img_files = [p for p in all_files if os.path.splitext(p)[1].lower() in IMAGE_EXTS]

    if not img_files:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise HTTPException(status_code=422, detail="ZIP에서 이미지 파일을 찾지 못했습니다.")

    # 6) S3 클라이언트 준비
    bucket = s3_bucket or os.getenv("S3_BUCKET")
    if not bucket:
        shutil.rmtree(tmpdir, ignore_errors=True)
        raise HTTPException(status_code=400, detail="S3 버킷이 지정되지 않았습니다. Form(s3_bucket) 또는 환경변수 S3_BUCKET을 설정하세요.")

    s3 = make_s3_client(aws_access_key_id, aws_secret_access_key, aws_region)

    # 날짜 prefix
    date_prefix = datetime.now().strftime("%Y/%m/%d")

    # 업로드 결과 수집
    uploaded = []
    skipped = []
    unmatched = []
    errors = []

    # 키 존재 여부 캐시
    def s3_exists(key: str) -> bool:
        try:
            s3.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            if e.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 404 or e.response.get("Error", {}).get("Code") == "404":
                return False
            return False

    # 7) 파일 처리
    for path in img_files:
        fname = os.path.basename(path)
        key_match = match_image_to_entity(path, entity_keys)
        if not key_match:
            unmatched.append({"file": fname, "reason": "엔티티 매칭 실패"})
            continue

        # CSV행 메타
        info = entity_idx[key_match]
        uid = info["uid"]

        # 파장 추정
        wl = guess_wavelength(fname)
        if not wl:
            # 파장 미표기 파일은 스킵(요건상 nm 필요)
            skipped.append({"file": fname, "uid": uid, "reason": "파일명에서 파장(nm) 미추출"})
            continue

        new_base = f"{uid}_{wl}.jpg"
        s3_key = f"{s3_prefix}/{date_prefix}/{uid}/{new_base}"

        # 이미 존재 & overwrite=False → 스킵
        if not overwrite and s3_exists(s3_key):
            skipped.append({"file": fname, "uid": uid, "wavelength": wl, "reason": "이미 존재(덮어쓰기 비활성)"})
            continue

        # 이미지 열기/변환
        tmp_out = None
        try:
            if convert_to_jpg:
                im = open_image_as_jpg(path)
                tmp_out = os.path.join(tempfile.gettempdir(), f"__up_{uid}_{wl}.jpg")
                im.save(tmp_out, format="JPEG", quality=95)
                upload_path = tmp_out
                content_type = "image/jpeg"
            else:
                upload_path = path
                # ContentType 추정
                ext = os.path.splitext(path)[1].lower()
                content_type = {
                    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                    ".png": "image/png", ".bmp":"image/bmp",
                    ".tif":"image/tiff", ".tiff":"image/tiff",
                    ".webp":"image/webp"
                }.get(ext, "application/octet-stream")

            # 7) S3 업로드
            extra_args = {"ContentType": content_type}
            s3.upload_file(upload_path, bucket, s3_key, ExtraArgs=extra_args)

            uploaded.append({
                "file": fname,
                "uid": uid,
                "wavelength": wl,
                "s3_key": s3_key
            })
        except (BotoCoreError, ClientError) as e:
            errors.append({"file": fname, "uid": uid, "error": f"S3 업로드 실패: {e}"})
        except Exception as e:
            errors.append({"file": fname, "uid": uid, "error": f"처리 실패: {e}"})
        finally:
            if tmp_out and os.path.exists(tmp_out):
                try:
                    os.remove(tmp_out)
                except Exception:
                    pass

    # 정리
    shutil.rmtree(tmpdir, ignore_errors=True)

    return {
        "summary": {
            "total_images_found": len(img_files),
            "uploaded": len(uploaded),
            "skipped": len(skipped),
            "unmatched": len(unmatched),
            "errors": len(errors),
        },
        "uploaded": uploaded,
        "skipped": skipped,
        "unmatched": unmatched,
        "errors": errors,
        "note": "파일명은 *_540nm.jpg 형태처럼 nm 표기가 있어야 매칭됩니다. 동일 키 존재 시 overwrite=false면 스킵됩니다."
    }

# 데이터 조회
# 필터링 기능 (부위, 파일 등록 날짜, 지역)
# def _parse_date_yyyy_mm_dd(s: str) -> datetime:
#     return datetime.strptime(s, "%Y-%m-%d")

# @router.get("/list")
# def list_data(
#     part: Optional[str] = Query(None),
#     date: Optional[str] = Query(None),
#     location: Optional[str] = Query(None),
#     limit: int = Query(50, ge=1, le=500),
#     offset: int = Query(0, ge=0),
#     db: Session = Depends(get_db)
# ):
    
#     # DB 연결 실패 시 Mock 데이터 반환
#     try:
#         # DB 연결 테스트
#         db.execute("SELECT 1").fetchone()
#     except Exception:
#         logger.warning("DB 연결 실패, mockup 데이터를 반환합니다.")
        
#         # Mock 데이터 생성
#         mock_items = [
#             {
#                 "meat_id": "M001-2025-0813-001",
#                 "trace_num": "TR20250813001",
#                 "part": "등심",
#                 "subpart": "윗등심",
#                 "farm_addr": "경기도 용인시 처인구 농장로 123",
#                 "farmer_name": "김농부",
#                 "butchery_date": "2025-08-10T09:00:00",
#                 "created_at": "2025-08-13T10:00:00",
#                 "status": 0,  # 대기중
#                 "image_path": "/images/meat/M001_rgb.jpg"
#             },
#             {
#                 "meat_id": "M002-2025-0813-002", 
#                 "trace_num": "TR20250813002",
#                 "part": "안심",
#                 "subpart": "안심살",
#                 "farm_addr": "전라남도 나주시 목장길 456",
#                 "farmer_name": "이목장",
#                 "butchery_date": "2025-08-11T14:30:00",
#                 "created_at": "2025-08-13T11:15:00",
#                 "status": 2,  # 승인
#                 "image_path": "/images/meat/M002_hsi.jpg"
#             },
#             {
#                 "meat_id": "M003-2025-0813-003",
#                 "trace_num": "TR20250813003", 
#                 "part": "갈비",
#                 "subpart": "본갈비",
#                 "farm_addr": "충청북도 청주시 상당구 한우로 789",
#                 "farmer_name": "박한우",
#                 "butchery_date": "2025-08-12T08:45:00",
#                 "created_at": "2025-08-13T12:30:00",
#                 "status": 1,  # 반려
#                 "image_path": "/images/meat/M003_rgb.jpg"
#             },
#             {
#                 "meat_id": "M004-2025-0813-004",
#                 "trace_num": "TR20250813004",
#                 "part": "채끝",
#                 "subpart": "채끝살", 
#                 "farm_addr": "강원도 횡성군 축산로 321",
#                 "farmer_name": "정축산",
#                 "butchery_date": "2025-08-09T16:20:00",
#                 "created_at": "2025-08-13T13:45:00",
#                 "status": 0,  # 대기중
#                 "image_path": "/images/meat/M004_hsi.jpg"
#             },
#             {
#                 "meat_id": "M005-2025-0813-005",
#                 "trace_num": "TR20250813005",
#                 "part": "삼겹살",
#                 "subpart": "삼겹살",
#                 "farm_addr": "제주특별자치도 제주시 흑돼지로 654",
#                 "farmer_name": "오제주",
#                 "butchery_date": "2025-08-08T11:10:00", 
#                 "created_at": "2025-08-13T14:20:00",
#                 "status": 2,  # 승인
#                 "image_path": "/images/meat/M005_rgb.jpg"
#             }
#         ]
        
#         # 필터링 적용 (Mock 데이터에서)
#         filtered_items = []
#         for item in mock_items:
#             # 부위 필터링
#             if part and item["part"] != part:
#                 continue
#             # 지역 필터링  
#             if location and location not in item["farm_addr"]:
#                 continue
#             # 날짜 필터링
#             if date:
#                 try:
#                     item_date = datetime.fromisoformat(item["created_at"]).date()
#                     filter_date = _parse_date_yyyy_mm_dd(date).date()
#                     if item_date != filter_date:
#                         continue
#                 except:
#                     continue
#             filtered_items.append(item)
        
#         # 페이징 적용
#         total = len(filtered_items)
#         start_idx = offset
#         end_idx = min(offset + limit, total)
#         paginated_items = filtered_items[start_idx:end_idx]
        
#         return {
#             "total": total,
#             "items": paginated_items,
#             "mock_data": True,  # Mock 데이터임을 표시
#             "message": "DB 연결 실패로 인한 Mock 데이터"
#         }

#     try:
#         # DB에서 데이터 조회
#         query = db.query(Meat).join(CategoryInfo, Meat.categoryId == CategoryInfo.id)

#         # 필터링 조건 적용
#         if part:
#             query = query.filter(CategoryInfo.primalValue == part)
#         if location:
#             query = query.filter(Meat.farmAddr.contains(location))
#         if date:
#             d0 = _parse_date_yyyy_mm_dd(date)
#             d1 = d0 + timedelta(days=1)
#             query = query.filter(and_(Meat.createdAt >= d0, Meat.createdAt < d1))
        
#         # 전체 개수 조회
#         total = query.count()
        
#         # 페이징 적용하여 데이터 조회
#         results = query.order_by(Meat.createdAt.desc()).offset(offset).limit(limit).all()
        
#         # 결과 포맷팅
#         items = []
#         for meat in results:
#             category = db.query(CategoryInfo).filter(CategoryInfo.id == meat.categoryId).first()
#             items.append({
#                 "meat_id": meat.id,
#                 "trace_num": meat.traceNum,
#                 "part": category.primalValue if category else "N/A",
#                 "subpart": category.secondaryValue if category else "N/A",
#                 "farm_addr": meat.farmAddr,
#                 "farmer_name": meat.farmerName,
#                 "butchery_date": meat.butcheryYmd.isoformat() if meat.butcheryYmd else None,
#                 "created_at": meat.createdAt.isoformat() if meat.createdAt else None,
#                 "status": meat.statusType,
#                 "image_path": meat.imagePath
#             })
        
#         return {"total": total, "items": items, "mock_data": False}

#     except ValueError:
#         raise HTTPException(status_code=400, detail="date는 YYYY-MM-DD 형식이어야 합니다.")
#     except Exception as e:
#         logger.error(f"Data list error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from typing import Dict, List, Optional, Set, Tuple
import pandas as pd
import zipfile, tempfile, os, io, shutil, re
from datetime import datetime, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.db.db_model import Meat, CategoryInfo, SpeciesInfo
from app.db.db_controller import find_id
from app.utils import logger, safe_str, safe_int, convert_to_datetime, DEFAULT_USER_ID

router = APIRouter(prefix="/data", tags=["Data"])

# 이미지 파일 확장자 정의
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}

# 정규화: 공백 제거 + 소문자화. 폴더/파일명과 개체명을 케이스 무시로 비교하기 위해 사용.
def _norm(s: str) -> str:
    return str(s).strip().lower()

# 파일명(확장자 제거)을 _ - 공백 . 기준으로 토큰화.
# 예: "O1234_band-0.png" → ["o1234", "band", "0"]
def _tokens(name_wo_ext: str) -> List[str]:
    # 파일명에서 토큰 추출: _, -, 공백, . 기준으로 분리
    return [t for t in re.split(r"[_\-\s\.]+", _norm(name_wo_ext)) if t]

def _iter_zip_files(zdir: str) -> List[str]:
    # 압축 해제된 디렉토리 밑의 모든 파일 경로 반환
    paths = []
    for root, _, files in os.walk(zdir):
        for f in files:
            paths.append(os.path.join(root, f))
    return paths

# 데이터 업로드
# input: xlsx(csv 파일),zip파일 (이미지 파일), output: 성공 메시지
# csv 파일 내부의 컬럼 이름과 이미지 파일 이름이 매칭되어야 함

# [수정 필요 사항] rgb 정수 0, hsi 정수 1
@router.post("/upload")
async def upload_data(
    csv_file: UploadFile = File(..., description="CSV/XLSX (serial_no 필수)"),
    images_zip: UploadFile = File(..., description="이미지 ZIP (컬럼명과 파일명 매칭)"),
    entity_column: str = Form(..., description="엔티티 컬럼명"),
    db: Session = Depends(get_db)
):
    # 1) CSV 읽기
    try:
        raw_data = (await csv_file.read()).decode("utf-8")
        name = (csv_file.filename or "").lower()
        if name.endswith(".xlsx") or name.endswith(".csv") or name.endswith(".xls"):
            df = pd.read_csv(io.StringIO(raw_data))
        else:
            try: 
                df = pd.read_excel(io.BytesIO(raw_data.encode()))
            except Exception as e: 
                raise HTTPException(status_code=400, detail=f"Error reading Excel file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"CSV/XLSX 파싱 실패: {str(e)}")

    cols_lower = { _norm(c): c for c in df.columns }
    if _norm(entity_column) not in cols_lower:
        raise HTTPException(status_code=400, 
                            detail=f"엔티티 컬럼 '{entity_column}'이 CSV/XLSX에 없습니다."
                            f"(실제 컬럼들: {list(df.columns)})")
    entity_col = cols_lower[_norm(entity_column)]

    # CSV의 개체 목록 수집 (공백/중복 정리)
    entities: List[str] = []
    for v in df[entity_col].tolist():
        val = str(v).strip()
        if val:
            entities.append(val)
    entity_set: Set[str] = set(entities)
    if not entity_set:
        raise HTTPException(status_code=422, detail="CSV에 유효한 개체 값이 없습니다.")
# 소문자 비교용 세트 (폴더/파일명 매칭은 케이스 무시)
    entity_set_norm: Set[str] = { _norm(e) for e in entity_set }

    # 2) ZIP 압축 해제 → 임시 폴더
    try:
        zbytes = await images_zip.read()
        with zipfile.ZipFile(io.BytesIO(zbytes)) as zf, tempfile.TemporaryDirectory() as tmpdir:
            zf.extractall(tmpdir)

            # 3) 해제된 파일들 순회하며 매핑
            mapping: Dict[str, List[str]] = { e: [] for e in entity_set }
            unmatched_files: List[str] = []
            ambiguous_files: List[Tuple[str, List[str]]] = []  # (파일경로, 후보개체들)

            for fpath in _iter_zip_files(tmpdir):
                _, ext = os.path.splitext(fpath)
                if ext.lower() not in IMAGE_EXTS:
                    continue

                # 우선 폴더 경로에서 개체명 후보 1순위: 최상위 또는 상위 디렉토리명들
                rel = os.path.relpath(fpath, tmpdir)
                parts = [p for p in rel.split(os.sep) if p]  # e.g. ['O1234', 'band', 'img.png']
                parts_norm = [ _norm(p) for p in parts ]

                # 폴더명 중 하나가 entity와 일치하면 채택
                folder_hit: Optional[str] = None
                for p in parts_norm[:-1]:  # 파일명을 제외한 디렉토리 부분
                    if p in entity_set_norm:
                        folder_hit = p
                        break

                matched_entity: Optional[str] = None
                candidate_entities: List[str] = []

                if folder_hit:
                    # 원본 케이스 보전을 위해 실제 엔티티 문자열로 복원
                    for e in entity_set:
                        if _norm(e) == folder_hit:
                            matched_entity = e
                            break
                else:
                    # 2순위: 파일명 토큰에서 매칭
                    base_wo_ext = os.path.splitext(os.path.basename(fpath))[0]
                    toks = set(_tokens(base_wo_ext))
                    # CSV 엔티티 중 소문자 기준으로 토큰에 '정확히' 포함되는 것을 후보로
                    for e in entity_set:
                        if _norm(e) in toks:
                            candidate_entities.append(e)

                    if len(candidate_entities) == 1:
                        matched_entity = candidate_entities[0]
                    elif len(candidate_entities) > 1:
                        ambiguous_files.append((rel, candidate_entities))

                if matched_entity:
                    mapping[matched_entity].append(rel)  # tmpdir 기준 상대경로 기록
                else:
                    if not folder_hit and not candidate_entities:
                        unmatched_files.append(rel)

            # 4) 결과 요약(누락 개체, 파일 매핑 현황)
            entities_without_files = [e for e, files in mapping.items() if len(files) == 0]

            # 성공/실패 기준: “모든 CSV 개체가 최소 1개 파일과 매핑”을 성공으로 정의 (필요 시 완화 가능)
            if entities_without_files or ambiguous_files or unmatched_files:
                return {
                    "message": "매핑 완료(일부 확인 필요)",
                    "summary": {
                        "csv_entities_count": len(entity_set),
                        "mapped_entities_count": len(entity_set) - len(entities_without_files),
                        "total_mapped_files": sum(len(v) for v in mapping.values()),
                        "unmatched_files_count": len(unmatched_files),
                        "ambiguous_files_count": len(ambiguous_files)
                    },
                    "entities_without_files": entities_without_files[:50],  # 과다 방지
                    "unmatched_files": unmatched_files[:50],
                    "ambiguous_files_examples": [
                        {"file": f, "candidates": c[:10]} for f, c in ambiguous_files[:20]
                    ],
                    "mapping_preview": {
                        e: mapping[e][:5] for e in list(mapping.keys())[:10]  # 미리보기만
                    }
                }

            # 전부 깔끔히 매핑된 경우 - DB에 데이터 저장
            try:
                saved_records = []
                for _, row in df.iterrows():
                    # 필수 컬럼 확인
                    entity_value = safe_str(row.get(entity_col))
                    if not entity_value or entity_value not in entity_set:
                        continue
                    
                    # 새로운 Meat 레코드 생성
                    meat_id = str(uuid.uuid4())
                    
                    # CSV에서 필요한 필드 추출 (컬럼이 있는 경우에만)
                    trace_num = safe_str(row.get('traceNum', row.get('trace_num', meat_id)))
                    farm_addr = safe_str(row.get('farmAddr', row.get('farm_addr')))
                    farmer_name = safe_str(row.get('farmerName', row.get('farmer_name')))
                    butchery_ymd = convert_to_datetime(safe_str(row.get('butcheryYmd', row.get('butchery_ymd'))), 2) if row.get('butcheryYmd') or row.get('butchery_ymd') else datetime.now()
                    birth_ymd = convert_to_datetime(safe_str(row.get('birthYmd', row.get('birth_ymd'))), 2) if row.get('birthYmd') or row.get('birth_ymd') else None
                    sex_type = safe_int(row.get('sexType', row.get('sex_type', 0)))  # 기본값: 0(수)
                    grade_num = safe_int(row.get('gradeNum', row.get('grade_num', 0)))  # 기본값: 0(1++)
                    
                    # 카테고리 ID 계산 (기본값 설정)
                    species_value = safe_str(row.get('species', '소'))  # 기본값: 소
                    primal_value = safe_str(row.get('primal', row.get('part', '등심')))  # 기본값: 등심
                    secondary_value = safe_str(row.get('secondary', row.get('subpart', '윗등심')))  # 기본값: 윗등심
                    
                    try:
                        category_id = find_id(species_value, primal_value, secondary_value, db)
                    except Exception:
                        # 카테고리를 찾을 수 없는 경우 기본값 사용 (소-등심-윗등심)
                        category_id = find_id('소', '등심', '윗등심', db)
                    
                    # Meat 객체 생성
                    new_meat = Meat(
                        id=meat_id,
                        userId=DEFAULT_USER_ID,
                        sexType=sex_type,
                        categoryId=category_id,
                        gradeNum=grade_num,
                        statusType=0,  # 기본값: 대기중
                        createdAt=datetime.now(),
                        traceNum=trace_num,
                        farmAddr=farm_addr,
                        farmerName=farmer_name,
                        butcheryYmd=butchery_ymd,
                        birthYmd=birth_ymd,
                        imagePath=None  # 이미지는 별도 처리
                    )
                    
                    db.add(new_meat)
                    saved_records.append({
                        "meat_id": meat_id,
                        "entity": entity_value,
                        "trace_num": trace_num,
                        "category_id": category_id
                    })
                
                # 변경사항 커밋
                db.commit()
                logger.info(f"Successfully saved {len(saved_records)} meat records to database")
                
                return {
                    "message": "성공: 모든 ZIP 이미지가 CSV 개체와 정상 매핑되고 DB에 저장되었습니다.",
                    "summary": {
                        "csv_entities_count": len(entity_set),
                        "mapped_entities_count": len(entity_set),
                        "total_mapped_files": sum(len(v) for v in mapping.values()),
                        "saved_db_records": len(saved_records)
                    },
                    "saved_records": saved_records[:10],  # 처음 10개만 미리보기
                    "mapping_preview": {
                        e: mapping[e][:5] for e in list(mapping.keys())[:10]
                    }
                }
                
            except Exception as db_error:
                db.rollback()
                logger.error(f"Database save error: {db_error}")
                raise HTTPException(status_code=500, detail=f"DB 저장 실패: {str(db_error)}")

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="ZIP 파일이 손상되었거나 올바르지 않습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"업로드 처리 실패: {e}")


# 데이터 조회
# 필터링 기능 (부위, 파일 등록 날짜, 지역)
def _parse_date_yyyy_mm_dd(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d")

@router.get("/list")
def list_data(
    part: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    try:
        # DB에서 데이터 조회
        query = db.query(Meat).join(CategoryInfo, Meat.categoryId == CategoryInfo.id)
        
        # 필터링 조건 적용
        if part:
            query = query.filter(CategoryInfo.primalValue == part)
        if location:
            query = query.filter(Meat.farmAddr.contains(location))
        if date:
            d0 = _parse_date_yyyy_mm_dd(date)
            d1 = d0 + timedelta(days=1)
            query = query.filter(and_(Meat.createdAt >= d0, Meat.createdAt < d1))
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이징 적용하여 데이터 조회
        results = query.order_by(Meat.createdAt.desc()).offset(offset).limit(limit).all()
        
        # 결과 포맷팅
        items = []
        for meat in results:
            category = db.query(CategoryInfo).filter(CategoryInfo.id == meat.categoryId).first()
            items.append({
                "meat_id": meat.id,
                "trace_num": meat.traceNum,
                "part": category.primalValue if category else "N/A",
                "subpart": category.secondaryValue if category else "N/A",
                "farm_addr": meat.farmAddr,
                "farmer_name": meat.farmerName,
                "butchery_date": meat.butcheryYmd.isoformat() if meat.butcheryYmd else None,
                "created_at": meat.createdAt.isoformat() if meat.createdAt else None,
                "status": meat.statusType,
                "image_path": meat.imagePath
            })
        
        return {"total": total, "items": items}

    except ValueError:
        raise HTTPException(status_code=400, detail="date는 YYYY-MM-DD 형식이어야 합니다.")
    except Exception as e:
        logger.error(f"Data list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

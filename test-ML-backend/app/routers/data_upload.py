from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import boto3
from botocore.exceptions import ClientError

from app.db.database import get_db
from app.db.db_model import (
    Meat, DeepAgingInfo, SensoryEval, HSISensoryEval, HSIImagesBands,
    AI_SensoryEval, AI_HSISensoryEval, SpectralInfo
)
from app.core.config import settings
from app.schemas.meat import DataUploadRequest, MeatDataUpload

router = APIRouter(prefix="", tags=["data-upload"])

# =============================================================================
# Pydantic Models (기존 모델들은 schemas/meat.py로 이동)
# =============================================================================

class BandData(BaseModel):
    spectral_index: int
    topLeft: List[int]
    topRight: List[int]
    bottomRight: List[int]
    bottomLeft: List[int]
    filename: str

class PresignedUrlRequest(BaseModel):
    filename: str
    content_type: str

class PresignedUrlResponse(BaseModel):
    upload_url: str
    file_key: str

# 벌크 업로드를 위한 새로운 모델들
class BulkUploadRequest(BaseModel):
    data_list: List[DataUploadRequest] = Field(..., min_items=1, max_items=100, description="업로드할 데이터 리스트 (최대 100개)")

class BulkUploadResponse(BaseModel):
    message: str
    total_count: int
    success_count: int
    failed_count: int
    results: List[dict]

# =============================================================================
# S3 Presigned URL API
# =============================================================================

@router.post("/presigned-url", response_model=PresignedUrlResponse)
async def get_presigned_url(request: PresignedUrlRequest):
    """
    S3 업로드를 위한 presigned URL을 생성합니다.
    
    - filename: 업로드할 파일명
    - content_type: 파일의 MIME 타입 (예: image/jpeg, image/png)
    
    반환값:
    - upload_url: 파일 업로드용 presigned URL (1시간 유효)
    - file_key: S3에 저장될 파일 경로
    """
    try:
        # S3 클라이언트 생성 (설정에서 가져옴)
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION_NAME
        )
        
        bucket_name = settings.S3_BUCKET_NAME
        
        # 파일 키 생성 (timestamp + filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_key = f"meat_images/{timestamp}_{request.filename}"
        
        # Presigned URL 생성
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_key,
                'ContentType': request.content_type
            },
            ExpiresIn=3600  # 1시간 유효
        )
        
        return PresignedUrlResponse(
            upload_url=presigned_url,
            file_key=file_key
        )
        
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"S3 presigned URL 생성 실패: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예상치 못한 오류: {str(e)}"
        )

# =============================================================================
# 데이터 업로드 API
# =============================================================================

@router.post("/ingest/row-upload", status_code=status.HTTP_201_CREATED)
async def ingest_row_upload(request: DataUploadRequest, db: Session = Depends(get_db)):
    """
    육류 데이터를 row 단위로 인제스트합니다.
    
    이 API는 다음과 같은 테이블들에 데이터를 삽입합니다:
    1. Meat - 원육 기본 정보
    2. DeepAgingInfo - 딥에이징 정보
    3. SensoryEval - 관능검사 (원육)
    4. HSISensoryEval - HSI 관능검사
    5. HSIImagesBands - HSI 이미지 밴드 정보
    6. AI 테이블들 - 예측값을 위한 빈 row 생성
    
    요청 데이터:
    - userId: 사용자 ID (이메일)
    - id: 육류 관리번호 (20자리 해시값)
    - traceNum: 이력번호
    - butcheryYmd: 도축일
    - manufactureYmd: 제조일
    - filmedAt: 촬영일
    - expireYmd: 만료일
    - isRefrigerated: 냉장 여부
    - meat: 육류 상세 데이터 (관능검사 점수, HSI 밴드 정보 등)
    """
    try:
        print(f"DEBUG: Starting ingest_row_upload with request: {request}")
        
        # 날짜 문자열을 datetime 객체로 변환
        butchery_date = datetime.strptime(request.butcheryYmd, "%Y-%m-%d")
        manufacture_date = datetime.strptime(request.manufactureYmd, "%Y-%m-%d")
        filmed_date = datetime.strptime(request.filmedAt, "%Y-%m-%d")
        expire_date = datetime.strptime(request.expireYmd, "%Y-%m-%d")
        current_time = datetime.now()
        
        print(f"DEBUG: Parsed dates - butchery: {butchery_date}, manufacture: {manufacture_date}, filmed: {filmed_date}, expire: {expire_date}")
        
        # 1. Meat 테이블에 데이터 삽입
        print(f"DEBUG: Creating Meat object with categoryId: {request.meat.categoryId}, gradeNum: {request.meat.gradeNum}")
        
        meat = Meat(
            id=request.id,
            userId=request.userId,
            categoryId=request.meat.categoryId,
            gradeNum=request.meat.gradeNum,
            statusType=0,  # 기본값: 대기중
            createdAt=current_time,
            traceNum=request.traceNum,
            butcheryYmd=butchery_date
        )
        
        print(f"DEBUG: Meat object created: {meat}")
        db.add(meat)
        db.flush()  # ID 생성
        print(f"DEBUG: Meat added to DB with ID: {meat.id}")
        
        # 2. DeepAgingInfo 테이블에 데이터 삽입
        print(f"DEBUG: Creating DeepAgingInfo object")
        deep_aging = DeepAgingInfo(
            id=request.id,
            seqno=request.meat.seqno,
            isCompleted=0,  # 기본값: 미완료
            date=current_time,
            minute=0  # 기본값: 0분
        )
        db.add(deep_aging)
        db.flush()
        print(f"DEBUG: DeepAgingInfo added to DB")
        
        # 3. SensoryEval 테이블에 데이터 삽입
        print(f"DEBUG: Creating SensoryEval object")
        sensory_eval = SensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time,
            userId=request.userId,
            period=0,  # 기본값: 0일
            filmedAt=filmed_date,
            marbling=request.meat.marbling,
            meat_color=request.meat.meat_color,
            texture=request.meat.texture,
            surface_moisture=request.meat.surface_moisture,
            overall=request.meat.overall,
            manufactureYmd=manufacture_date,
            expireYmd=expire_date
        )
        db.add(sensory_eval)
        db.flush()
        print(f"DEBUG: SensoryEval added to DB")
        
        # 4. HSISensoryEval 테이블에 데이터 삽입
        print(f"DEBUG: Creating HSISensoryEval object")
        hsi_sensory_eval = HSISensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time,
            marbling=request.meat.marbling,
            meat_color=request.meat.meat_color,
            texture=request.meat.texture,
            surface_moisture=request.meat.surface_moisture,
            overall=request.meat.overall
        )
        db.add(hsi_sensory_eval)
        db.flush()
        print(f"DEBUG: HSISensoryEval added to DB")
        
        # 5. HSIImagesBands 테이블에 데이터 삽입
        print(f"DEBUG: Processing {len(request.meat.bands)} bands")
        for i, band in enumerate(request.meat.bands):
            print(f"DEBUG: Processing band {i}: spectral_index={band.spectral_index}, filename={band.filename}")
            
            # spectral_index 유효성 검사
            spectral_info = db.query(SpectralInfo).filter(SpectralInfo.spectral_index == band.spectral_index).first()
            if not spectral_info:
                print(f"WARNING: Spectral index {band.spectral_index} not found in SpectralInfo table")
                # 임시로 기본값 사용
                print(f"DEBUG: Using default spectral info for index {band.spectral_index}")
            
            hsi_band = HSIImagesBands(
                id=request.id,
                seqno=request.meat.seqno,
                isRefrigerated=request.isRefrigerated,
                spectral_index=band.spectral_index,
                topLeft=band.topLeft,  # [x, y] 좌표 배열 그대로 저장
                topRight=band.topRight,
                bottomRight=band.bottomRight,
                bottomLeft=band.bottomLeft,
                filename=band.filename
            )
            db.add(hsi_band)
            print(f"DEBUG: HSIImagesBands {i} added to DB")
        
        # 6. AI 테이블들에 빈 row 생성 (예측값을 위한 placeholder)
        print(f"DEBUG: Creating AI table objects")
        ai_sensory_eval = AI_SensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time
        )
        db.add(ai_sensory_eval)
        
        ai_hsi_sensory_eval = AI_HSISensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time
        )
        db.add(ai_hsi_sensory_eval)
        
        # 모든 데이터 커밋
        print(f"DEBUG: Committing all data to DB")
        db.commit()
        print(f"DEBUG: Data commit successful")
        
        return {
            "message": "데이터 업로드 성공",
            "meat_id": request.id,
            "seqno": request.meat.seqno,
            "uploaded_at": current_time.isoformat()
        }
        
    except ValueError as e:
        print(f"ERROR: ValueError occurred: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"데이터 형식 오류: {str(e)}"
        )
    except Exception as e:
        print(f"ERROR: Unexpected error occurred: {str(e)}")
        print(f"ERROR: Error type: {type(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 인제스트 실패: {str(e)}"
        )

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_meat_data(request: DataUploadRequest, db: Session = Depends(get_db)):
    """
    육류 데이터를 업로드합니다.
    
    이 API는 다음과 같은 테이블들에 데이터를 삽입합니다:
    1. Meat - 원육 기본 정보
    2. DeepAgingInfo - 딥에이징 정보
    3. SensoryEval - 관능검사 (원육)
    4. HSISensoryEval - HSI 관능검사
    5. HSIImagesBands - HSI 이미지 밴드 정보
    6. AI 테이블들 - 예측값을 위한 빈 row 생성
    
    요청 데이터:
    - userId: 사용자 ID (이메일)
    - id: 육류 관리번호 (20자리 해시값)
    - traceNum: 이력번호
    - butcheryYmd: 도축일
    - manufactureYmd: 제조일
    - filmedAt: 촬영일
    - expireYmd: 만료일
    - isRefrigerated: 냉장 여부
    - meat: 육류 상세 데이터 (관능검사 점수, HSI 밴드 정보 등)
    """
    try:
        # 날짜 문자열을 datetime 객체로 변환
        butchery_date = datetime.strptime(request.butcheryYmd, "%Y-%m-%d")
        manufacture_date = datetime.strptime(request.manufactureYmd, "%Y-%m-%d")
        filmed_date = datetime.strptime(request.filmedAt, "%Y-%m-%d")
        expire_date = datetime.strptime(request.expireYmd, "%Y-%m-%d")
        current_time = datetime.now()
        
        # 1. Meat 테이블에 데이터 삽입
        meat = Meat(
            id=request.id,
            userId=request.userId,
            categoryId=request.meat.categoryId,
            gradeNum=request.meat.gradeNum,
            statusType=0,  # 기본값: 대기중
            createdAt=current_time,
            traceNum=request.traceNum,
            butcheryYmd=butchery_date
        )
        db.add(meat)
        db.flush()  # ID 생성
        
        # 2. DeepAgingInfo 테이블에 데이터 삽입
        deep_aging = DeepAgingInfo(
            id=request.id,
            seqno=request.meat.seqno,
            isCompleted=0,  # 기본값: 미완료
            date=current_time,
            minute=0  # 기본값: 0분
        )
        db.add(deep_aging)
        db.flush()
        
        # 3. SensoryEval 테이블에 데이터 삽입
        sensory_eval = SensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time,
            userId=request.userId,
            period=0,  # 기본값: 0일
            filmedAt=filmed_date,
            marbling=request.meat.marbling,
            meat_color=request.meat.meat_color,
            texture=request.meat.texture,
            surface_moisture=request.meat.surface_moisture,
            overall=request.meat.overall,
            manufactureYmd=manufacture_date,
            expireYmd=expire_date
        )
        db.add(sensory_eval)
        db.flush()
        
        # 4. HSISensoryEval 테이블에 데이터 삽입
        hsi_sensory_eval = HSISensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time,
            marbling=request.meat.marbling,
            meat_color=request.meat.meat_color,
            texture=request.meat.texture,
            surface_moisture=request.meat.surface_moisture,
            overall=request.meat.overall
        )
        db.add(hsi_sensory_eval)
        db.flush()
        
        # 5. HSIImagesBands 테이블에 데이터 삽입
        for band in request.meat.bands:
            # spectral_index 유효성 검사
            spectral_info = db.query(SpectralInfo).filter(SpectralInfo.spectral_index == band.spectral_index).first()
            if not spectral_info:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"유효하지 않은 spectral_index: {band.spectral_index}"
                )
            
            hsi_band = HSIImagesBands(
                id=request.id,
                seqno=request.meat.seqno,
                isRefrigerated=request.isRefrigerated,
                spectral_index=band.spectral_index,
                topLeft=band.topLeft,  # [x, y] 좌표 배열 그대로 저장
                topRight=band.topRight,
                bottomRight=band.bottomRight,
                bottomLeft=band.bottomLeft,
                filename=band.filename
            )
            db.add(hsi_band)
        
        # 6. AI 테이블들에 빈 row 생성 (예측값을 위한 placeholder)
        ai_sensory_eval = AI_SensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time
        )
        db.add(ai_sensory_eval)
        
        ai_hsi_sensory_eval = AI_HSISensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.isRefrigerated,
            createdAt=current_time
        )
        db.add(ai_hsi_sensory_eval)
        
        # 모든 데이터 커밋
        db.commit()
        
        return {
            "message": "데이터 업로드 성공",
            "meat_id": request.id,
            "seqno": request.meat.seqno,
            "uploaded_at": current_time.isoformat()
        }
        
    except ValueError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"데이터 형식 오류: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"데이터 업로드 실패: {str(e)}"
        )

@router.post("/bulk-upload", status_code=status.HTTP_201_CREATED)
async def bulk_upload_meat_data(request: BulkUploadRequest, db: Session = Depends(get_db)):
    """
    여러 개의 육류 데이터를 벌크로 업로드합니다.
    
    이 API는 여러 개의 육류 데이터를 한 번에 처리하여 다음과 같은 테이블들에 데이터를 삽입합니다:
    1. Meat - 원육 기본 정보
    2. DeepAgingInfo - 딥에이징 정보
    3. SensoryEval - 관능검사 (원육)
    4. HSISensoryEval - HSI 관능검사
    5. HSIImagesBands - HSI 이미지 밴드 정보
    6. AI 테이블들 - 예측값을 위한 빈 row 생성
    
    요청 데이터:
    - data_list: DataUploadRequest 객체들의 리스트 (최대 100개)
    
    반환값:
    - total_count: 전체 요청 개수
    - success_count: 성공한 개수
    - failed_count: 실패한 개수
    - results: 각 데이터의 처리 결과
    """
    total_count = len(request.data_list)
    success_count = 0
    failed_count = 0
    results = []
    
    print(f"DEBUG: Starting bulk upload with {total_count} items")
    
    for i, data_request in enumerate(request.data_list):
        try:
            print(f"DEBUG: Processing item {i+1}/{total_count}: {data_request.id}")
            
            # 중복 ID 체크
            existing_meat = db.query(Meat).filter(Meat.id == data_request.id).first()
            if existing_meat:
                print(f"WARNING: Meat ID {data_request.id} already exists, skipping...")
                results.append({
                    "index": i,
                    "meat_id": data_request.id,
                    "seqno": data_request.meat.seqno,
                    "status": "skipped",
                    "message": f"중복된 ID: {data_request.id}",
                    "error": "duplicate_key"
                })
                failed_count += 1
                continue
            
            # 날짜 문자열을 datetime 객체로 변환
            butchery_date = datetime.strptime(data_request.butcheryYmd, "%Y-%m-%d")
            manufacture_date = datetime.strptime(data_request.manufactureYmd, "%Y-%m-%d")
            filmed_date = datetime.strptime(data_request.filmedAt, "%Y-%m-%d")
            expire_date = datetime.strptime(data_request.expireYmd, "%Y-%m-%d")
            current_time = datetime.now()
            
            # 1. Meat 테이블에 데이터 삽입
            meat = Meat(
                id=data_request.id,
                userId=data_request.userId,
                categoryId=data_request.meat.categoryId,
                gradeNum=data_request.meat.gradeNum,
                statusType=0,  # 기본값: 대기중
                createdAt=current_time,
                traceNum=data_request.traceNum,
                butcheryYmd=butchery_date
            )
            db.add(meat)
            db.flush()  # ID 생성
            
            # 2. DeepAgingInfo 테이블에 데이터 삽입
            deep_aging = DeepAgingInfo(
                id=data_request.id,
                seqno=data_request.meat.seqno,
                isCompleted=0,  # 기본값: 미완료
                date=current_time,
                minute=0  # 기본값: 0분
            )
            db.add(deep_aging)
            db.flush()
            
            # 3. SensoryEval 테이블에 데이터 삽입
            sensory_eval = SensoryEval(
                id=data_request.id,
                seqno=data_request.meat.seqno,
                isRefrigerated=data_request.isRefrigerated,
                createdAt=current_time,
                userId=data_request.userId,
                period=0,  # 기본값: 0일
                filmedAt=filmed_date,
                marbling=data_request.meat.marbling,
                meat_color=data_request.meat.meat_color,
                texture=data_request.meat.texture,
                surface_moisture=data_request.meat.surface_moisture,
                overall=data_request.meat.overall,
                manufactureYmd=manufacture_date,
                expireYmd=expire_date
            )
            db.add(sensory_eval)
            db.flush()
            
            # 4. HSISensoryEval 테이블에 데이터 삽입
            hsi_sensory_eval = HSISensoryEval(
                id=data_request.id,
                seqno=data_request.meat.seqno,
                isRefrigerated=data_request.isRefrigerated,
                createdAt=current_time,
                marbling=data_request.meat.marbling,
                meat_color=data_request.meat.meat_color,
                texture=data_request.meat.texture,
                surface_moisture=data_request.meat.surface_moisture,
                overall=data_request.meat.overall
            )
            db.add(hsi_sensory_eval)
            db.flush()
            
            # 5. HSIImagesBands 테이블에 데이터 삽입
            for band in data_request.meat.bands:
                # spectral_index 유효성 검사
                spectral_info = db.query(SpectralInfo).filter(SpectralInfo.spectral_index == band.spectral_index).first()
                if not spectral_info:
                    print(f"WARNING: Spectral index {band.spectral_index} not found in SpectralInfo table for item {i+1}")
                    # 임시로 기본값 사용
                
                hsi_band = HSIImagesBands(
                    id=data_request.id,
                    seqno=data_request.meat.seqno,
                    isRefrigerated=data_request.isRefrigerated,
                    spectral_index=band.spectral_index,
                    topLeft=band.topLeft,  # [x, y] 좌표 배열 그대로 저장
                    topRight=band.topRight,
                    bottomRight=band.bottomRight,
                    bottomLeft=band.bottomLeft,
                    filename=band.filename
                )
                db.add(hsi_band)
            
            # 6. AI 테이블들에 빈 row 생성 (예측값을 위한 placeholder)
            ai_sensory_eval = AI_SensoryEval(
                id=data_request.id,
                seqno=data_request.meat.seqno,
                isRefrigerated=data_request.isRefrigerated,
                createdAt=current_time
            )
            db.add(ai_sensory_eval)
            
            ai_hsi_sensory_eval = AI_HSISensoryEval(
                id=data_request.id,
                seqno=data_request.meat.seqno,
                isRefrigerated=data_request.isRefrigerated,
                createdAt=current_time
            )
            db.add(ai_hsi_sensory_eval)
            
            # 성공 결과 기록
            results.append({
                "index": i,
                "meat_id": data_request.id,
                "seqno": data_request.meat.seqno,
                "status": "success",
                "message": "데이터 업로드 성공",
                "uploaded_at": current_time.isoformat()
            })
            success_count += 1
            
            print(f"DEBUG: Item {i+1} processed successfully")
            
        except Exception as e:
            print(f"ERROR: Failed to process item {i+1}: {str(e)}")
            failed_count += 1
            
            # 실패 결과 기록
            results.append({
                "index": i,
                "meat_id": getattr(data_request, 'id', 'unknown'),
                "seqno": getattr(data_request.meat, 'seqno', 'unknown') if hasattr(data_request, 'meat') else 'unknown',
                "status": "failed",
                "message": f"데이터 업로드 실패: {str(e)}",
                "error": str(e)
            })
            
            # 개별 실패는 전체 트랜잭션에 영향을 주지 않도록 계속 진행
            # 세션을 롤백하여 다음 항목 처리를 위한 깨끗한 상태로 만듦
            try:
                db.rollback()
                print(f"DEBUG: Session rolled back for item {i+1}")
            except Exception as rollback_error:
                print(f"WARNING: Failed to rollback session for item {i+1}: {str(rollback_error)}")
    
    try:
        # 모든 성공한 데이터 커밋
        if success_count > 0:
            print(f"DEBUG: Committing {success_count} successful items")
            db.commit()
            print(f"DEBUG: Bulk upload commit successful")
        else:
            print(f"DEBUG: No successful items to commit")
            db.rollback()
        
        return BulkUploadResponse(
            message=f"벌크 업로드 완료: {success_count}개 성공, {failed_count}개 실패",
            total_count=total_count,
            success_count=success_count,
            failed_count=failed_count,
            results=results
        )
        
    except Exception as e:
        print(f"ERROR: Failed to commit bulk upload: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"벌크 업로드 커밋 실패: {str(e)}"
        )

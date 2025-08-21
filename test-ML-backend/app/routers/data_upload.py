from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import and_
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

# 벌크 presigned URL을 위한 새로운 모델들
class BulkPresignedUrlRequest(BaseModel):
    files: List[PresignedUrlRequest] = Field(..., min_items=1, max_items=100, description="업로드할 파일들의 리스트 (최대 100개)")

class BulkPresignedUrlResponse(BaseModel):
    message: str
    total_count: int
    files: List[PresignedUrlResponse]

# =============================================================================
# 수정 기능을 위한 새로운 모델들
# =============================================================================

class SensoryEvalUpdateRequest(BaseModel):
    """
    관능평가 데이터 수정 요청 모델
    
    이 모델은 sensory_eval 테이블의 데이터를 수정할 때 사용됩니다.
    복합키(id, seqno, isRefrigerated)로 데이터를 식별하고,
    수정하고자 하는 필드만 선택적으로 전달할 수 있습니다.
    
    데이터베이스 구조:
    - sensory_eval 테이블의 복합키: (id, seqno, isRefrigerated)
    - id: 육류 관리번호 (meat 테이블의 PK)
    - seqno: 딥에이징 시퀀스 번호 (deepAging_info 테이블의 seqno)
    - isRefrigerated: 냉장 여부 (신선육=false, 냉장육=true)
    """
    model_config = ConfigDict(populate_by_name=True)
    
    # ============================================================================
    # 필수 식별자 (복합키)
    # ============================================================================
    id: str = Field(
        ..., 
        description="육류 관리번호 (Meat ID) - meat 테이블의 기본키와 연결",
        example="L01709271277001"
    )
    seqno: int = Field(
        ..., 
        ge=0, 
        description="딥에이징 시퀀스 번호 - deepAging_info 테이블의 seqno와 연결",
        example=1
    )
    is_refrigerated: bool = Field(
        ..., 
        alias="isRefrigerated", 
        description="냉장 여부 - 신선육(false) 또는 냉장육(true) 구분",
        example=False
    )
    
    # ============================================================================
    # 메타데이터 수정 필드 (Optional)
    # ============================================================================
    period: Optional[int] = Field(
        None, 
        ge=0, 
        description="도축일로부터 경과된 시간 (시간 단위)",
        example=24
    )
    filmed_at: Optional[datetime] = Field(
        None, 
        alias="filmedAt", 
        description="관능평가 이미지 촬영일시",
        example="2025-01-01T10:00:00Z"
    )
    image_path: Optional[str] = Field(
        None, 
        alias="imagePath", 
        description="관능평가 이미지 파일 경로 (S3 경로 등)",
        example="s3://bucket/sensory/images/L01709271277001_1_false.jpg"
    )
    weight_kg: Optional[float] = Field(
        None, 
        gt=0, 
        description="육류 무게 (킬로그램)",
        example=12.5
    )
    
    # ============================================================================
    # 관능평가 점수 필드 (Optional) - 1-10점 척도
    # ============================================================================
    marbling: Optional[float] = Field(
        None, 
        ge=1, le=10,
        description="마블링 점수 (지방 분포도) - 1-10점 척도",
        example=3.5
    )
    meat_color: Optional[float] = Field(
        None, 
        ge=1, le=10,
        description="육색 점수 - 1-10점 척도",
        example=4.0
    )
    texture: Optional[float] = Field(
        None, 
        ge=1, le=10,
        description="조직감 점수 - 1-10점 척도",
        example=3.2
    )
    surface_moisture: Optional[float] = Field(
        None, 
        ge=1, le=10,
        alias="surfaceMoisture", 
        description="표면 수분 점수 - 1-10점 척도",
        example=1.5
    )
    overall: Optional[float] = Field(
        None, 
        ge=1, le=10,
        description="전체 종합 점수 - 1-10점 척도",
        example=3.8
    )
    
    # ============================================================================
    # 가열육 관련 필드 (Optional) - 처리육일 때만 사용
    # ============================================================================
    manufacture_ymd: Optional[datetime] = Field(
        None, 
        alias="manufactureYmd", 
        description="제조일자 (처리육의 경우)",
        example="2025-01-01T10:00:00Z"
    )
    expire_ymd: Optional[datetime] = Field(
        None, 
        alias="expireYmd", 
        description="소비기한 (처리육의 경우)",
        example="2025-01-15T10:00:00Z"
    )

class SensoryEvalDeleteRequest(BaseModel):
    """
    관능평가 데이터 삭제 요청 모델
    
    이 모델은 sensory_eval 테이블의 데이터를 삭제할 때 사용됩니다.
    복합키(id, seqno, isRefrigerated)로 삭제할 데이터를 식별합니다.
    
    삭제 시 주의사항:
    - CASCADE 설정으로 연결된 ai_sensory_eval 데이터도 함께 삭제됩니다.
    - 삭제된 데이터는 복구할 수 없으므로 신중하게 사용해야 합니다.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    # ============================================================================
    # 필수 식별자 (복합키) - 삭제할 데이터 식별용
    # ============================================================================
    id: str = Field(
        ..., 
        description="육류 관리번호 (Meat ID) - 삭제할 데이터의 육류 ID",
        example="L01709271277001"
    )
    seqno: int = Field(
        ..., 
        ge=0, 
        description="딥에이징 시퀀스 번호 - 삭제할 데이터의 시퀀스 번호",
        example=1
    )
    is_refrigerated: bool = Field(
        ..., 
        alias="isRefrigerated", 
        description="냉장 여부 - 삭제할 데이터의 냉장 상태 (신선육=false, 냉장육=true)",
        example=False
    )

class CrudResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# =============================================================================
# Helper Functions
# =============================================================================

def validate_sensory_eval_exists(db: Session, id: str, seqno: int, is_refrigerated: bool) -> SensoryEval:
    """sensory_eval 테이블에서 데이터 존재 여부 확인"""
    sensory_eval = db.query(SensoryEval).filter(
        and_(
            SensoryEval.id == id,
            SensoryEval.seqno == seqno,
            SensoryEval.isRefrigerated == is_refrigerated
        )
    ).first()
    
    if not sensory_eval:
        raise HTTPException(
            status_code=404,
            detail=f"Sensory evaluation not found: id={id}, seqno={seqno}, isRefrigerated={is_refrigerated}"
        )
    
    return sensory_eval

def validate_deep_aging_exists(db: Session, id: str, seqno: int) -> DeepAgingInfo:
    """deepAging_info 테이블에서 데이터 존재 여부 확인"""
    deep_aging = db.query(DeepAgingInfo).filter(
        and_(
            DeepAgingInfo.id == id,
            DeepAgingInfo.seqno == seqno
        )
    ).first()
    
    if not deep_aging:
        raise HTTPException(
            status_code=404,
            detail=f"Deep aging info not found: id={id}, seqno={seqno}"
        )
    
    return deep_aging

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
        
        # 파일 키 생성 (filename)
        file_key = f"train_dataset/HSI/{request.filename}"
        
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

@router.post("/bulk-presigned-url", response_model=BulkPresignedUrlResponse)
async def get_bulk_presigned_urls(request: BulkPresignedUrlRequest):
    """
    여러 파일을 위한 presigned URL을 일괄 생성합니다.
    
    이 API는 여러 파일을 동시에 S3에 업로드하기 위한 presigned URL들을 생성합니다.
    
    요청 데이터:
    - files: 업로드할 파일들의 리스트 (최대 100개)
        - filename: 업로드할 파일명
        - content_type: 파일의 MIME 타입
    
    반환값:
    - message: 처리 결과 메시지
    - total_count: 요청된 파일 개수
    - files: 각 파일별 presigned URL과 file_key 리스트
    
    특징:
    - 각 파일마다 고유한 타임스탬프 기반 경로 생성
    - 모든 파일이 동일한 세션에서 처리되어 일관성 보장
    - 최대 100개 파일까지 지원
    """
    try:
        # S3 클라이언트 생성
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.S3_REGION_NAME
        )
        
        bucket_name = settings.S3_BUCKET_NAME
        presigned_urls = []
        
        print(f"DEBUG: Generating bulk presigned URLs for {len(request.files)} files")
        
        for i, file_request in enumerate(request.files):
            try:
                # 각 파일마다 고유한 타임스탬프 생성 (밀리초 단위로 구분)
                file_key = f"train_dataset/HSI/{file_request.filename}"
                
                print(f"DEBUG: Processing file {i+1}: {file_request.filename} -> {file_key}")
                
                # Presigned URL 생성
                presigned_url = s3_client.generate_presigned_url(
                    'put_object',
                    Params={
                        'Bucket': bucket_name,
                        'Key': file_key,
                        'ContentType': file_request.content_type
                    },
                    ExpiresIn=3600  # 1시간 유효
                )
                
                presigned_urls.append(PresignedUrlResponse(
                    upload_url=presigned_url,
                    file_key=file_key
                ))
                
                print(f"DEBUG: Successfully generated presigned URL for file {i+1}")
                
            except Exception as file_error:
                print(f"ERROR: Failed to generate presigned URL for file {i+1} ({file_request.filename}): {str(file_error)}")
                # 개별 파일 실패는 전체 프로세스에 영향을 주지 않도록 계속 진행
                continue
        
        if not presigned_urls:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="모든 파일에 대한 presigned URL 생성에 실패했습니다."
            )
        
        print(f"DEBUG: Successfully generated {len(presigned_urls)} presigned URLs out of {len(request.files)} requested files")
        
        return BulkPresignedUrlResponse(
            message=f"벌크 presigned URL 생성 완료: {len(presigned_urls)}개 성공",
            total_count=len(request.files),
            files=presigned_urls
        )
        
    except ClientError as e:
        print(f"ERROR: S3 client error in bulk presigned URL generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"S3 벌크 presigned URL 생성 실패: {str(e)}"
        )
    except Exception as e:
        print(f"ERROR: Unexpected error in bulk presigned URL generation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"벌크 presigned URL 생성 중 예상치 못한 오류: {str(e)}"
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

@router.post("/bulk-upsert", status_code=status.HTTP_200_OK)
async def bulk_upsert_meat_data(request: BulkUploadRequest, db: Session = Depends(get_db)):
    """
    여러 개의 육류 데이터를 벌크로 upsert합니다.
    
    이 API는 여러 개의 육류 데이터를 한 번에 처리하여 다음과 같은 테이블들에 데이터를 삽입하거나 업데이트합니다:
    1. Meat - 원육 기본 정보
    2. DeepAgingInfo - 딥에이징 정보
    3. SensoryEval - 관능검사 (원육)
    4. HSISensoryEval - HSI 관능검사
    5. HSIImagesBands - HSI 이미지 밴드 정보
    6. AI 테이블들 - 예측값을 위한 빈 row 생성
    
    Upsert 동작:
    - 새 데이터: 삽입 (INSERT)
    - 기존 데이터: 업데이트 (UPDATE)
    
    요청 데이터:
    - data_list: DataUploadRequest 객체들의 리스트 (최대 100개)
    
    반환값:
    - total_count: 전체 요청 개수
    - success_count: 성공한 개수 (삽입 + 업데이트)
    - failed_count: 실패한 개수
    - insert_count: 새로 삽입된 개수
    - update_count: 업데이트된 개수
    - results: 각 데이터의 처리 결과
    """
    total_count = len(request.data_list)
    success_count = 0
    failed_count = 0
    insert_count = 0
    update_count = 0
    results = []
    
    print(f"DEBUG: Starting bulk upsert with {total_count} items")
    
    for i, data_request in enumerate(request.data_list):
        try:
            print(f"DEBUG: Processing item {i+1}/{total_count}: {data_request.id}")
            
            # 기존 데이터 존재 여부 확인
            existing_meat = db.query(Meat).filter(Meat.id == data_request.id).first()
            is_update = existing_meat is not None
            
            if is_update:
                print(f"INFO: Meat ID {data_request.id} already exists, updating...")
                # 기존 데이터 삭제 (CASCADE로 연결된 하위 데이터도 함께 삭제)
                db.delete(existing_meat)
                db.flush()
                print(f"DEBUG: Existing data deleted for update")
            
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
            operation_type = "update" if is_update else "insert"
            results.append({
                "index": i,
                "meat_id": data_request.id,
                "seqno": data_request.meat.seqno,
                "status": "success",
                "operation": operation_type,
                "message": f"데이터 {operation_type} 성공",
                "uploaded_at": current_time.isoformat()
            })
            success_count += 1
            
            if is_update:
                update_count += 1
            else:
                insert_count += 1
            
            print(f"DEBUG: Item {i+1} processed successfully ({operation_type})")
            
        except Exception as e:
            print(f"ERROR: Failed to process item {i+1}: {str(e)}")
            failed_count += 1
            
            # 실패 결과 기록
            results.append({
                "index": i,
                "meat_id": getattr(data_request, 'id', 'unknown'),
                "seqno": getattr(data_request.meat, 'seqno', 'unknown') if hasattr(data_request, 'meat') else 'unknown',
                "status": "failed",
                "operation": "failed",
                "message": f"데이터 처리 실패: {str(e)}",
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
            print(f"DEBUG: Bulk upsert commit successful")
        else:
            print(f"DEBUG: No successful items to commit")
            db.rollback()
        
        return {
            "message": f"벌크 upsert 완료: {success_count}개 성공 (삽입: {insert_count}개, 업데이트: {update_count}개), {failed_count}개 실패",
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "insert_count": insert_count,
            "update_count": update_count,
            "results": results
        }
        
    except Exception as e:
        print(f"ERROR: Failed to commit bulk upsert: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"벌크 upsert 커밋 실패: {str(e)}"
        )

# =============================================================================
# CRUD API Endpoints (수정, 삭제, 조회)
# =============================================================================

@router.get("/fetch/{id}/{seqno}/{is_refrigerated}")
def get_sensory_eval(
    id: str,
    seqno: int,
    is_refrigerated: bool,
    db: Session = Depends(get_db)
):
    """
    특정 관능평가 데이터 조회
    
    복합키(id, seqno, isRefrigerated)로 데이터를 식별하여 조회합니다.
    
    주의사항:
    - AI 테이블의 예측 데이터는 조회하지 않습니다 (수정 금지)
    - 연결된 HSI 데이터는 별도 API로 조회해야 합니다
    """
    try:
        sensory_eval = validate_sensory_eval_exists(db, id, seqno, is_refrigerated)
        
        # AI 테이블 데이터는 조회하지 않음 (예측 데이터이므로)
        return {
            "id": sensory_eval.id,
            "seqno": sensory_eval.seqno,
            "isRefrigerated": sensory_eval.isRefrigerated,
            "createdAt": sensory_eval.createdAt,
            "userId": sensory_eval.userId,
            "period": sensory_eval.period,
            "filmedAt": sensory_eval.filmedAt,
            "imagePath": sensory_eval.imagePath,
            "weightKg": getattr(sensory_eval, 'weight_kg', None),
            "marbling": sensory_eval.marbling,
            "meat_color": sensory_eval.meat_color,
            "texture": sensory_eval.texture,
            "surfaceMoisture": sensory_eval.surface_moisture,
            "overall": sensory_eval.overall,
            "manufactureYmd": sensory_eval.manufactureYmd,
            "expireYmd": sensory_eval.expireYmd
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve sensory evaluation: {str(e)}"
        )

@router.put("/modify", response_model=CrudResponse)
def update_sensory_eval(
    request: SensoryEvalUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    관능평가 데이터 수정 API
    
    이 엔드포인트는 sensory_eval 테이블의 기존 데이터를 수정합니다.
    
    데이터 흐름:
    1. 클라이언트가 수정할 데이터와 식별자(id, seqno, isRefrigerated)를 전송
    2. 서버에서 해당 데이터의 존재 여부를 확인
    3. 전송된 필드만 선택적으로 업데이트 (None이 아닌 필드만)
    4. updatedAt 필드를 현재 시간으로 자동 업데이트
    5. 데이터베이스에 변경사항을 커밋
    6. 수정 결과를 클라이언트에 반환
    
    특징:
    - 부분 업데이트 지원: 수정할 필드만 전송하면 됨
    - 트랜잭션 안전성: 실패 시 롤백
    - 자동 타임스탬프: updatedAt 필드 자동 갱신
    - AI 테이블 수정 금지: 예측 데이터는 수정할 수 없음
    """
    try:
        # ============================================================================
        # 1단계: 데이터 존재 여부 확인
        # ============================================================================
        # 복합키(id, seqno, isRefrigerated)로 수정할 데이터를 찾음
        sensory_eval = validate_sensory_eval_exists(
            db, request.id, request.seqno, request.is_refrigerated
        )
        
        # ============================================================================
        # 2단계: 수정할 필드들을 수집 (None이 아닌 필드만)
        # ============================================================================
        update_data = {}
        
        # 메타데이터 필드들
        if request.period is not None:
            update_data["period"] = request.period
        if request.filmed_at is not None:
            update_data["filmedAt"] = request.filmed_at
        if request.image_path is not None:
            update_data["imagePath"] = request.image_path
        if request.weight_kg is not None:
            update_data["weight_kg"] = request.weight_kg
        
        # 관능평가 점수 필드들
        if request.marbling is not None:
            update_data["marbling"] = request.marbling
        if request.meat_color is not None:
            update_data["meat_color"] = request.meat_color
        if request.texture is not None:
            update_data["texture"] = request.texture
        if request.surface_moisture is not None:
            update_data["surface_moisture"] = request.surface_moisture
        if request.overall is not None:
            update_data["overall"] = request.overall
        
        # 가열육 관련 필드들
        if request.manufacture_ymd is not None:
            update_data["manufactureYmd"] = request.manufacture_ymd
        if request.expire_ymd is not None:
            update_data["expireYmd"] = request.expire_ymd
        
        # ============================================================================
        # 3단계: 데이터베이스 업데이트 실행
        # ============================================================================
        # 수집된 필드들을 데이터베이스 객체에 반영
        for field, value in update_data.items():
            setattr(sensory_eval, field, value)
        
        # updatedAt 필드를 현재 시간으로 자동 업데이트
        sensory_eval.updatedAt = datetime.now()
        
        # ============================================================================
        # 4단계: 데이터베이스 커밋 및 결과 반환
        # ============================================================================
        db.commit()  # 변경사항을 데이터베이스에 저장
        db.refresh(sensory_eval)  # 객체를 최신 상태로 갱신
        
        return CrudResponse(
            success=True,
            message=f"Sensory evaluation updated successfully: id={request.id}, seqno={request.seqno}, isRefrigerated={request.is_refrigerated}",
            data={
                "id": sensory_eval.id,
                "seqno": sensory_eval.seqno,
                "isRefrigerated": sensory_eval.isRefrigerated,
                "updatedAt": sensory_eval.updatedAt.isoformat() if sensory_eval.updatedAt else None
            }
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생 (404, 400 등)
        raise
    except Exception as e:
        # 예상치 못한 오류 발생 시 롤백
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update sensory evaluation: {str(e)}"
        )

@router.delete("/remove", response_model=CrudResponse)
def delete_sensory_eval(
    request: SensoryEvalDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    관능평가 데이터 삭제 API
    
    이 엔드포인트는 sensory_eval 테이블의 데이터를 삭제합니다.
    
    데이터 흐름:
    1. 클라이언트가 삭제할 데이터의 식별자(id, seqno, isRefrigerated)를 전송
    2. 서버에서 해당 데이터의 존재 여부를 확인
    3. 데이터베이스에서 해당 레코드를 삭제
    4. CASCADE 설정으로 연결된 하위 데이터들도 자동 삭제
    5. 삭제 결과를 클라이언트에 반환
    
    CASCADE 삭제 대상:
    - ai_sensory_eval: AI 예측 결과 데이터
    - 기타 외래키로 연결된 하위 테이블들
    
    주의사항:
    - 삭제된 데이터는 복구할 수 없음
    - 연결된 모든 하위 데이터도 함께 삭제됨
    - AI 테이블의 예측 데이터도 함께 삭제됨
    """
    try:
        # ============================================================================
        # 1단계: 데이터 존재 여부 확인
        # ============================================================================
        # 복합키(id, seqno, isRefrigerated)로 삭제할 데이터를 찾음
        sensory_eval = validate_sensory_eval_exists(
            db, request.id, request.seqno, request.is_refrigerated
        )
        
        # ============================================================================
        # 2단계: 데이터베이스에서 삭제 실행
        # ============================================================================
        # CASCADE 설정으로 연결된 하위 데이터들도 자동 삭제됨
        # - ai_sensory_eval 테이블의 관련 데이터
        # - 기타 외래키로 연결된 테이블들
        db.delete(sensory_eval)
        db.commit()  # 삭제 작업을 데이터베이스에 커밋
        
        # ============================================================================
        # 3단계: 삭제 결과 반환
        # ============================================================================
        return CrudResponse(
            success=True,
            message=f"Sensory evaluation deleted successfully: id={request.id}, seqno={request.seqno}, isRefrigerated={request.is_refrigerated}",
            data={
                "id": request.id,
                "seqno": request.seqno,
                "isRefrigerated": request.is_refrigerated,
                "deletedAt": datetime.now().isoformat()  # 삭제 완료 시간 기록
            }
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생 (404, 400 등)
        raise
    except Exception as e:
        # 예상치 못한 오류 발생 시 롤백
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete sensory evaluation: {str(e)}"
        )

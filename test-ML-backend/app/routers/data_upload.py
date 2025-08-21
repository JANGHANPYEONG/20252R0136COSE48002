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

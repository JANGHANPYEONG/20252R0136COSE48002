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
    - meat: 육류 상세 데이터 (관능검사 점수, HSI 밴드 정보 등)
    - hsiFilenames: HSI 파일명 리스트
    """
    try:
        # 날짜 문자열을 datetime 객체로 변환 (필요한 경우)
        current_time = datetime.now()
        
        # 1. Meat 테이블에 데이터 삽입
        meat = Meat(
            id=request.id,
            userId=request.userId,
            categoryId=request.meat.categoryId if hasattr(request.meat, 'categoryId') else None,
            gradeNum=request.meat.gradeNum if hasattr(request.meat, 'gradeNum') else None,
            statusType=0,  # 기본값: 대기중
            createdAt=current_time,
            traceNum=request.meat.traceNum,
            butcheryYmd=current_time  # 기본값으로 현재 시간 사용
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
            isRefrigerated=request.meat.hsi.isRefrigerated if request.meat.hsi else False,
            createdAt=current_time,
            userId=request.userId,
            period=0,  # 기본값: 0일
            filmedAt=current_time,  # 기본값으로 현재 시간 사용
            marbling=request.meat.marbling,
            meat_color=request.meat.meatColor or request.meat.meat_Color,
            texture=request.meat.texture,
            surface_moisture=request.meat.surfaceMoisture,
            overall=request.meat.total,
            manufactureYmd=current_time,  # 기본값으로 현재 시간 사용
            expireYmd=current_time  # 기본값으로 현재 시간 사용
        )
        db.add(sensory_eval)
        db.flush()
        
        # 4. HSISensoryEval 테이블에 데이터 삽입
        hsi_sensory_eval = HSISensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.meat.hsi.isRefrigerated if request.meat.hsi else False,
            createdAt=current_time,
            marbling=request.meat.marbling,
            meat_color=request.meat.meatColor or request.meat.meat_Color,
            texture=request.meat.texture,
            surface_moisture=request.meat.surfaceMoisture,
            overall=request.meat.total
        )
        db.add(hsi_sensory_eval)
        db.flush()
        
        # 5. HSIImagesBands 테이블에 데이터 삽입 (hsiFilenames 기반)
        for i, filename in enumerate(request.hsiFilenames):
            # spectral_index는 파일 순서대로 할당 (0부터 시작)
            hsi_band = HSIImagesBands(
                id=request.id,
                seqno=request.meat.seqno,
                isRefrigerated=request.meat.hsi.isRefrigerated if request.meat.hsi else False,
                spectral_index=i,
                topLeft=[0, 0],  # 기본값
                topRight=[100, 0],  # 기본값
                bottomRight=[100, 100],  # 기본값
                bottomLeft=[0, 100],  # 기본값
                filename=filename
            )
            db.add(hsi_band)
        
        # 6. AI 테이블들에 빈 row 생성 (예측값을 위한 placeholder)
        ai_sensory_eval = AI_SensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.meat.hsi.isRefrigerated if request.meat.hsi else False,
            createdAt=current_time
        )
        db.add(ai_sensory_eval)
        
        ai_hsi_sensory_eval = AI_HSISensoryEval(
            id=request.id,
            seqno=request.meat.seqno,
            isRefrigerated=request.meat.hsi.isRefrigerated if request.meat.hsi else False,
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

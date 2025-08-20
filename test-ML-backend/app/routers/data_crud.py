from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_, delete

from app.db.database import get_db
from app.db.db_model import SensoryEval, DeepAgingInfo, Meat, HSIImagesBands, HSISensoryEval

router = APIRouter()

# ============================================================================
# Request/Response Models
# ============================================================================

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
        ge=0, 
        description="마블링 점수 (지방 분포도) - 1-10점 척도",
        example=3.5
    )
    color: Optional[float] = Field(
        None, 
        ge=0, 
        description="육색 점수 - 1-10점 척도",
        example=4.0
    )
    texture: Optional[float] = Field(
        None, 
        ge=0, 
        description="조직감 점수 - 1-10점 척도",
        example=3.2
    )
    surface_moisture: Optional[float] = Field(
        None, 
        ge=0, 
        alias="surfaceMoisture", 
        description="표면 수분 점수 - 1-10점 척도",
        example=1.5
    )
    overall: Optional[float] = Field(
        None, 
        ge=0, 
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

class SensoryEvalResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)
    
    id: str
    seqno: int
    is_refrigerated: bool = Field(alias="isRefrigerated")
    created_at: datetime = Field(alias="createdAt")
    user_id: str = Field(alias="userId")
    period: int
    filmed_at: Optional[datetime] = Field(alias="filmedAt")
    image_path: Optional[str] = Field(alias="imagePath")
    weight_kg: Optional[float] = Field(alias="weightKg")
    marbling: Optional[float]
    color: Optional[float]
    texture: Optional[float]
    surface_moisture: Optional[float] = Field(alias="surfaceMoisture")
    overall: Optional[float]
    manufacture_ymd: Optional[datetime] = Field(alias="manufactureYmd")
    expire_ymd: Optional[datetime] = Field(alias="expireYmd")

class CrudResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# ============================================================================
# Helper Functions
# ============================================================================

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

# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/sensory-eval/{id}/{seqno}/{is_refrigerated}", response_model=SensoryEvalResponse)
def get_sensory_eval(
    id: str,
    seqno: int,
    is_refrigerated: bool,
    db: Session = Depends(get_db)
):
    """특정 관능평가 데이터 조회"""
    sensory_eval = validate_sensory_eval_exists(db, id, seqno, is_refrigerated)
    return sensory_eval

@router.put("/sensory-eval", response_model=CrudResponse)
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
        if request.color is not None:
            update_data["color"] = request.color
        if request.texture is not None:
            update_data["texture"] = request.texture
        if request.surface_moisture is not None:
            update_data["surfaceMoisture"] = request.surface_moisture
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
        sensory_eval.updatedAt = datetime.now(timezone.utc)
        
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

@router.delete("/sensory-eval", response_model=CrudResponse)
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
                "deletedAt": datetime.now(timezone.utc).isoformat()  # 삭제 완료 시간 기록
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

# ============================================================================
# 테스트용 엔드포인트 (개발 완료 후 제거 가능. 실제 운영 데이터와 혼동될 수 있음.)
# ============================================================================

@router.get("/test/create-sample")
def create_sample_data(db: Session = Depends(get_db)):
    """테스트용 샘플 데이터 생성"""
    try:
        # 1. meat 테이블에 기본 데이터 확인/생성
        meat_id = "TEST_MEAT_001"
        meat = db.query(Meat).filter(Meat.id == meat_id).first()
        
        if not meat:
            meat = Meat(
                id=meat_id,
                userId="deeplant@example.com",
                sexType=1,
                categoryId=1,
                gradeNum=2,
                statusType=0,
                createdAt=datetime.now(timezone.utc),
                traceNum="TEST_TRACE_001",
                butcheryYmd=datetime.now(timezone.utc)
            )
            db.add(meat)
            db.commit()
            db.refresh(meat)
        
        # 2. deepAging_info 테이블에 데이터 생성
        seqno = 1
        deep_aging = db.query(DeepAgingInfo).filter(
            and_(DeepAgingInfo.id == meat_id, DeepAgingInfo.seqno == seqno)
        ).first()
        
        if not deep_aging:
            deep_aging = DeepAgingInfo(
                id=meat_id,
                seqno=seqno,
                isCompleted=0,
                date=datetime.now(timezone.utc),
                minute=1440  # 24시간
            )
            db.add(deep_aging)
            db.commit()
            db.refresh(deep_aging)
        
        # 3. sensory_eval 테이블에 테스트 데이터 생성
        is_refrigerated = False
        sensory_eval = db.query(SensoryEval).filter(
            and_(
                SensoryEval.id == meat_id,
                SensoryEval.seqno == seqno,
                SensoryEval.isRefrigerated == is_refrigerated
            )
        ).first()
        
        if not sensory_eval:
            sensory_eval = SensoryEval(
                id=meat_id,
                seqno=seqno,
                isRefrigerated=is_refrigerated,
                createdAt=datetime.now(timezone.utc),
                userId="deeplant@example.com",
                period=24,
                filmedAt=datetime.now(timezone.utc),
                weight_kg=12.5,
                marbling=3.5,
                color=4.0,
                texture=3.2,
                surfaceMoisture=1.5,
                overall=3.8
            )
            db.add(sensory_eval)
            db.commit()
            db.refresh(sensory_eval)
        
        return {
            "success": True,
            "message": "Sample data created successfully",
            "data": {
                "meat_id": meat_id,
                "seqno": seqno,
                "isRefrigerated": is_refrigerated,
                "sensory_eval_id": sensory_eval.id
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create sample data: {str(e)}"
        )

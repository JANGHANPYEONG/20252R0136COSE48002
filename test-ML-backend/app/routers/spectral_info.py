from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.database import get_db
from app.db.db_model import SpectralInfo

router = APIRouter()

# ============================================================================
# Request/Response Models
# ============================================================================

class SpectralInfoBase(BaseModel):
    """스펙트럼 정보 기본 모델"""
    model_config = ConfigDict(populate_by_name=True)
    
    spectral_index: int = Field(..., description="스펙트럼 인덱스", example=0)
    wavelength_nm: float = Field(..., description="파장 (나노미터)", example=430.0)

class SpectralInfoCreate(SpectralInfoBase):
    """스펙트럼 정보 생성 모델"""
    pass

class SpectralInfoUpdate(BaseModel):
    """스펙트럼 정보 수정 모델"""
    model_config = ConfigDict(populate_by_name=True)
    
    wavelength_nm: float = Field(..., description="파장 (나노미터)", example=430.0)

class SpectralInfoResponse(SpectralInfoBase):
    """스펙트럼 정보 응답 모델"""
    pass

class SpectralInfoBulkRequest(BaseModel):
    """스펙트럼 정보 일괄 처리 요청 모델"""
    spectrals: List[SpectralInfoBase] = Field(..., description="스펙트럼 정보 리스트")

class SpectralInfoBulkResponse(BaseModel):
    """스펙트럼 정보 일괄 처리 응답 모델"""
    message: str = Field(..., description="처리 결과 메시지")
    created_count: int = Field(..., description="생성된 레코드 수")
    updated_count: int = Field(..., description="수정된 레코드 수")
    failed_count: int = Field(..., description="실패한 레코드 수")
    failed_items: List[dict] = Field(default_factory=list, description="실패한 항목들")

# ============================================================================
# CRUD Operations
# ============================================================================

@router.post("/spectral-info", response_model=SpectralInfoResponse, tags=["Spectral Info"])
async def create_spectral_info(
    spectral_info: SpectralInfoCreate,
    db: Session = Depends(get_db)
):
    """단일 스펙트럼 정보 생성"""
    try:
        # 중복 체크
        existing = db.query(SpectralInfo).filter(
            SpectralInfo.spectral_index == spectral_info.spectral_index
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Spectral index {spectral_info.spectral_index} already exists"
            )
        
        # 새 레코드 생성
        db_spectral = SpectralInfo(
            spectral_index=spectral_info.spectral_index,
            wavelength_nm=spectral_info.wavelength_nm
        )
        
        db.add(db_spectral)
        db.commit()
        db.refresh(db_spectral)
        
        return db_spectral
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create spectral info: {str(e)}")

@router.get("/spectral-info", response_model=List[SpectralInfoResponse], tags=["Spectral Info"])
async def get_all_spectral_info(db: Session = Depends(get_db)):
    """모든 스펙트럼 정보 조회"""
    try:
        spectrals = db.query(SpectralInfo).order_by(SpectralInfo.spectral_index).all()
        return spectrals
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spectral info: {str(e)}")

@router.get("/spectral-info/{spectral_index}", response_model=SpectralInfoResponse, tags=["Spectral Info"])
async def get_spectral_info_by_index(
    spectral_index: int,
    db: Session = Depends(get_db)
):
    """특정 인덱스의 스펙트럼 정보 조회"""
    try:
        spectral = db.query(SpectralInfo).filter(
            SpectralInfo.spectral_index == spectral_index
        ).first()
        
        if not spectral:
            raise HTTPException(
                status_code=404,
                detail=f"Spectral info with index {spectral_index} not found"
            )
        
        return spectral
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch spectral info: {str(e)}")

@router.put("/spectral-info/{spectral_index}", response_model=SpectralInfoResponse, tags=["Spectral Info"])
async def update_spectral_info(
    spectral_index: int,
    spectral_update: SpectralInfoUpdate,
    db: Session = Depends(get_db)
):
    """스펙트럼 정보 수정"""
    try:
        spectral = db.query(SpectralInfo).filter(
            SpectralInfo.spectral_index == spectral_index
        ).first()
        
        if not spectral:
            raise HTTPException(
                status_code=404,
                detail=f"Spectral info with index {spectral_index} not found"
            )
        
        # 파장 값 업데이트
        spectral.wavelength_nm = spectral_update.wavelength_nm
        
        db.commit()
        db.refresh(spectral)
        
        return spectral
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update spectral info: {str(e)}")

@router.delete("/spectral-info/{spectral_index}", tags=["Spectral Info"])
async def delete_spectral_info(
    spectral_index: int,
    db: Session = Depends(get_db)
):
    """스펙트럼 정보 삭제"""
    try:
        spectral = db.query(SpectralInfo).filter(
            SpectralInfo.spectral_index == spectral_index
        ).first()
        
        if not spectral:
            raise HTTPException(
                status_code=404,
                detail=f"Spectral info with index {spectral_index} not found"
            )
        
        # 관련 데이터가 있는지 확인 (HSIImagesBands에서 사용 중인지)
        from app.db.db_model import HSIImagesBands
        related_data = db.query(HSIImagesBands).filter(
            HSIImagesBands.spectral_index == spectral_index
        ).first()
        
        if related_data:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete spectral info {spectral_index}. It is being used by HSI images."
            )
        
        db.delete(spectral)
        db.commit()
        
        return {"message": f"Spectral info with index {spectral_index} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete spectral info: {str(e)}")

@router.post("/spectral-info/bulk", response_model=SpectralInfoBulkResponse, tags=["Spectral Info"])
async def bulk_upsert_spectral_info(
    request: SpectralInfoBulkRequest,
    db: Session = Depends(get_db)
):
    """스펙트럼 정보 일괄 생성/수정"""
    created_count = 0
    updated_count = 0
    failed_count = 0
    failed_items = []
    
    try:
        for spectral_data in request.spectrals:
            try:
                # 기존 데이터 확인
                existing = db.query(SpectralInfo).filter(
                    SpectralInfo.spectral_index == spectral_data.spectral_index
                ).first()
                
                if existing:
                    # 기존 데이터 수정
                    existing.wavelength_nm = spectral_data.wavelength_nm
                    updated_count += 1
                else:
                    # 새 데이터 생성
                    new_spectral = SpectralInfo(
                        spectral_index=spectral_data.spectral_index,
                        wavelength_nm=spectral_data.wavelength_nm
                    )
                    db.add(new_spectral)
                    created_count += 1
                    
            except Exception as e:
                failed_count += 1
                failed_items.append({
                    "spectral_index": spectral_data.spectral_index,
                    "wavelength_nm": spectral_data.wavelength_nm,
                    "error": str(e)
                })
        
        db.commit()
        
        return SpectralInfoBulkResponse(
            message="Bulk operation completed",
            created_count=created_count,
            updated_count=updated_count,
            failed_count=failed_count,
            failed_items=failed_items
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")

@router.delete("/spectral-info/bulk", tags=["Spectral Info"])
async def bulk_delete_spectral_info(
    spectral_indices: List[int],
    db: Session = Depends(get_db)
):
    """스펙트럼 정보 일괄 삭제"""
    try:
        deleted_count = 0
        failed_count = 0
        failed_items = []
        
        for spectral_index in spectral_indices:
            try:
                spectral = db.query(SpectralInfo).filter(
                    SpectralInfo.spectral_index == spectral_index
                ).first()
                
                if not spectral:
                    failed_count += 1
                    failed_items.append({
                        "spectral_index": spectral_index,
                        "error": "Not found"
                    })
                    continue
                
                # 관련 데이터 확인
                from app.db.db_model import HSIImagesBands
                related_data = db.query(HSIImagesBands).filter(
                    HSIImagesBands.spectral_index == spectral_index
                ).first()
                
                if related_data:
                    failed_count += 1
                    failed_items.append({
                        "spectral_index": spectral_index,
                        "error": "Being used by HSI images"
                    })
                    continue
                
                db.delete(spectral)
                deleted_count += 1
                
            except Exception as e:
                failed_count += 1
                failed_items.append({
                    "spectral_index": spectral_index,
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "message": "Bulk delete operation completed",
            "deleted_count": deleted_count,
            "failed_count": failed_count,
            "failed_items": failed_items
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Bulk delete operation failed: {str(e)}")

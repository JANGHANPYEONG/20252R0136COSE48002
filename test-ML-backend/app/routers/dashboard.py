"""
대시보드 조회 API 라우터.

필터링 조건으로 육류/관능평가/HSI 데이터 목록을 조회하고 상세 정보를 반환한다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel

from app.db.database import get_db
from app.db.db_model import (
    Meat, DeepAgingInfo, SensoryEval, AI_SensoryEval, 
    HSISensoryEval, AI_HSISensoryEval, HSIImagesBands
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# =============================================================================
# Request/Response Models
# =============================================================================

class DashboardFilters(BaseModel):
    categoryIds: Optional[List[int]] = None
    butcheryYmd_from: Optional[str] = None
    butcheryYmd_to: Optional[str] = None
    createdAt_from: Optional[str] = None
    createdAt_to: Optional[str] = None
    page: Optional[int] = 1
    pageSize: Optional[int] = 50

class DashboardItem(BaseModel):
    id: Optional[str]
    traceNum: Optional[str]
    categoryId: Optional[int]
    butcheryYmd: Optional[str]
    hasDeepAging: Optional[bool]

class DashboardResponse(BaseModel):
    filters: Optional[DashboardFilters]
    total: Optional[int]
    items: Optional[List[DashboardItem]]

class IndividualMeatRequest(BaseModel):
    id: Optional[str]

class SensoryEvalData(BaseModel):
    id: Optional[str]
    seqno: Optional[int]
    isRefrigerated: Optional[bool]
    createdAt: Optional[str]
    userId: Optional[str]
    period: Optional[int]
    filmedAt: Optional[str]
    imagePath: Optional[str]
    marbling: Optional[float]
    meat_color: Optional[float]
    texture: Optional[float]
    surface_moisture: Optional[float]
    overall: Optional[float]
    manufactureYmd: Optional[str]
    expireYmd: Optional[str]

class AISensoryEvalData(BaseModel):
    id: Optional[str]
    seqno: Optional[int]
    isRefrigerated: Optional[bool]
    createdAt: Optional[str]
    xai_imagePath: Optional[str]
    xai_gradeNum: Optional[int]
    xai_gradeNum_imagePath: Optional[str]
    marbling: Optional[float]
    meat_color: Optional[float]
    texture: Optional[float]
    surface_moisture: Optional[float]
    overall: Optional[float]

class HSISensoryEvalData(BaseModel):
    id: Optional[str]
    seqno: Optional[int]
    isRefrigerated: Optional[bool]
    createdAt: Optional[str]
    xai_imagePath: Optional[str]
    xai_gradeNum: Optional[int]
    xai_gradeNum_imagePath: Optional[str]
    marbling: Optional[float]
    meat_color: Optional[float]
    texture: Optional[float]
    surface_moisture: Optional[float]
    overall: Optional[float]

class AIHSISensoryEvalData(BaseModel):
    id: Optional[str]
    seqno: Optional[int]
    isRefrigerated: Optional[bool]
    createdAt: Optional[str]
    xai_imagePath: Optional[str]
    xai_gradeNum: Optional[int]
    xai_gradeNum_imagePath: Optional[str]
    marbling: Optional[float]
    meat_color: Optional[float]
    texture: Optional[float]
    surface_moisture: Optional[float]
    overall: Optional[float]

class HSIImagesBandsData(BaseModel):
    spectral_index: Optional[int]
    filename: Optional[str]
    topLeft: Optional[List[int]]
    topRight: Optional[List[int]]
    bottomRight: Optional[List[int]]
    bottomLeft: Optional[List[int]]

class SeqnoConditionData(BaseModel):
    seqno: Optional[int]
    isRefrigerated: Optional[bool]
    sensory_eval: Optional[SensoryEvalData]
    ai_sensory_eval: Optional[AISensoryEvalData]
    hsi_sensory_eval: Optional[HSISensoryEvalData]
    ai_hsi_sensory_eval: Optional[AIHSISensoryEvalData]
    hsi_images_bands: Optional[List[HSIImagesBandsData]]

class DeepAgingData(BaseModel):
    seqnos: Optional[List[int]]
    rows: Optional[List[dict]]

class MeatData(BaseModel):
    id: Optional[str]
    userId: Optional[str]
    sexType: Optional[int]
    categoryId: Optional[int]
    gradeNum: Optional[int]
    statusType: Optional[int]
    createdAt: Optional[str]
    traceNum: Optional[str]
    butcheryYmd: Optional[str]
    birthYmd: Optional[str]
    imagePath: Optional[str]

class IndividualMeatResponse(BaseModel):
    id: Optional[str]
    meat: Optional[MeatData]
    deepAging: Optional[DeepAgingData]
    by_seqno_and_condition: Optional[List[SeqnoConditionData]]


# =============================================================================
# Dashboard Bulk Data API
# =============================================================================

@router.post("/bulk", response_model=DashboardResponse)
async def get_dashboard_bulk_data(
    filters: DashboardFilters,
    db: Session = Depends(get_db)
):
    """
    대시보드용 벌크 데이터 조회
    필터 조건에 맞는 고기 데이터를 페이지네이션과 함께 반환
    """
    try:
        # 기본 쿼리 시작
        query = db.query(Meat)
        
        # 필터 적용
        if filters.categoryIds:
            query = query.filter(Meat.categoryId.in_(filters.categoryIds))
        
        if filters.butcheryYmd_from:
            from_date = datetime.strptime(filters.butcheryYmd_from, "%Y-%m-%d")
            query = query.filter(Meat.butcheryYmd >= from_date)
        
        if filters.butcheryYmd_to:
            to_date = datetime.strptime(filters.butcheryYmd_to, "%Y-%m-%d")
            query = query.filter(Meat.butcheryYmd <= to_date)
        
        if filters.createdAt_from:
            from_datetime = datetime.fromisoformat(filters.createdAt_from.replace('Z', '+00:00'))
            query = query.filter(Meat.createdAt >= from_datetime)
        
        if filters.createdAt_to:
            to_datetime = datetime.fromisoformat(filters.createdAt_to.replace('Z', '+00:00'))
            query = query.filter(Meat.createdAt <= to_datetime)
        
        # 전체 개수 조회
        total = query.count()
        
        # 페이지네이션 적용
        offset = (filters.page - 1) * filters.pageSize
        meats = query.offset(offset).limit(filters.pageSize).all()
        
        # DeepAging 존재 여부 확인을 위한 쿼리
        meat_ids = [meat.id for meat in meats]
        deep_aging_exists = db.query(DeepAgingInfo.id).filter(
            DeepAgingInfo.id.in_(meat_ids)
        ).distinct().all()
        deep_aging_ids = {row[0] for row in deep_aging_exists}
        
        # 응답 데이터 구성
        items = []
        for meat in meats:
            items.append(DashboardItem(
                id=meat.id,
                traceNum=meat.traceNum,
                categoryId=meat.categoryId,
                butcheryYmd=meat.butcheryYmd.isoformat() if meat.butcheryYmd else "",
                hasDeepAging=meat.id in deep_aging_ids
            ))
        
        return DashboardResponse(
            filters=filters,
            total=total,
            items=items
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 중 오류 발생: {str(e)}")


# =============================================================================
# Individual Meat Data API
# =============================================================================

@router.post("/individual", response_model=IndividualMeatResponse)
async def get_individual_meat_data(
    request: IndividualMeatRequest,
    db: Session = Depends(get_db)
):
    """
    개별 고기 데이터 조회
    ID로 고기와 관련된 모든 정보를 조회하여 반환
    """
    try:
        # 기본 고기 정보 조회
        meat = db.query(Meat).filter(Meat.id == request.id).first()
        if not meat:
            raise HTTPException(status_code=404, detail="해당 ID의 고기를 찾을 수 없습니다")
        
        # DeepAging 정보 조회
        deep_aging_infos = db.query(DeepAgingInfo).filter(
            DeepAgingInfo.id == request.id
        ).order_by(DeepAgingInfo.seqno).all()
        
        deep_aging_data = DeepAgingData(
            seqnos=[info.seqno for info in deep_aging_infos],
            rows=[
                {
                    "id": info.id,
                    "seqno": info.seqno,
                    "isCompleted": info.isCompleted,
                    "date": info.date.isoformat() if info.date else None,
                    "minute": info.minute
                }
                for info in deep_aging_infos
            ]
        )
        
        # seqno별 상세 데이터 조회
        by_seqno_condition = []
        
        for deep_aging in deep_aging_infos:
            seqno = deep_aging.seqno
            
            # 상온 조건 데이터
            room_data = await _get_seqno_condition_data(
                db, request.id, seqno, False
            )
            if room_data:
                by_seqno_condition.append(room_data)
            
            # 냉장 조건 데이터
            cold_data = await _get_seqno_condition_data(
                db, request.id, seqno, True
            )
            if cold_data:
                by_seqno_condition.append(cold_data)
        
        # 고기 기본 정보 구성
        meat_data = MeatData(
            id=meat.id,
            userId=meat.userId,
            sexType=meat.sexType,
            categoryId=meat.categoryId,
            gradeNum=meat.gradeNum,
            statusType=meat.statusType,
            createdAt=meat.createdAt.isoformat() if meat.createdAt else None,
            traceNum=meat.traceNum,
            butcheryYmd=meat.butcheryYmd.isoformat() if meat.butcheryYmd else None,
            birthYmd=meat.birthYmd.isoformat() if meat.birthYmd else None,
            imagePath=meat.imagePath
        )
        
        return IndividualMeatResponse(
            id=request.id,
            meat=meat_data,
            deepAging=deep_aging_data,
            by_seqno_and_condition=by_seqno_condition
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 중 오류 발생: {str(e)}")


async def _get_seqno_condition_data(
    db: Session, 
    meat_id: str, 
    seqno: int, 
    is_refrigerated: bool
) -> Optional[SeqnoConditionData]:
    """
    특정 seqno와 조건(상온/냉장)에 대한 데이터를 조회
    """
    # SensoryEval 조회
    sensory_eval = db.query(SensoryEval).filter(
        and_(
            SensoryEval.id == meat_id,
            SensoryEval.seqno == seqno,
            SensoryEval.isRefrigerated == is_refrigerated
        )
    ).first()
    
    # AI SensoryEval 조회
    ai_sensory_eval = db.query(AI_SensoryEval).filter(
        and_(
            AI_SensoryEval.id == meat_id,
            AI_SensoryEval.seqno == seqno,
            AI_SensoryEval.isRefrigerated == is_refrigerated
        )
    ).first()
    
    # HSI SensoryEval 조회
    hsi_sensory_eval = db.query(HSISensoryEval).filter(
        and_(
            HSISensoryEval.id == meat_id,
            HSISensoryEval.seqno == seqno,
            HSISensoryEval.isRefrigerated == is_refrigerated
        )
    ).first()
    
    # AI HSI SensoryEval 조회
    ai_hsi_sensory_eval = db.query(AI_HSISensoryEval).filter(
        and_(
            AI_HSISensoryEval.id == meat_id,
            AI_HSISensoryEval.seqno == seqno,
            AI_HSISensoryEval.isRefrigerated == is_refrigerated
        )
    ).first()
    
    # HSI Images Bands 조회
    hsi_images_bands = db.query(HSIImagesBands).filter(
        and_(
            HSIImagesBands.id == meat_id,
            HSIImagesBands.seqno == seqno,
            HSIImagesBands.isRefrigerated == is_refrigerated
        )
    ).all()
    
    # 데이터가 하나라도 있으면 반환
    if any([sensory_eval, ai_sensory_eval, hsi_sensory_eval, ai_hsi_sensory_eval, hsi_images_bands]):
        return SeqnoConditionData(
            seqno=seqno,
            isRefrigerated=is_refrigerated,
            sensory_eval=_convert_sensory_eval(sensory_eval) if sensory_eval else None,
            ai_sensory_eval=_convert_ai_sensory_eval(ai_sensory_eval) if ai_sensory_eval else None,
            hsi_sensory_eval=_convert_hsi_sensory_eval(hsi_sensory_eval) if hsi_sensory_eval else None,
            ai_hsi_sensory_eval=_convert_ai_hsi_sensory_eval(ai_hsi_sensory_eval) if ai_hsi_sensory_eval else None,
            hsi_images_bands=[
                HSIImagesBandsData(
                    spectral_index=band.spectral_index,
                    filename=band.filename,
                    topLeft=band.topLeft,
                    topRight=band.topRight,
                    bottomRight=band.bottomRight,
                    bottomLeft=band.bottomLeft
                )
                for band in hsi_images_bands
            ]
        )
    
    return None


def _convert_sensory_eval(sensory_eval: SensoryEval) -> SensoryEvalData:
    """SensoryEval 모델을 SensoryEvalData로 변환"""
    return SensoryEvalData(
        id=sensory_eval.id,
        seqno=sensory_eval.seqno,
        isRefrigerated=sensory_eval.isRefrigerated,
        createdAt=sensory_eval.createdAt.isoformat() if sensory_eval.createdAt else None,
        userId=sensory_eval.userId,
        period=sensory_eval.period,
        filmedAt=sensory_eval.filmedAt.isoformat() if sensory_eval.filmedAt else None,
        imagePath=sensory_eval.imagePath,
        marbling=sensory_eval.marbling,
        meat_color=sensory_eval.meat_color,
        texture=sensory_eval.texture,
        surface_moisture=sensory_eval.surface_moisture,
        overall=sensory_eval.overall,
        manufactureYmd=sensory_eval.manufactureYmd.isoformat() if sensory_eval.manufactureYmd else None,
        expireYmd=sensory_eval.expireYmd.isoformat() if sensory_eval.expireYmd else None
    )


def _convert_ai_sensory_eval(ai_sensory_eval: AI_SensoryEval) -> AISensoryEvalData:
    """AI_SensoryEval 모델을 AISensoryEvalData로 변환"""
    return AISensoryEvalData(
        id=ai_sensory_eval.id,
        seqno=ai_sensory_eval.seqno,
        isRefrigerated=ai_sensory_eval.isRefrigerated,
        createdAt=ai_sensory_eval.createdAt.isoformat() if ai_sensory_eval.createdAt else None,
        xai_imagePath=ai_sensory_eval.xai_imagePath,
        xai_gradeNum=ai_sensory_eval.xai_gradeNum,
        xai_gradeNum_imagePath=ai_sensory_eval.xai_gradeNum_imagePath,
        marbling=ai_sensory_eval.marbling,
        meat_color=ai_sensory_eval.meat_color,
        texture=ai_sensory_eval.texture,
        surface_moisture=ai_sensory_eval.surface_moisture,
        overall=ai_sensory_eval.overall
    )


def _convert_hsi_sensory_eval(hsi_sensory_eval: HSISensoryEval) -> HSISensoryEvalData:
    """HSISensoryEval 모델을 HSISensoryEvalData로 변환"""
    return HSISensoryEvalData(
        id=hsi_sensory_eval.id,
        seqno=hsi_sensory_eval.seqno,
        isRefrigerated=hsi_sensory_eval.isRefrigerated,
        createdAt=hsi_sensory_eval.createdAt.isoformat() if hsi_sensory_eval.createdAt else None,
        xai_imagePath=hsi_sensory_eval.xai_imagePath,
        xai_gradeNum=hsi_sensory_eval.xai_gradeNum,
        xai_gradeNum_imagePath=hsi_sensory_eval.xai_gradeNum_imagePath,
        marbling=hsi_sensory_eval.marbling,
        meat_color=hsi_sensory_eval.meat_color,
        texture=hsi_sensory_eval.texture,
        surface_moisture=hsi_sensory_eval.surface_moisture,
        overall=hsi_sensory_eval.overall
    )


def _convert_ai_hsi_sensory_eval(ai_hsi_sensory_eval: AI_HSISensoryEval) -> AIHSISensoryEvalData:
    """AI_HSISensoryEval 모델을 AIHSISensoryEvalData로 변환"""
    return AIHSISensoryEvalData(
        id=ai_hsi_sensory_eval.id,
        seqno=ai_hsi_sensory_eval.seqno,
        isRefrigerated=ai_hsi_sensory_eval.isRefrigerated,
        createdAt=ai_hsi_sensory_eval.createdAt.isoformat() if ai_hsi_sensory_eval.createdAt else None,
        xai_imagePath=ai_hsi_sensory_eval.xai_imagePath,
        xai_gradeNum=ai_hsi_sensory_eval.xai_gradeNum,
        xai_gradeNum_imagePath=ai_hsi_sensory_eval.xai_gradeNum_imagePath,
        marbling=ai_hsi_sensory_eval.marbling,
        meat_color=ai_hsi_sensory_eval.meat_color,
        texture=ai_hsi_sensory_eval.texture,
        surface_moisture=ai_hsi_sensory_eval.surface_moisture,
        overall=ai_hsi_sensory_eval.overall
    )

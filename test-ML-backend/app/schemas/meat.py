"""
육류 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class MeatBase(BaseModel):
    """육류 기본 스키마"""
    sexType: Optional[int] = None
    categoryId: int
    gradeNum: Optional[int] = None
    traceNum: str
    farmAddr: Optional[str] = None
    farmerName: Optional[str] = None
    butcheryYmd: datetime
    birthYmd: Optional[datetime] = None
    imagePath: Optional[str] = None

class MeatCreate(MeatBase):
    """육류 생성 스키마"""
    meatId: str

class MeatUpdate(BaseModel):
    """육류 수정 스키마"""
    sexType: Optional[int] = None
    categoryId: Optional[int] = None
    gradeNum: Optional[int] = None
    traceNum: Optional[str] = None
    farmAddr: Optional[str] = None
    farmerName: Optional[str] = None
    butcheryYmd: Optional[datetime] = None
    birthYmd: Optional[datetime] = None
    imagePath: Optional[str] = None

class MeatResponse(MeatBase):
    """육류 응답 스키마"""
    id: str
    userId: str
    statusType: int
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class DeepAgingBase(BaseModel):
    """딥에이징 기본 스키마"""
    date: datetime
    minute: int
    isCompleted: int = 0

class DeepAgingCreate(DeepAgingBase):
    """딥에이징 생성 스키마"""
    meatId: str
    seqno: int

class DeepAgingResponse(DeepAgingBase):
    """딥에이징 응답 스키마"""
    id: str
    seqno: int

    class Config:
        from_attributes = True

class SensoryEvalBase(BaseModel):
    """관능검사 기본 스키마"""
    period: int
    filmedAt: Optional[datetime] = None
    imagePath: Optional[str] = None
    marbling: Optional[float] = None
    color: Optional[float] = None
    texture: Optional[float] = None
    surfaceMoisture: Optional[float] = None
    overall: Optional[float] = None

class SensoryEvalCreate(SensoryEvalBase):
    """관능검사 생성 스키마"""
    meatId: str
    seqno: int

class SensoryEvalResponse(SensoryEvalBase):
    """관능검사 응답 스키마"""
    id: str
    seqno: int
    userId: str
    createdAt: datetime

    class Config:
        from_attributes = True

class MeatQuery(BaseModel):
    """육류 조회 쿼리 스키마"""
    offset: Optional[str] = None
    count: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    specieValue: Optional[str] = None
    farmAddr: Optional[str] = None
    userId: Optional[str] = None
    type: Optional[str] = None
    createdAt: Optional[str] = None
    statusType: Optional[str] = None
    company: Optional[str] = None

class HSIMeta(BaseModel):
    """HSI 메타데이터 스키마"""
    expectedCount: Optional[int] = None
    isRefrigerated: Optional[bool] = None

class MeatDataUpload(BaseModel):
    """육류 데이터 업로드 스키마"""
    traceNum: str
    sampleNum: str
    seqno: Optional[int] = 1
    gradeNum: Optional[str] = None
    butcheryDate: Optional[str] = None
    picturedDate: Optional[str] = None
    manufactureDate: Optional[str] = None
    expirationDate: Optional[str] = None
    period: Optional[str] = None
    marbling: Optional[float] = None
    meatColor: Optional[float] = None
    meat_Color: Optional[float] = None  # 프론트엔드와 일치시키기 위해 추가
    texture: Optional[float] = None
    surfaceMoisture: Optional[float] = None
    total: Optional[float] = None
    hsi: Optional[HSIMeta] = None
    edgePoint: Optional[Dict[str, Any]] = None

class DataUploadRequest(BaseModel):
    """데이터 업로드 요청 스키마"""
    userId: str
    rowId: str
    id: str
    meat: MeatDataUpload
    hsiFilenames: list[str]

"""
육류 관련 Pydantic 스키마
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

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

class BandData(BaseModel):
    """HSI 밴드 데이터 스키마"""
    spectral_index: int
    topLeft: List[int]
    topRight: List[int]
    bottomRight: List[int]
    bottomLeft: List[int]
    filename: str

class MeatDataUpload(BaseModel):
    """육류 데이터 업로드 스키마"""
    categoryId: Optional[int] = None
    gradeNum: Optional[int] = None
    seqno: int
    marbling: float = Field(ge=1, le=10)
    meat_color: float = Field(ge=1, le=10)
    texture: float = Field(ge=1, le=10)
    surface_moisture: float = Field(ge=1, le=10)
    overall: float = Field(ge=1, le=10)
    bands: List[BandData]

class DataUploadRequest(BaseModel):
    """데이터 업로드 요청 스키마"""
    userId: str
    id: str
    traceNum: str
    butcheryYmd: str  # "2025-08-05" 형식
    manufactureYmd: str  # "2025-08-06" 형식
    filmedAt: str  # "2025-08-18" 형식
    expireYmd: str  # "2025-09-19" 형식
    isRefrigerated: bool
    meat: MeatDataUpload

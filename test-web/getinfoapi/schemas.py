# schemas.py
# schema 검증 코드
from pydantic import BaseModel, Field
from typing import Optional

class TraceQuery(BaseModel):
    traceNo: str = Field(..., description="개체/이력/묶음번호")
    optionNo: Optional[int] = Field(None, description="옵션번호")
    corpNo: Optional[int] = Field(None, description="묶음 구성 업소 사업자번호")

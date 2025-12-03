"""
기존 DB에 저장된 AI HSI 예측 결과를 조회하는 라우터.

app.state 리소스를 사용해 세션을 얻고, 복합키로 ai_hsi_sensory_eval 데이터를 반환한다.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# DB 관련 imports
from app.db.db_model import AI_HSISensoryEval

router = APIRouter()

# --------------------------------------------------------------------------
# 내부 유틸: app.state 에서 공용 리소스 꺼내기
# --------------------------------------------------------------------------
def _require_state_attr(request: Request, name: str):
    """
    FastAPI의 app.state 에 등록된 리소스를 가져옴.
    미등록 시 500 에러로 안내.
    """
    if not hasattr(request.app.state, name):
        raise HTTPException(
            status_code=500,
            detail=f"Server is not configured: missing app.state.{name}",
        )
    return getattr(request.app.state, name)


class HSIPredictRequest(BaseModel):
    id: str
    seqno: str

class HSIPredictData(BaseModel):
    isRefrigerated: bool
    marbling: Optional[float] = None
    color: Optional[float] = None
    texture: Optional[float] = None
    surfaceMoisture: Optional[float] = None
    overall: Optional[float] = None
    createdAt: Optional[datetime] = None
    xaiImagePath: Optional[str] = None

class HSIPredictResponse(BaseModel):
    message: str
    prediction: List[HSIPredictData]  # 단일 개체의 예측 데이터 리스트



@router.post("/prediction", response_model=HSIPredictResponse)
async def get_hsi_prediction(request: Request, hsi_request: HSIPredictRequest):
    """
    AI HSI 예측 결과를 조회하는 엔드포인트 (단일 개체)
    복합키 (id, seqno, isRefrigerated)를 사용하여 ai_hsi_sensory_eval 테이블에서 데이터 조회
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        print(f"HSI prediction request received for id={hsi_request.id}, seqno={hsi_request.seqno}")

        # 입력 검증
        if not hsi_request.id or not str(hsi_request.id).strip():
            return HSIPredictResponse(message="failed", prediction=[])
        if not hsi_request.seqno or not str(hsi_request.seqno).strip():
            return HSIPredictResponse(message="failed", prediction=[])

        # 단일 개체에 대한 쿼리 수행
        hsi_predictions = db_session.query(AI_HSISensoryEval).filter(
            AI_HSISensoryEval.id == str(hsi_request.id),
            AI_HSISensoryEval.seqno == hsi_request.seqno
        ).all()

        predictions = []
        for prediction in hsi_predictions:
            prediction_data = HSIPredictData(
                isRefrigerated=prediction.isRefrigerated,
                marbling=prediction.marbling,
                color=prediction.meat_color,
                texture=prediction.texture,
                surfaceMoisture=prediction.surface_moisture,
                overall=prediction.overall,
                createdAt=prediction.createdAt,
                xaiImagePath=prediction.xai_imagePath
            )
            predictions.append(prediction_data)

        if predictions:
            return HSIPredictResponse(message="success", prediction=predictions)
        else:
            return HSIPredictResponse(message="failed", prediction=[])

    except Exception as e:
        print(f"Unexpected error in get_hsi_prediction endpoint: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return HSIPredictResponse(message="failed", prediction=[])

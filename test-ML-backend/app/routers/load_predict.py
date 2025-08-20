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

class HSIPredictResponse(BaseModel):
    id: str
    seqno: int
    isRefrigerated: bool
    marbling: Optional[float] = None
    color: Optional[float] = None
    texture: Optional[float] = None
    surfaceMoisture: Optional[float] = None
    overall: Optional[float] = None
    createdAt: Optional[datetime] = None


@router.post("/hsi-prediction", response_model=List[HSIPredictResponse])
async def get_hsi_prediction(request: Request, hsi_request: HSIPredictRequest):
    """
    AI HSI 예측 결과를 조회하는 엔드포인트
    복합키 (id, seqno, isRefrigerated)를 사용하여 ai_hsi_sensory_eval 테이블에서 데이터 조회
    """
    try:
        # FastAPI의 app.state에서 DB 세션 가져오기
        db_session = _require_state_attr(request, "db_session")
        
        print(f"HSI prediction request received: id={hsi_request.id}, seqno={hsi_request.seqno}")
        
        # 입력 검증
        if not hsi_request.id or not str(hsi_request.id).strip():
            raise HTTPException(status_code=400, detail="id cannot be empty")
        
        if not hsi_request.seqno or not str(hsi_request.seqno).strip():
            raise HTTPException(status_code=400, detail="seqno cannot be empty")
        
        # 쿼리 구성 - id와 seqno로 조회하여 모든 isRefrigerated 값의 결과를 가져옴
        hsi_predictions = db_session.query(AI_HSISensoryEval).filter(
            AI_HSISensoryEval.id == str(hsi_request.id),
            AI_HSISensoryEval.seqno == int(hsi_request.seqno)
        ).all()
        
        if not hsi_predictions:
            raise HTTPException(
                status_code=404, 
                detail=f"No HSI prediction data found for id={hsi_request.id}, seqno={hsi_request.seqno}"
            )
        
        # 결과를 리스트로 변환
        response_list = []
        for prediction in hsi_predictions:
            response_data = HSIPredictResponse(
                id=prediction.id,
                seqno=prediction.seqno,
                isRefrigerated=prediction.isRefrigerated,
                marbling=prediction.Marbling,
                color=prediction.Meat_Color,
                texture=prediction.Texture,
                surfaceMoisture=prediction.Surface_Moisture,
                overall=prediction.Total,
                createdAt=prediction.createdAt
            )
            response_list.append(response_data)
        
        print(f"Found {len(response_list)} HSI prediction records")
        return response_list
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        print(f"Unexpected error in get_hsi_prediction endpoint: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"HSI prediction query failed: {str(e)}")

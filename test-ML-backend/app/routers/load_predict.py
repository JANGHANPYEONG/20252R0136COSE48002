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


class HSIPredictItem(BaseModel):
    id: str  
    seqno: str  

class HSIPredictRequest(BaseModel):
    items: List[HSIPredictItem]  # 여러 개체 조회를 위한 리스트  

class HSIPredictData(BaseModel):
    isRefrigerated: bool
    marbling: Optional[float] = None
    color: Optional[float] = None
    texture: Optional[float] = None
    surfaceMoisture: Optional[float] = None
    overall: Optional[float] = None
    createdAt: Optional[datetime] = None

class HSIPredictGroup(BaseModel):
    id: str
    seqno: int
    predictions: List[HSIPredictData]  # 해당 개체의 예측 데이터들 (냉장/비냉장)

class HSIPredictResponse(BaseModel):
    message: str
    prediction: List[HSIPredictGroup]  # 개체별로 그룹화된 예측 데이터


@router.post("/prediction", response_model=HSIPredictResponse)
async def get_hsi_prediction(request: Request, hsi_request: HSIPredictRequest):
    """
    AI HSI 예측 결과를 조회하는 엔드포인트 (여러 개체 지원)
    복합키 (id, seqno, isRefrigerated)를 사용하여 ai_hsi_sensory_eval 테이블에서 데이터 조회
    """
    try:
        # FastAPI의 app.state에서 DB 세션 가져오기
        db_session = _require_state_attr(request, "db_session")
        
        print(f"HSI prediction request received for {len(hsi_request.items)} items")
        
        # 입력 검증
        if not hsi_request.items:
            return HSIPredictResponse(
                message="failed",
                prediction=[]
            )
        
        grouped_predictions = []
        
        # 각 아이템에 대해 조회 수행
        for item in hsi_request.items:
            print(f"Processing item: id={item.id}, seqno={item.seqno}")
            
            # 개별 아이템 입력 검증
            if not item.id or not str(item.id).strip():
                print(f"Skipping item with empty id: {item}")
                continue
                
            if not item.seqno or not str(item.seqno).strip():
                print(f"Skipping item with empty seqno: {item}")
                continue
            
            # 개별 아이템에 대한 쿼리 수행
            try:
                hsi_predictions = db_session.query(AI_HSISensoryEval).filter(
                    AI_HSISensoryEval.id == str(item.id),
                    AI_HSISensoryEval.seqno == item.seqno
                ).all()
                
                # 해당 개체의 예측 데이터들을 리스트로 구성
                item_predictions = []
                for prediction in hsi_predictions:
                    prediction_data = HSIPredictData(
                        isRefrigerated=prediction.isRefrigerated,
                        marbling=prediction.Marbling,
                        color=prediction.Meat_Color,
                        texture=prediction.Texture,
                        surfaceMoisture=prediction.Surface_Moisture,
                        overall=prediction.Total,
                        createdAt=prediction.createdAt
                    )
                    item_predictions.append(prediction_data)
                
                # 예측 데이터가 있는 경우에만 그룹에 추가
                if item_predictions:
                    group = HSIPredictGroup(
                        id=str(item.id),
                        seqno=int(item.seqno),
                        predictions=item_predictions
                    )
                    grouped_predictions.append(group)
                    
            except Exception as item_error:
                print(f"Error processing item {item.id}, {item.seqno}: {item_error}")
                continue
        
        print(f"Found {len(grouped_predictions)} groups with prediction data")
        
        # 결과가 있으면 성공, 없으면 실패로 응답
        if grouped_predictions:
            return HSIPredictResponse(
                message="success",
                prediction=grouped_predictions
            )
        else:
            return HSIPredictResponse(
                message="failed",
                prediction=[]
            )
        
    except Exception as e:
        print(f"Unexpected error in get_hsi_prediction endpoint: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return HSIPredictResponse(
            message="failed",
            prediction=[]
        )

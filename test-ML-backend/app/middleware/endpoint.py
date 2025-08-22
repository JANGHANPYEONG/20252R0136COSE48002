# api.py
from typing import List, Optional, Dict, Any
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, constr
from starlette.middleware.cors import CORSMiddleware

from settings import DB_URL, CONCURRENCY
from repo import DataRepository
from model_runner import ModelRunner

# ====== 스키마 ======
TraceNo = constr(strip_whitespace=True, min_length=8, max_length=32)

class PredictItem(BaseModel):
    traceNo: TraceNo

class PredictBatchReq(BaseModel):
    items: List[PredictItem] = Field(..., min_items=1)
    options: Optional[Dict[str, Any]] = None  # ex) {"returnProba":true, "model":"vit_xgb_v2"}

class PredictResult(BaseModel):
    traceNo: str
    prediction: Dict[str, Any]
    meta: Optional[Dict[str, Any]] = None

class PredictBatchResp(BaseModel):
    results: List[PredictResult]
    errors: List[Dict[str, Any]]

# ====== 앱/DI ======
app = FastAPI(title="Deeplant Predict API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # 배포시 도메인 제한
    allow_headers=["*"],
    allow_methods=["*"],
)

repo = DataRepository(DB_URL)
runner = ModelRunner()
sem = asyncio.Semaphore(CONCURRENCY)

@app.get("/health")
def health():
    return {"status": "ok"}

# ====== 배치 예측 엔드포인트 ======
@app.post("/predict/batch", response_model=PredictBatchResp)
async def predict_batch(req: PredictBatchReq):
    results: List[PredictResult] = []
    errors: List[Dict[str, Any]] = []

    async def handle_one(trace_no: str):
        async with sem:
            try:
                rec = repo.get_by_trace(trace_no)
                if not rec:
                    raise HTTPException(status_code=404, detail=f"traceNo 미존재: {trace_no}")
                pred = runner.predict_record(rec)
                results.append(PredictResult(
                    traceNo=trace_no,
                    prediction=pred,
                    meta=rec.get("meta")
                ))
            except HTTPException as e:
                errors.append({"traceNo": trace_no, "error": e.detail})
            except Exception as e:
                errors.append({"traceNo": trace_no, "error": str(e)})

    tasks = [handle_one(it.traceNo) for it in req.items]
    await asyncio.gather(*tasks)

    return PredictBatchResp(results=results, errors=errors)

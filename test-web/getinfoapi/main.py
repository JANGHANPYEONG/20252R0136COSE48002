# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from clients import fetch_trace_info

class TraceQuery(BaseModel):
    traceNo: str
    optionNo: Optional[int] = None
    corpNo: Optional[int] = None

app = FastAPI(title="Livestock Trace Proxy")

@app.get("/trace-info")
async def trace_info(q: TraceQuery = Depends()):  # ✅ GET 쿼리스트링 -> 모델로 바인딩
    try:
        resp = await fetch_trace_info(q.model_dump())
        return resp.json() if "application/json" in resp.headers.get("Content-Type","").lower() else {"raw": resp.text}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

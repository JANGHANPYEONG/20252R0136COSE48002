# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from clients import fetch_trace_info
import xmltodict  # pip install xmltodict

class TraceQuery(BaseModel):
    traceNo: str
    optionNo: Optional[int] = None
    corpNo: Optional[int] = None

app = FastAPI(title="Livestock Trace Proxy")

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/trace-info")
async def trace_info(q: TraceQuery = Depends()):  # GET 쿼리스트링 -> 모델 바인딩 (유지)
    try:
        resp = await fetch_trace_info(q.model_dump())
        ctype = (resp.headers.get("Content-Type") or "").lower()
        text = resp.text.strip()

        # 1) JSON이면 그대로 반환
        if "application/json" in ctype or text.startswith("{"):
            return resp.json()

        # 2) XML이면 파싱해서 JSON으로 변환
        try:
            data = xmltodict.parse(text)
            return data
        except Exception:
            # 3) 그 외(HTML 등)면 원문과 헤더를 같이 리턴해 디버깅 가능하게
            return {
                "content_type": ctype,
                "status_code": resp.status_code,
                "raw": text[:2000]  # 너무 길면 앞부분만
            }

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")

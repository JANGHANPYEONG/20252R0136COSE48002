# clients.py
# 외부 API호출 클라이언트

import os
import httpx
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())  # 여기서 .env 로드

OPENAPI_URL = os.getenv("LIVESTOCK_OPENAPI_URL")
SERVICE_KEY = os.getenv("LIVESTOCK_SERVICE_KEY")

if not OPENAPI_URL or not SERVICE_KEY:
    raise RuntimeError("환경변수 누락: LIVESTOCK_OPENAPI_URL / LIVESTOCK_SERVICE_KEY")

async def fetch_trace_info(params: dict) -> httpx.Response:
    query = {"serviceKey": SERVICE_KEY, **{k: v for k, v in params.items() if v is not None}}
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, read=30.0)) as client:
        r = await client.get(OPENAPI_URL, params=query)
        r.raise_for_status()
        return r

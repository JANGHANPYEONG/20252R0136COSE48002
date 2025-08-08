# clients.py
# 외부 API호출 클라이언트
import os
import httpx

OPENAPI_URL = os.environ["LIVESTOCK_OPENAPI_URL"]
SERVICE_KEY = os.environ["LIVESTOCK_SERVICE_KEY"]

async def fetch_trace_info(params: dict) -> httpx.Response:
    # data.go.kr 샘플 규격: GET + querystring + serviceKey
    query = {
        "serviceKey": SERVICE_KEY,
        **{k: v for k, v in params.items() if v is not None}
    }
    timeout = httpx.Timeout(10.0, read=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(OPENAPI_URL, params=query)
        resp.raise_for_status()
        return resp

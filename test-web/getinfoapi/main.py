# main.py
# FastAPI endpoint(proxy)
from fastapi import FastAPI, Query, HTTPException
from clients import fetch_trace_info
from schemas import TraceQuery

import json
import xmltodict  # XML만 내려오는 경우를 대비 (필요시 설치: pip install xmltodict)

app = FastAPI(title="Livestock Trace Proxy")

@app.get("/trace-info", summary="축산물이력정보조회 프록시")
async def trace_info(
    traceNo: str = Query(..., description="개체번호"),
    optionNo: int | None = Query(None, description='옵션번호'),
    corpNo: int | None = Query(None, description="묶음 구성 업소 사업")
):
    try:
        params = {"traceNo": traceNo, "optionNo": optionNo, "corpNo": corpNo}
        resp = await fetch_trace_info(params)
        return resp.json() if "application/json" in resp.headers.get("Content-Type","").lower().else{"raw": resp.text}
        # JSON 우선 처리
        if "application/json" in ctype or resp.text.strip().startswith("{"):
            data = resp.json()
        else:
            # XML 가능성 처리
            try:
                data = xmltodict.parse(resp.text)
            except Exception:
                # 마지막 fallback: 원문 반환
                data = {"raw": resp.text}

        # 공공데이터포털 표준 응답 코드 처리 (명세 기준)
        # resultCode / resultMsg / successYn 등이 바디 안에 존재하는 경우가 많음
        # 구조가 다를 수 있어 안전하게 키 존재 확인
        result_code = None
        result_msg = None
        success_yn = None

        # 딕셔너리 어디에 들어올지 몰라서 전역 탐색 헬퍼
        def dig(d, key):
            if isinstance(d, dict):
                if key in d: return d[key]
                for v in d.values():
                    res = dig(v, key)
                    if res is not None:
                        return res
            elif isinstance(d, list):
                for it in d:
                    res = dig(it, key)
                    if res is not None:
                        return res
            return None

        result_code = dig(data, "resultCode")
        result_msg = dig(data, "resultMsg")
        success_yn = dig(data, "successYn")

        if result_code and str(result_code) not in ("00", "0000", "INFO-000") and (success_yn not in (None, "Y", "true", True)):
            # 에러 메시지 테이블: INFO-100(키 오류) 등 명세에 기재
            raise HTTPException(status_code=502, detail=f"{result_code}: {result_msg}")

        return data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upstream error: {e}")

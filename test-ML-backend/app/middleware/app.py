"""
FastAPI 기반 데모 더미 서버.

간단한 헬스체크와 예측 엔드포인트를 제공하며 CORS 전역 허용, 고정 페이로드
응답 등을 테스트용으로 구현한 라우터다.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="Demo Dummy API")

# CORS: 데모 편의상 전체 허용 (운영 땐 도메인 제한)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True
)

DUMMY_PAYLOAD = {
    "M001": {
        "색상": 7.2,
        "향(Aroma)": 6.8,
        "조직감(Texture)": 6.9,
        "즙성(Juiciness)": 6.5,
        "풍미(Flavor)": 7.1,
        "전체 기호도": 7.0,
    },
    "M003": {
        "색상(Color)": 8.1,
        "향(Aroma)": 7.4,
        "조직감(Texture)": 7.0,
        "즙성(Juiciness)": 6.8,
        "풍미(Flavor)": 7.5,
        "전체 기호도": 7.6,
    },
}


@app.get("/health")
async def health():
    return {"status": "ok"}

def build_dummy_mapping(ids):
    # 요청된 id 리스트에 맞춰 {id: 더미값} 형태로 만들어줌
    return {str(_id): DUMMY_PAYLOAD for _id in ids}

def extract_ids(payload):
    # 여러 형태를 느슨하게 지원: {data_ids: [...]}, {items:[{id:..}|{traceNo:..}]}
    ids = []
    if isinstance(payload, dict):
        if isinstance(payload.get("data_ids"), list):
            ids = payload["data_ids"]
        elif isinstance(payload.get("items"), list):
            for it in payload["items"]:
                if isinstance(it, dict):
                    ids.append(it.get("id") or it.get("traceNo"))
            ids = [i for i in ids if i]  # None 제거
    return ids or ["DUMMY"]  # 비어있으면 기본값

# 1) 우리가 쓰는 표준 엔드포인트
@app.post("/predict")
async def predict(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = None
    ids = extract_ids(payload)
    return JSONResponse(build_dummy_mapping(ids))

# 2) 어떤 POST든 다 더미 리턴(백업용 와일드카드)
@app.api_route("/{path:path}", methods=["POST"])
async def any_post(_: Request, path: str):
    # 경로/바디 상관없이 고정 더미 반환
    return JSONResponse(DUMMY_PAYLOAD)

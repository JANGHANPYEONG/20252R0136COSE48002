"""
육류 정보 CRUD·조회 전반을 담당하는 FastAPI 라우터.

기존 Flask 엔드포인트(add/get/update/delete)를 통합해 원육, 딥에이징, 관능평가,
예측 결과 등 다양한 API를 제공하며 `app.state`에서 세션·스토리지 의존성을 주입해 사용한다.
"""

from typing import Any, Dict, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request, Query
from fastapi.responses import JSONResponse

# 원본 비즈니스 로직 함수 모음
from app.db.db_controller import (
    create_raw_meat_deep_aging_info,
    create_specific_sensory_eval,
    create_specific_std_meat_data,
    create_specific_probexpt_data,
    create_specific_deep_aging_data,
    create_specific_heatedmeat_seonsory_eval,
    _addSpecificPredictData,
    get_meat,
    get_range_meat_data,
    _getMeatDataByUserId,
    _getMeatDataByUserType,
    _getMeatDataByRangeStatusType,
    _getTexanomyData,
    _getPredictionData,
    get_OpenCVresult,
    get_meat_by_partial_id,
    _updateConfirmData,
    _updateRejectData,
    _deleteSpecificDeepAgingData,
    deleteMeatByIDList,
)

# 모델 (일부 엔드포인트에서 사용)
from app.db.db_model import Meat, User  # 경로 유지. 이동했다면 수정 요망.

# 유틸 (원본 코드 그대로 사용)
from app.utils.utils import (
    safe_int,
    safe_bool,
    safe_str,
    convert2datetime,
    species,  # '전체' 처리에 사용
    logger,   # 예외 로깅
)

router = APIRouter()

# --------------------------------------------------------------------------
# 내부 유틸: app.state 에서 공용 리소스 꺼내기
# --------------------------------------------------------------------------
def _require_state_attr(request: Request, name: str) -> Any:
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

# --------------------------------------------------------------------------
# [add_api] 특정 육류의 기본 원육 정보 생성/수정
# --------------------------------------------------------------------------
@router.post("", summary="특정 육류의 기본 원육 정보 생성")
async def create_specific_meat_data(request: Request, data: Dict[str, Any]):
    """
    - 원본: POST /
    - meatId가 기존에 있으면 400
    - 성공 시 초기 DeepAging(seqno=0)도 생성
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        s3_conn = _require_state_attr(request, "s3_conn")
        firestore_conn = _require_state_attr(request, "firestore_conn")

        meat_id = data.get("meatId")
        meat = get_meat(db_session, meat_id)

        if meat:
            return JSONResponse({"msg": "Already Existing Meat"}, status_code=400)

        new_meat_id = create_specific_std_meat_data(
            db_session, s3_conn, firestore_conn, data, meat_id, is_post=1
        )
        if new_meat_id:
            create_raw_meat_deep_aging_info(db_session, new_meat_id, seqno=0)
            return JSONResponse(
                {"msg": "Success to store Raw Meat and Initial DeepAging Information"},
                status_code=200,
            )

        # new_meat_id가 falsy인 경우(원본에 구체 처리 X): 일반 서버 에러로 취급
        return JSONResponse({"msg": "Failed to create meat"}, status_code=500)

    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.patch("", summary="특정 육류의 기본 원육 정보 수정")
async def patch_specific_meat_data(request: Request, data: Dict[str, Any]):
    """
    - 원본: PATCH /
    - 존재하지 않으면 404
    - 이미 확정된 데이터라 수정 불가한 경우 400
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        s3_conn = _require_state_attr(request, "s3_conn")
        firestore_conn = _require_state_attr(request, "firestore_conn")

        meat_id = data.get("meatId")
        meat = get_meat(db_session, meat_id)
        if not meat:
            return JSONResponse({"msg": "Not Existing Meat"}, status_code=404)

        updated_meat_id = create_specific_std_meat_data(
            db_session, s3_conn, firestore_conn, data, meat_id, is_post=0
        )
        if updated_meat_id:
            return JSONResponse(
                {"msg": f"Success to update Raw Meat {updated_meat_id} Information"},
                status_code=200,
            )
        else:
            return JSONResponse({"msg": "Already Confirmed Meat Data"}, status_code=400)

    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# --------------------------------------------------------------------------
# [add_api] 특정 육류의 딥에이징 이력 생성/수정
# --------------------------------------------------------------------------
@router.post("/deep-aging-data", summary="특정 육류의 딥에이징 이력 생성")
async def add_specific_deep_aging_data(request: Request, data: Dict[str, Any]):
    """
    - POST /deep-aging-data
    - 필수: meatId, seqno, deepAging
    - 반환 코드: 로직 함수에서 오는 값을 그대로 사용
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        if not (data.get("meatId") and data.get("seqno") and data.get("deepAging")):
            return JSONResponse({"msg": "Failed to Create Deep Aging Data"}, status_code=400)

        deep_aging_id = create_specific_deep_aging_data(db_session, data, is_post=1)
        if deep_aging_id:
            return JSONResponse(
                {"msg": f"Success to Create Deep Aging Data {deep_aging_id}"},
                status_code=200,
            )
        elif deep_aging_id is None:
            return JSONResponse(
                {"msg": f"Meat {data['meatId']} Does NOT Exists"}, status_code=404
            )
        else:
            return JSONResponse(
                {"msg": f"Seqno {data['seqno']} Deep Aging Info. Already Exists"},
                status_code=400,
            )
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.patch("/deep-aging-data", summary="특정 육류의 딥에이징 이력 수정")
async def patch_specific_deep_aging_data(request: Request, data: Dict[str, Any]):
    """
    - PATCH /deep-aging-data
    - 필수: meatId, seqno, isCompleted
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        if not (
            data.get("meatId")
            and (data.get("seqno") is not None)
            and (data.get("isCompleted") is not None)
        ):
            return JSONResponse({"msg": "Failed to Patch Deep Aging Data"}, status_code=400)

        deep_aging_id = create_specific_deep_aging_data(db_session, data, is_post=0)
        if deep_aging_id:
            return JSONResponse(
                {"msg": f"Success to Patch Deep Aging Data {deep_aging_id}"},
                status_code=200,
            )
        elif deep_aging_id is None:
            return JSONResponse(
                {"msg": f"Meat {data['meatId']} Does NOT Exists"}, status_code=404
            )
        else:
            return JSONResponse(
                {"msg": f"Seqno {data['seqno']} Does NOT Exists"}, status_code=404
            )
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# --------------------------------------------------------------------------
# [add_api] 특정 육류의 관능/가열육/실험실/예측 데이터 생성/수정
# --------------------------------------------------------------------------
@router.post("/sensory-eval", summary="특정 육류의 관능 검사 결과 생성")
@router.patch("/sensory-eval", summary="특정 육류의 관능 검사 결과 수정")
async def upsert_specific_sensory_eval(request: Request, data: Dict[str, Any]):
    """
    - POST/PATCH /sensory-eval
    - 내부 로직이 {"msg": ..., "code": ...} 형태로 응답하므로 그대로 전달
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        s3_conn = _require_state_attr(request, "s3_conn")
        firestore_conn = _require_state_attr(request, "firestore_conn")

        is_post = 1 if request.method.upper() == "POST" else 0
        result = create_specific_sensory_eval(
            db_session, s3_conn, firestore_conn, data, is_post=is_post
        )
        return JSONResponse({"msg": result["msg"]}, status_code=result["code"])
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.post("/heatedmeat-eval", summary="특정 육류의 가열육 관능 검사 결과 생성")
@router.patch("/heatedmeat-eval", summary="특정 육류의 가열육 관능 검사 결과 수정")
async def upsert_specific_heatedmeat_eval(request: Request, data: Dict[str, Any]):
    """
    - POST/PATCH /heatedmeat-eval
    - 메서드별 필수 키 체크 (원본과 동일)
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        firestore_conn = _require_state_attr(request, "firestore_conn")
        s3_conn = _require_state_attr(request, "s3_conn")

        if request.method.upper() == "POST":
            is_post = True
            for key in ("meatId", "seqno", "userId", "imgAdded", "heatedmeatSensoryData"):
                if key not in data or data[key] is None:
                    return JSONResponse({"msg": "Failed to POST Heatedmeat Sensory Data"}, status_code=400)
        else:  # PATCH
            is_post = False
            for key in ("meatId", "seqno", "imgAdded", "heatedmeatSensoryData"):
                if key not in data or data[key] is None:
                    return JSONResponse({"msg": "Failed to PATCH Heatedmeat Sensory Data"}, status_code=400)

        result = create_specific_heatedmeat_seonsory_eval(
            db_session, firestore_conn, s3_conn, data, is_post
        )
        return JSONResponse({"msg": result["msg"]}, status_code=result["code"])
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.post("/probexpt-data", summary="특정 육류의 실험실 데이터 생성")
@router.patch("/probexpt-data", summary="특정 육류의 실험실 데이터 수정")
async def upsert_specific_probexpt_data(request: Request, data: Dict[str, Any]):
    """
    - POST/PATCH /probexpt-data
    - 메서드별 필수 키 체크 (원본과 동일)
    """
    try:
        db_session = _require_state_attr(request, "db_session")

        if request.method.upper() == "POST":
            is_post = True
            for key in ("meatId", "seqno", "isHeated", "userId", "probexptData"):
                if key not in data or data[key] is None:
                    return JSONResponse({"msg": "Failed to POST Probexpt Data"}, status_code=400)
        else:  # PATCH
            is_post = False
            for key in ("meatId", "seqno", "isHeated", "probexptData"):
                if key not in data or data[key] is None:
                    return JSONResponse({"msg": "Failed to PATCH Probexpt Data"}, status_code=400)

        result = create_specific_probexpt_data(db_session, data, is_post)
        return JSONResponse({"msg": result["msg"]}, status_code=result["code"])
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.post("/predict-data", summary="예측 데이터 생성")
async def add_specific_predict_data(request: Request, data: Optional[Dict[str, Any]] = None):
    """
    - POST /predict-data
    - 원본 GET은 404 처리 → 여기서도 GET은 제공하지 않음
    """
    try:
        if not data:
            return JSONResponse({"msg": "No data in Request."}, status_code=401)

        db_session = _require_state_attr(request, "db_session")
        # 원본 함수가 (Response, code) 형태를 반환할 수 있어 그대로 전달
        return _addSpecificPredictData(db_session, data)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=505,
        )


# --------------------------------------------------------------------------
# [get_api] 조회 계열
# --------------------------------------------------------------------------
@router.get("", summary="범위/종 필터 조회")
async def get_meat_data(
    request: Request,
    offset: Optional[str] = Query(None),
    count: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    specieValue: Optional[str] = Query(None),
):
    """
    - GET /
    - specieValue == '전체' 이면 2, 아니면 species.index(specieValue)
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        if specieValue == "전체":
            specie_value = 2
        else:
            specie_value = species.index(specieValue) if specieValue else None

        result = get_range_meat_data(db_session, offset, count, start, end, specie_value)
        return JSONResponse(result, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.get("/by-meat-id", summary="meatId 단건 조회")
async def get_meat_data_by_id(request: Request, meatId: Optional[str] = Query(None)):
    try:
        db_session = _require_state_attr(request, "db_session")
        if meatId is None:
            return JSONResponse({"msg": "Invalid Meat ID"}, status_code=400)

        result = get_meat(db_session, meatId)
        if result:
            return JSONResponse(result, status_code=200)
        else:
            return JSONResponse({"msg": f"No Meat data found for {meatId}"}, status_code=404)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.get("/by-partial-id", summary="meatId 부분 일치 조회")
async def get_meat_data_by_partial_id(
    request: Request,
    meatId: Optional[str] = Query(None),
    offset: Optional[str] = Query(None),
    count: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    specieValue: Optional[str] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")
        if specieValue == "전체":
            specie_value = 2
        else:
            specie_value = species.index(specieValue) if specieValue else None

        if meatId is None:
            return JSONResponse({"msg": "Invalid Meat Id"}, status_code=400)

        meats = get_meat_by_partial_id(db_session, meatId, offset, count, start, end, specie_value)
        return JSONResponse(meats, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.get("/by-range-data", summary="범위 + 표시 여부 필터 조회")
async def get_meat_data_by_range_data(
    request: Request,
    offset: Optional[str] = Query(None),
    count: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    farmAddr: Optional[str] = Query(None),
    userId: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    createdAt: Optional[str] = Query(None),
    statusType: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")

        result = get_range_meat_data(
            db_session,
            offset,
            count,
            start,
            end,
            safe_bool(farmAddr),
            safe_bool(userId),
            safe_bool(type),
            safe_bool(createdAt),
            safe_bool(statusType),
            safe_bool(company),
        )
        # 원본은 (payload, 200) 튜플 형태로 반환했지만 여기선 JSON만 반환
        return JSONResponse(result, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=505,
        )


@router.get("/by-user-id", summary="특정 사용자 기준 조회")
async def get_meat_data_by_user_id(
    request: Request,
    userId: Optional[str] = Query(None),
    offset: Optional[str] = Query(None),
    count: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")

        _offset = safe_int(offset)
        _count = safe_int(count)
        if not (userId and start and end) or _offset is None or _count is None:
            return JSONResponse({"msg": "Invalid parameter"}, status_code=400)

        meat_by_user = _getMeatDataByUserId(db_session, userId, _offset, _count, start, end)
        return JSONResponse(meat_by_user, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.get("/by-user-type", summary="사용자 타입별 조회")
async def get_meat_data_by_user_type(request: Request, userType: Optional[str] = Query(None)):
    try:
        db_session = _require_state_attr(request, "db_session")
        if userType:
            return _getMeatDataByUserType(db_session, userType)
        else:
            return JSONResponse({"msg": "No userType in parameter"}, status_code=400)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=505,
        )


@router.get("/by-user-total", summary="전체 사용자별 생성 데이터 집계")
async def get_meat_data_by_user_total(request: Request):
    """
    - 원본은 Flask Response를 그대로 모아서 반환했음.
    - 여기서는 dict로 통일: {userId: <해당 사용자 데이터>}
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        users = db_session.query(User).all()

        user_meats: Dict[str, Any] = {}
        for user in users:
            # 원본 시그니처 불명확 → 가장 단순 형태로 호출을 시도
            try:
                result = _getMeatDataByUserId(db_session, user.userId)
                # result가 (payload, code) 형태일 수도 있으니 분기 처리
                if isinstance(result, tuple) and len(result) >= 1:
                    payload = result[0]
                else:
                    payload = result
            except TypeError:
                # 인자가 더 필요하면 None/기본값으로 재시도
                payload = _getMeatDataByUserId(db_session, user.userId, 0, 100, None, None)
            # Flask Response 호환 처리
            if hasattr(payload, "get_json"):
                user_meats[user.userId] = payload.get_json()
            else:
                user_meats[user.userId] = payload
        return JSONResponse(user_meats, status_code=200)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=505,
        )


@router.get("/by-status", summary="승인 여부 + 범위 조회")
async def get_meat_data_by_range_status_type(
    request: Request,
    statusType: Optional[str] = Query(None),
    offset: Optional[str] = Query(None),
    count: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
    specieValue: Optional[str] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")
        start_dt = convert2datetime(start, 0) if start else None
        end_dt = convert2datetime(end, 0) if end else None

        if statusType is not None and specieValue is not None:
            return _getMeatDataByRangeStatusType(
                db_session, statusType, offset, count, specieValue, start_dt, end_dt
            )
        else:
            return JSONResponse(
                {"msg": "Invalid statusType or specieValue in parameter"}, status_code=400
            )
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )

# Texanomy 하드코딩 기본 데이터 출력
@router.get("/default-data", summary="Texanomy 기본 데이터")
async def get_texanomy_default_data(request: Request):
    try:
        db_session = _require_state_attr(request, "db_session")
        return _getTexanomyData(db_session)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# 예측 데이터 조회
@router.get("/predict-data", summary="예측 결과 조회")
async def get_prediction_data(
    request: Request,
    meatId: Optional[str] = Query(None),
    seqno: Optional[int] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")
        meat_id = safe_str(meatId)
        seq_no = safe_int(seqno)
        if meat_id and (seq_no is not None):
            return _getPredictionData(db_session, meat_id, seq_no)
        else:
            return JSONResponse({"msg": "Invalid id or seqno parameter"}, status_code=404)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# opencv 결과 조회    
@router.get("/opencv-image", summary="OpenCV 결과 조회")
async def get_opencv_data(
    request: Request,
    meatId: Optional[str] = Query(None),
    seqno: Optional[int] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")
        meat_id = safe_str(meatId)
        seq_no = safe_int(seqno)

        if meat_id and (seq_no is not None):
            result = get_OpenCVresult(db_session, meat_id, seq_no)
            if result:
                return JSONResponse(result, status_code=200)
            else:
                return JSONResponse({"msg": "OpenCV Result Does Not Exist"}, status_code=400)
        return JSONResponse({"msg": "Invalid id or seqno parameter"}, status_code=404)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# --------------------------------------------------------------------------
# [update_api] 승인/반려
# --------------------------------------------------------------------------
@router.patch("/confirm", summary="육류 데이터 승인")
async def update_confirm_data(request: Request, meatId: Optional[str] = Query(None)):
    try:
        db_session = _require_state_attr(request, "db_session")
        meat_id = safe_str(meatId)
        if meat_id:
            return _updateConfirmData(db_session, meat_id)
        else:
            return JSONResponse({"msg": "No meatId parameter"}, status_code=400)
    except Exception as e:
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


@router.patch("/reject", summary="육류 데이터 반려")
async def update_reject_data(request: Request, meatId: Optional[str] = Query(None)):
    try:
        db_session = _require_state_attr(request, "db_session")
        meat_id = safe_str(meatId)
        if meat_id:
            return _updateRejectData(db_session, meat_id)
        else:
            return JSONResponse({"msg": "No meatId parameter"}, status_code=400)
    except Exception as e:
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# --------------------------------------------------------------------------
# [delete_api] 삭제
# --------------------------------------------------------------------------
# 전체 육류 데이터 삭제
@router.delete("", summary="육류 데이터 일괄 삭제")
async def delete_total_meat_data(request: Request, body: Dict[str, Any]):
    """
    - DELETE /
    - body: {"id": ["A001", "A002", ...]}
    """
    try:
        db_session = _require_state_attr(request, "db_session")
        s3_conn = _require_state_attr(request, "s3_conn")

        id_list = (body or {}).get("id")
        if id_list:
            _, fail = deleteMeatByIDList(db_session, s3_conn, id_list)
            if not fail:
                return JSONResponse({"msg": "Success to Delete ID List"}, status_code=200)
            else:
                return JSONResponse(
                    {"msg": f"Fail to Delete ID List: {', '.join([_id for _id in fail])}"},
                    status_code=400,
                )
        # id_list 미지정 시 400
        return JSONResponse({"msg": "Invalid body: 'id' is required"}, status_code=400)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )


# 특정 육류의 딥에이징 이력 삭제
@router.delete("/deep-aging", summary="특정 육류의 딥에이징 이력 삭제")
async def delete_deep_aging_data(
    request: Request,
    meatId: Optional[str] = Query(None),
    seqno: Optional[int] = Query(None),
):
    try:
        db_session = _require_state_attr(request, "db_session")
        s3_conn = _require_state_attr(request, "s3_conn")

        _id = safe_str(meatId)
        _seq = safe_int(seqno)
        if _id and _seq:
            result = _deleteSpecificDeepAgingData(db_session, s3_conn, _id, _seq)
            return JSONResponse({"msg": result["msg"]}, status_code=result["code"])
        else:
            return JSONResponse({"msg": "Invalid id and seqno"}, status_code=400)
    except Exception as e:
        logger.exception(str(e))
        return JSONResponse(
            {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")},
            status_code=500,
        )

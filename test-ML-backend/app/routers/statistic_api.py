"""
육류 통계 데이터를 제공하는 라우터.

기간별 비율, 부위별 집계, 시계열 등 대시보드에 필요한 통계 API를 노출한다.
"""

from app.db.db_controller import (
    get_num_of_processed_raw,
    get_num_by_farmAddr,
    get_probexpt_of_meat,
    get_sensory_of_meat,
    get_sensory_of_raw_heatedmeat,
    get_timeseries_of_cattle_data,
)
from fastapi import APIRouter, Request, Query
from fastapi.responses import JSONResponse
from datetime import datetime
from utils import *

router = APIRouter()

# 1. 신선육, 숙성육 비율(소, 돼지 전체)
# 최종 엔드포인트: /meat/statistic/ratio/fresh-and-processed
@router.get("/ratio/fresh-and-processed")
def getRatioFreshAndProcessed(
    request: Request,

    # start, end -> DB에서 특정 기간의 데이터를 필터링하는 데 사용되는 파라미터
    # db_controller.pt에서 start 및 end를 기간 설정을 위한 변수로 사용
    start: str = Query(None, description="[format] YYYY-MM-DD"), # Optional Query Parameter 
    end: str = Query(None, description="[format] YYYY-MM-DD"), # str 타입 대신에 date 타임을 쓸지?
):
    try:
        db_session = request.app.state.db_session # Flask의 current_app 대체
        start = safe_str(start)
        end = safe_str(end)

        if start and end:
            ratio_data = get_num_of_processed_raw(db_session, start, end)
            return JSONResponse(content=ratio_data, status_code=200)
        else: 
            return JSONResponse(content={"msg": "Invalid date range"}, status_code=400)

    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

# 2. 대분류 부위 별 개수(소, 돼지)
@router.get("/counts/by-large-part")
def getCountsByLargePart(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)

        if start and end:
            counts_data = get_num_by_farmAddr(db_session, start, end)
            return JSONResponse(content=counts_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid date range"}, status_code=400)

    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )
    
# 3. 농장 지역 별 개수(소, 돼지)
@router.get("/counts/by-farm-location")
def getCountsByFarmLocation(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)

        if start and end:
            counts_data = get_num_by_farmAddr(db_session, start, end)
            return JSONResponse(content=counts_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid date range"}, status_code=400)

    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

# 4. 신선육 맛데이터 항목 별 평균, 최대, 최소
# probexpt = Probe/Profiling Experiment (관능평가·맛 분석 실험 데이터)로 추정됨
@router.get("/probexbt-stats/fresh")
def getProbexptStatsOfFresh(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
    animal_type: str = Query(None, description="Animal type (cattle, pig)"), # 2025 기준은 pig만 있음.
    grade: int = Query(None, description="Grade of meat (1-5)"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)
        animal_type = safe_str(animal_type)
        grade = safe_int(grade)

        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            probexpt_data = get_probexpt_of_meat(db_session, start, end, specie_id, grade)
            return JSONResponse(content=probexpt_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

# 5. 처리육 맛데이터 항목 별 평균, 최대, 최소
@router.get("/probexbt-stats/processed")
def getProbexptStatsOfProcessed(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
    animal_type: str = Query(None, description="Animal type (cattle, pig)"),
    grade: int = Query(None, description="Grade of meat (1-5)"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)
        animal_type = safe_str(animal_type)
        grade = safe_int(grade)

        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            probexpt_data = get_probexpt_of_meat(db_session, start, end, specie_id, grade)
            return JSONResponse(content=probexpt_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

# 6. 신선역 관능검사 데이터 항목 별 평균, 최대, 최소
@router.get("/sensory-stats/fresh")
def getSensoryStatsOfFresh(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
    animal_type: str = Query(None, description="Animal type (cattle, pig)"),
    grade: int = Query(None, description="Grade of meat (1-5)"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)
        animal_type = safe_str(animal_type)
        grade = safe_int(grade)

        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            sensory_data = get_sensory_of_meat(db_session, start, end, specie_id, grade)
            return JSONResponse(content=sensory_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )
    
# 7. 가공육 관능검사 데이터 항목 별 평균, 최대, 최소
@router.get("/sensory-stats/processed")
def getSensoryStatsOfProcessed(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
    animal_type: str = Query(None, description="Animal type (cattle, pig)"),
    grade: int = Query(None, description="Grade of meat (1-5)"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)
        animal_type = safe_str(animal_type)
        grade = safe_int(grade)

        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            sensory_data = get_sensory_of_meat(db_session, start, end, specie_id, grade)
            return JSONResponse(content=sensory_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

# 8. 가열된 신선육 관능 데이터 각 항목 별 평균, 최대, 최소
@router.get("/sensory-stats/heated-fresh")
def getSensoryStatsOfHeatedFresh(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
    animal_type: str = Query(None, description="Animal type (cattle, pig)"),
    grade: int = Query(None, description="Grade of meat (1-5)"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)
        animal_type = safe_str(animal_type)
        grade = safe_int(grade)

        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            sensory_data = get_sensory_of_raw_heatedmeat(db_session, start, end, specie_id, grade)
            return JSONResponse(content=sensory_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

# # 9. 가열된 가공육 관능 데이터 각 항목 별 평균, 최대, 최소
# @router.get("/sensory-stats/heated-processed")
# def getSensoryStatsOfHeatedProcessed(
#     request: Request,
#     start: str = Query(None, description="[format] YYYY-MM-DD"),
#     end: str = Query(None, description="[format] YYYY-MM-DD"),
#     seqno: int = Query(None, description="Sequence number"),
# ):
#     try:
#         db_session = request.app.state.db_session
#         start = safe_str(start)
#         end = safe_str(end)
#         seqno = safe_int(seqno)

#         if start and end and (seqno is not None):
#             sensory_data = get_sensory_of_processed_heatmeat(db_session, start, end, seqno)
#             return JSONResponse(content=sensory_data, status_code=200)
#         else:
#             return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
#     except Exception as e:
#         logger.exception(e)
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "msg": "Server Error",
#                 "time": datetime.now().strftime("%H:%M:%S")
#             }
#         )

# # 10. 가열된 가공육 맛 데이터 각 항목 별 평균, 최대, 최소
# @router.get("/probexbt-stats/heated-processed")
# def getProbexptStatsOfHeatedProcessed(
#     request: Request,
#     start: str = Query(None, description="[format] YYYY-MM-DD"),
#     end: str = Query(None, description="[format] YYYY-MM-DD"),
# ):
#     try:
#         db_session = request.app.state.db_session
#         start = safe_str(start)
#         end = safe_str(end)

#         if start and end:
#             sensory_data = get_probexpt_of_processed_heatmeat(db_session, start, end)
#             return JSONResponse(content=sensory_data, status_code=200)
#         else:
#             return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
#     except Exception as e:
#         logger.exception(e)
#         return JSONResponse(
#             status_code=500,
#             content={
#                 "msg": "Server Error",
#                 "time": datetime.now().strftime("%H:%M:%S")
#             }
#         )

# 11. 시계열 데이터 조회
@router.get("/time")
def getTimeSeriesData(
    request: Request,
    start: str = Query(None, description="[format] YYYY-MM-DD"),
    end: str = Query(None, description="[format] YYYY-MM-DD"),
    meat_value: str = Query(None, description="Meat value"),
    seqno: int = Query(None, description="Sequence number"),
):
    try:
        db_session = request.app.state.db_session
        start = safe_str(start)
        end = safe_str(end)
        meat_value = safe_str(meat_value)
        seqno = safe_int(seqno)

        if start and end and meat_value and (seqno is not None):
            sensory_data = get_timeseries_of_cattle_data(db_session, start, end, meat_value, seqno)
            return JSONResponse(content=sensory_data, status_code=200)
        else:
            return JSONResponse(content={"msg": "Invalid query parameters"}, status_code=400)
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content={
                "msg": "Server Error",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        )

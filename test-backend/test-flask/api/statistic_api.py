from db.db_controller import (
    get_num_of_processed_raw,
    get_num_of_cattle_pig,
    get_num_of_primal_part,
    get_num_by_farmAddr,
    get_probexpt_of_meat,
    get_probexpt_of_processedmeat,
    get_sensory_of_rawmeat,
    get_sensory_of_processedmeat,
    get_sensory_of_processed_heatedmeat,
    get_sensory_of_raw_heatedmeat,
    get_probexpt_of_processed_heatedmeat,
)
from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
from utils import *

statistic_api = Blueprint("statistic_api", __name__)


# 1. 신선육, 숙성육 비율(소, 돼지 전체)
@statistic_api.route("/ratio/fresh-and-processed", methods=["GET"])
def getRatioFreshAndProcessed():
    try:
        db_session = current_app.db_session
        start = safe_str(request.args.get("start"))
        end = safe_str(request.args.get("end"))
        if start and end:
            ratio_data = get_num_of_processed_raw(db_session, start, end)
            return jsonify(ratio_data), 200
        else:
            return jsonify({"msg": "Invalid Parameter"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )


# 2. 소, 돼지 개수
@statistic_api.route("/counts/cattle-and-pork", methods=["GET", "POST"])
def getCountsCattleAndPork():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            start = safe_str(request.args.get("start"))
            end = safe_str(request.args.get("end"))
            if start and end:
                return get_num_of_cattle_pig(db_session, start, end)
            else:
                return jsonify("No id parameter"), 401

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )


# 3. 대분류 부위 별 개수(소, 돼지)
@statistic_api.route("/counts/by-large-part", methods=["GET"])
def getCountsByLargePart():
    try:
        db_session = current_app.db_session
        start = safe_str(request.args.get("start"))
        end = safe_str(request.args.get("end"))
        if start and end:
            meat_by_species = get_num_of_primal_part(db_session, start, end)
            return jsonify(meat_by_species), 200
        else:
            return jsonify({"msg": "Invalid Parameter"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 4. 농장 지역 별 개수(소,돼지)
@statistic_api.route("/counts/by-farm-location", methods=["GET"])
def getCountsByFarmLocation():
    try:
        db_session = current_app.db_session
        start = safe_str(request.args.get("start"))
        end = safe_str(request.args.get("end"))
        if start and end:
            meat_by_farm = get_num_by_farmAddr(db_session, start, end)
            return jsonify(meat_by_farm), 200
        else:
            return jsonify({"msg": "Invalid Parameter"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 5. 신선육 맛데이터 항목 별 평균, 최대, 최소
@statistic_api.route("/probexpt-stats/fresh", methods=["GET"])
def getProbexptStatsOfFresh():
    try:
        db_session = current_app.db_session
        start = safe_str(request.args.get("start"))
        end = safe_str(request.args.get("end"))
        animal_type = safe_str(request.args.get("animalType"))
        grade = safe_int(request.args.get("grade"))
        
        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            probexpt_raw_data = get_probexpt_of_meat(db_session, start, end, specie_id, grade, is_raw=1)
            
            return jsonify(probexpt_raw_data), 200
        else:
            return jsonify({"msg": "Invalid Parameter"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 6. 처리육 맛데이터 항목 별 평균, 최대, 최소
@statistic_api.route("/probexpt-stats/processed", methods=["GET"])
def getProbexptStatsOfProcessed():
    try:
        db_session = current_app.db_session
        start = safe_str(request.args.get("start"))
        end = safe_str(request.args.get("end"))
        animal_type = safe_str(request.args.get("animalType"))
        grade = safe_int(request.args.get("grade"))
        seqno = safe_int(request.args.get("seqno"))
            
        if start and end and animal_type and (grade is not None):
            specie_id = species.index(animal_type)
            probexpt_processed_data = get_probexpt_of_meat(db_session, start, end, specie_id, grade, is_raw=0)
                
            return jsonify(probexpt_processed_data), 200
        else:
            return jsonify({"msg": "Invalid Parameter"}), 400
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )

# 7. 신선육 관능검사 데이터 항목 별 평균, 최대, 최소
@statistic_api.route("/sensory-stats/fresh", methods=["GET", "POST"])
def getSensoryStatsOfFresh():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            start = safe_str(request.args.get("start"))
            end = safe_str(request.args.get("end"))
            if start and end:
                return get_sensory_of_rawmeat(db_session, start, end)
            else:
                return jsonify("No id parameter"), 401

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

# 8. 가공육 관능검사 데이터 항목 별 평균, 최대, 최소
@statistic_api.route("/sensory-stats/processed", methods=["GET", "POST"])
def getSensoryStatsOfProcessed():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            start = safe_str(request.args.get("start"))
            end = safe_str(request.args.get("end"))
            seqno = safe_int(request.args.get("seqno"))
            if start and end:
                return get_sensory_of_processedmeat(db_session, seqno, start, end)
            else:
                return jsonify("No id parameter"), 401

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )


# 9. 가열된 신선육 관능 데이터 각 항목 별 평균, 최대, 최소
@statistic_api.route("/sensory-stats/heated-fresh", methods=["GET", "POST"])
def getSensoryStatsOfHeatedFresh():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            start = safe_str(request.args.get("start"))
            end = safe_str(request.args.get("end"))
            if start and end:
                return get_sensory_of_raw_heatedmeat(db_session, start, end)
            else:
                return jsonify("No id parameter"), 401

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )


# 10. 가열된 가공육 관능 데이터 각 항목 별 평균, 최대, 최소
@statistic_api.route("/sensory-stats/heated-processed", methods=["GET", "POST"])
def getSensoryStatsOfHeatedProcessed():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            start = safe_str(request.args.get("start"))
            end = safe_str(request.args.get("end"))
            seqno = safe_int(request.args.get("seqno"))
            if start and end:
                return get_sensory_of_processed_heatedmeat(
                    db_session, seqno, start, end
                )
            else:
                return jsonify("No id parameter"), 401

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )


# 11. 가열된 가공육 맛 데이터 각 항목 별 평균, 최대, 최소
@statistic_api.route("/probexpt-stats/heated-processed", methods=["GET", "POST"])
def getProbexptStatsOfHeatedProcessed():
    try:
        if request.method == "GET":
            db_session = current_app.db_session
            start = safe_str(request.args.get("start"))
            end = safe_str(request.args.get("end"))
            if start and end:
                return get_probexpt_of_processed_heatedmeat(db_session, start, end)
            else:
                return jsonify("No id parameter"), 401

        else:
            return jsonify({"msg": "Invalid Route, Please Try Again."}), 404
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            505,
        )

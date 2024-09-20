from flask import Blueprint, current_app, jsonify, request
import logging
from datetime import datetime
import pprint

from opencv_utils import *
from db.db_controller import *
from ml_utils import *


predict_api = Blueprint("predict_api", __name__)

logger = logging.getLogger(__name__)


# 특정 육류의 컬러팔레트 조회
@predict_api.route("/color-palette", methods=["GET"])
def create_meat_palette():
    s3_conn = current_app.s3_conn
    meat_id = request.args.get("meatId")
    seqno = request.args.get("seqno")
    
    img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
    result = display_palette_with_ratios(img)
    return jsonify({"meatId": meat_id, "seqno": seqno, "result": result})


# 특정 육류의 텍스쳐 정보 조회
@predict_api.route("/texture-info", methods=["GET"])
def create_meat_texture_info():
    s3_conn = current_app.s3_conn
    meat_id = request.args.get("meatId")
    seqno = request.args.get("seqno")
    
    img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
    texture_result = create_texture_info(img)
    return texture_result


# 특정 육류의 텍스쳐 정보 조회
@predict_api.route("/lbp-gabor", methods=["GET"])
def create_meat_lbp_garbor_images():
    s3_conn = current_app.s3_conn
    meat_id = request.args.get("meatId")
    seqno = request.args.get("seqno")
    
    img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
    
    lbp_result = lbp_calculate(s3_conn, img, meat_id, seqno)
    gabor_result = gabor_texture_analysis(s3_conn, img, meat_id, seqno)
    pprint.pprint(gabor_result)
    return lbp_result, gabor_result


# 원육 이미지에 대해서 opencv 전처리 진행 (컬러팔레트, 텍스쳐 정보, lbp-gabor, 단면 이미지)
@predict_api.route("/process-image", methods=["POST", "PATCH"])
def create_raw_meat_opencv_info():
    try:
        db_session = current_app.db_session
        s3_conn = current_app.s3_conn
        meat_id = request.args.get("meatId")
        seqno = request.args.get("seqno")
        
        # 해당 육류 - 회차의 관능 데이터가 존재하지 않을 때
        sensory_info = get_SensoryEval(db_session, meat_id, seqno)
        if not sensory_info:
            return {"msg": f"Sensory Info Does Not Exist: {meat_id} - {seqno}"}, 400
        
        # 해당 육류 - 회차의 opencv 데이터가 존재할 때
        opencv_info = get_OpenCVresult(db_session, meat_id, seqno)
        if opencv_info:
            return {"msg": f"OpenCV Result Already Exists"}, 400
        
        segment_img_object = extract_section_image(f"sensory_evals/{meat_id}-{seqno}.png", meat_id, seqno)
        
        if segment_img_object:
            result = process_opencv_image(db_session, s3_conn, meat_id, seqno, segment_img_object)
            return jsonify({"msg": f"Success to create OpenCV Info"}), 200
        else:
            return jsonify({"msg": f"Fail to create OpenCV data"}), 400
    except Exception as e:
        logging.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )
        

# 예측 실행 (예측 관능 평가, 예측 등급)
@predict_api.route("/sensory-eval", methods=["POST"])
def predict_sensory_eval():
    try:
        db_session = current_app.db_session
        s3_conn = current_app.s3_conn
        meat_id = safe_str(request.args.get("meatId"))
        seqno = safe_int(request.args.get("seqno"))
        
        # 해당 육류 - 회차의 관능 데이터가 존재하지 않을 때
        sensory_info = get_SensoryEval(db_session, meat_id, seqno)
        if not sensory_info:
            return {"msg": f"Sensory Info Does Not Exist: {meat_id} - {seqno}"}, 400
        
        # 해당 육류 - 회차의 예측 관능, 등급 데이터가 존재할 때
        ai_sensory_info = get_AI_SensoryEval(db_session, meat_id, seqno)
        if ai_sensory_info:
            return {"msg": f"AI Sensory Info Already Exists"}, 400
        
        ai_sensory_data = process_predict_sensory_eval(db_session, s3_conn, meat_id, seqno)
        if ai_sensory_data:
            return jsonify({"msg": f"Success to create Predict Data"}), 200
        else:
            return jsonify({"msg": f"Fail to create Predict Data"}), 400

    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        ) 
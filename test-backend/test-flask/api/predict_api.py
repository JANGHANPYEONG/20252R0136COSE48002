from flask import Blueprint, current_app, jsonify, request
import logging
from datetime import datetime
import pprint

from opencv_utils import *
from db.db_controller import *


predict_api = Blueprint("predict_api", __name__)


# 특정 육류의 컬러팔레트 도출
@predict_api.route("/color_palette", methods=["GET"])
def create_meat_palette():
    s3_conn = current_app.s3_conn
    meat_id = request.args.get("meatId")
    seqno = request.args.get("seqno")
    
    img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
    print("Success to Download Image From S3")
    result = display_palette_with_ratios(img)
    return jsonify({"meatId": meat_id, "seqno": seqno, "result": result})


# 특정 육류의 텍스쳐 정보 도출
@predict_api.route("/texture_info", methods=["GET"])
def create_meat_texture_info():
    s3_conn = current_app.s3_conn
    meat_id = request.args.get("meatId")
    seqno = request.args.get("seqno")
    
    img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
    texture_result = create_texture_info(img)
    print(texture_result)
    return texture_result


# 특정 육류의 텍스쳐 정보 도출
@predict_api.route("/lbp_gabor", methods=["GET"])
def create_meat_lbp_garbor_images():
    s3_conn = current_app.s3_conn
    meat_id = request.args.get("meatId")
    seqno = request.args.get("seqno")
    
    img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
    
    lbp_result = lbp_calculate(s3_conn, img, meat_id, seqno)
    print(lbp_result)
    gabor_result = gabor_texture_analysis(s3_conn, img, meat_id, seqno)
    pprint.pprint(gabor_result)
    return lbp_result, gabor_result


# 원육 이미지에 대해서 opencv 전처리 진행
@predict_api.route("/process-image", methods=["POST", "PATCH"])
def create_raw_meat_opencv_info():
    try:
        db_session = current_app.db_session
        s3_conn = current_app.s3_conn
        meat_id = request.args.get("meatId")
        img = s3_conn.download_image(f"sensory_evals/{meat_id}-0.png")
        segment_img_object = extract_section_image(s3_conn, f"sensory_evals/{meat_id}-0.png", meat_id)
        
        if segment_img_object:
            result = process_opencv_image(db_session, s3_conn, meat_id, segment_img_object)
            return jsonify({"msg": f"Success to create OpenCV Info"}), 200
        else:
            return jsonify({"msg": f"Fail to create Segmentation Images"}), 400
    except Exception as e:
        logging.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )
        

# 예측 실행
@predict_api.route("/sensory-eval", methods=["POST"])
def predict_sensory_eval():
    try:
        db_session = current_app.db_session
        s3_conn = current_app.s3_conn
        meat_id = request.args.get("meatId")
        seqno = request.args.get("seqno")
        img = s3_conn.download_image(f"sensory_evals/{meat_id}-{seqno}.png")
        segment_img_object = extract_section_image(s3_conn, f"sensory_evals/{meat_id}-{seqno}.png", meat_id)
        


    except Exception as e:
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        ) 
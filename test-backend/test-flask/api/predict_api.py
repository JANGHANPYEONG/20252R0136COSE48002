from flask import Blueprint, current_app, jsonify, request

from opencv_utils import *


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
    return gabor_result
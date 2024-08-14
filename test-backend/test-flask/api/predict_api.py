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
    result = final_color_palette_proportion(img)
    return jsonify({"meatId": meat_id, "seqno": seqno, "result": result})
from flask import (
    Blueprint,
    jsonify,
    request,
    current_app,
)
import os
import zipfile
from datetime import datetime
from werkzeug.utils import secure_filename
from db.db_controller import (
    create_raw_meat_deep_aging_info,
    create_specific_sensory_eval,
    create_specific_std_meat_data,
    create_specific_probexpt_data,
    create_specific_deep_aging_data,
    create_specific_heatedmeat_seonsory_eval,
    _addSpecificPredictData,
    get_meat,
)
from utils import *

add_api = Blueprint("add_api", __name__)


# 대량 데이터 업로드 (CSV + ZIP 이미지)
@add_api.route("/upload/data", methods=["POST"])
def upload_bulk_data():
    """
    프론트엔드에서 CSV 레이블 파일과 ZIP 이미지 파일을 받아
    /home/ubuntu/2025-Deeplant-Dev/database/label 및 image 폴더에 저장
    """
    try:
        # 기본 경로 설정
        base_path = request.form.get('basePath', '/home/ubuntu/2025-Deeplant-Dev/database')
        csv_folder = request.form.get('csvPath', 'label')
        image_folder = request.form.get('imagePath', 'image')
        
        # 전체 경로 생성
        csv_dir = os.path.join(base_path, csv_folder)
        image_dir = os.path.join(base_path, image_folder)
        
        # 디렉토리 생성 (존재하지 않는 경우)
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)
        
        # 업로드된 파일들 확인
        if 'label' not in request.files or 'image' not in request.files:
            return jsonify({
                "success": False,
                "message": "CSV 파일(label) 및 ZIP 파일(image)이 모두 필요합니다."
            }), 400
            
        label_file = request.files['label']
        image_file = request.files['image']
        
        if label_file.filename == '' or image_file.filename == '':
            return jsonify({
                "success": False,
                "message": "파일이 선택되지 않았습니다."
            }), 400
        
        # 파일 확장자 검증
        if not (label_file.filename.lower().endswith('.csv')):
            return jsonify({
                "success": False,
                "message": "CSV 파일만 업로드 가능합니다."
            }), 400
            
        if not (image_file.filename.lower().endswith('.zip')):
            return jsonify({
                "success": False,
                "message": "ZIP 파일만 업로드 가능합니다."
            }), 400
        
        # 안전한 파일명 생성
        csv_filename = secure_filename(label_file.filename)
        zip_filename = secure_filename(image_file.filename)
        
        # 파일 저장 경로
        csv_path = os.path.join(csv_dir, csv_filename)
        zip_path = os.path.join(image_dir, zip_filename)
        
        # 파일 저장
        label_file.save(csv_path)
        image_file.save(zip_path)
        
        # ZIP 파일 유효성 검사
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_count = len(zip_ref.namelist())
        except zipfile.BadZipFile:
            # 유효하지 않은 ZIP 파일인 경우 삭제
            os.remove(zip_path)
            if os.path.exists(csv_path):
                os.remove(csv_path)
            return jsonify({
                "success": False,
                "message": "유효하지 않은 ZIP 파일입니다."
            }), 400
        
        # CSV 파일 라인 수 계산
        csv_line_count = 0
        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                csv_line_count = sum(1 for line in f) - 1  # 헤더 제외
        except Exception as e:
            csv_line_count = 0
        
        # 성공 응답
        return jsonify({
            "success": True,
            "message": "파일이 성공적으로 업로드되었습니다.",
            "data": {
                "csv": {
                    "filename": csv_filename,
                    "path": csv_path,
                    "size": os.path.getsize(csv_path),
                    "lines": csv_line_count
                },
                "image": {
                    "filename": zip_filename,
                    "path": zip_path,
                    "size": os.path.getsize(zip_path),
                    "file_count": file_count
                },
                "uploaded_at": datetime.now().isoformat(),
                "base_path": base_path
            }
        }), 200
        
    except Exception as e:
        logger.exception(f"파일 업로드 오류: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "time": datetime.now().strftime("%H:%M:%S")
        }), 500


# 특정 육류의 기본 정보 생성 및 수정
@add_api.route("/", methods=["POST", "PATCH"])
def add_specific_meat_data():
    db_session = current_app.db_session
    s3_conn = current_app.s3_conn
    firestore_conn = current_app.firestore_conn
    try:
        data = request.get_json()
        meat_id = data.get("meatId")
        meat = get_meat(db_session, meat_id)
        
        if request.method == "POST": # 기본 원육 정보 생성(POST)
            if meat:
                return jsonify({"msg": "Already Existing Meat"}), 400
                
            new_meat_id = create_specific_std_meat_data(
                db_session, s3_conn, firestore_conn, data, meat_id, is_post=1
            )
            if new_meat_id:
                create_raw_meat_deep_aging_info(db_session, new_meat_id, seqno=0)
                return jsonify({"msg": "Success to store Raw Meat and Initial DeepAging Information"}), 200
                
        else: # 기본 원육 정보 수정(PATCH)
            if not meat:
                return jsonify({"msg": "Not Existing Meat"}), 404

            updated_meat_id = create_specific_std_meat_data(
                db_session, s3_conn, firestore_conn, data, meat_id, is_post=0
            )
            if updated_meat_id:
                return jsonify({"msg": f"Success to update Raw Meat {updated_meat_id} Information"}), 200
            else:
                return jsonify({"msg": f"Already Confirmed Meat Data"}), 400

    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 딥 에이징 이력 생성
@add_api.route("/deep-aging-data", methods=["POST", "PATCH"])
def add_specific_deepAging_data():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        if request.method == "POST":
            if not (data["meatId"] and data["seqno"] and data["deepAging"]):
                return jsonify({"msg": "Failed to Create Deep Aging Data"}), 400
            deep_aging_id = create_specific_deep_aging_data(db_session, data, is_post=1)
            if deep_aging_id:
                return jsonify({"msg": f"Success to Create Deep Aging Data {deep_aging_id}"}), 200
            elif deep_aging_id is None:
                return jsonify({"msg": f"Meat {data['meatId']} Does NOT Exists"}), 404
            else:
                return jsonify({"msg": f"Seqno {data['seqno']} Deep Aging Info. Already Exists"}), 400
        elif request.method == "PATCH":
            if not (data["meatId"] and data["seqno"] is not None and data["isCompleted"] is not None):
                return jsonify({"msg": "Failed to Patch Deep Aging Data"}), 400
            deep_aging_id = create_specific_deep_aging_data(db_session, data, is_post=0)
            if deep_aging_id:
                return jsonify({"msg": f"Success to Patch Deep Aging Data {deep_aging_id}"}), 200
            elif deep_aging_id is None:
                return jsonify({"msg": f"Meat {data['meatId']} Does NOT Exists"}), 404
            else:
                return jsonify({"msg": f"Seqno {data['seqno']} Does NOT Exists"}), 404

    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 관능 검사 결과 생성 및 수정
@add_api.route("/sensory-eval", methods=["POST", "PATCH"])
def add_specific_sensory_eval():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        s3_conn = current_app.s3_conn
        firestore_conn = current_app.firestore_conn
        
        if request.method == "POST":
            sensory_data = create_specific_sensory_eval(db_session, s3_conn, firestore_conn, data, is_post=1)
        else:
            sensory_data = create_specific_sensory_eval(db_session, s3_conn, firestore_conn, data, is_post=0)
        return jsonify({"msg": sensory_data["msg"]}), sensory_data["code"]
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 가열육 관능 검사 결과 생성 및 수정
@add_api.route("/heatedmeat-eval", methods=["POST", "PATCH"])
def add_specific_heatedmeat_sensory_eval():
    try:
        db_session = current_app.db_session
        firestore_conn = current_app.firestore_conn
        s3_conn = current_app.s3_conn
        data = request.get_json()
        if request.method == "POST":
            is_post = True
            for key in ("meatId", "seqno", "userId", "imgAdded","heatedmeatSensoryData"):
                if key not in data.keys() or data[key] is None:
                    return jsonify({"msg": "Failed to POST Heatedmeat Sensory Data"}), 400
        elif request.method == "PATCH":
            is_post = False
            for key in ("meatId", "seqno", "imgAdded", "heatedmeatSensoryData"):
                if key not in data.keys() or data[key] is None:
                    return jsonify({"msg": "Failed to PATCH Heatedmeat Sensory Data"}), 400
                
        heatedmeat_sensory_data = create_specific_heatedmeat_seonsory_eval(db_session, firestore_conn, s3_conn, data, is_post)
        return jsonify({"msg": heatedmeat_sensory_data["msg"]}), heatedmeat_sensory_data["code"]
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 특정 육류의 실험실 데이터 생성 및 수정
@add_api.route("/probexpt-data", methods=["POST", "PATCH"])
def add_specific_probexpt_data():
    try:
        db_session = current_app.db_session
        data = request.get_json()
        if request.method == "POST":
            is_post = True
            for key in ("meatId", "seqno", "isHeated", "userId", "probexptData"):
                if key not in data.keys() or data[key] is None:
                    return jsonify({"msg": "Failed to POST Probexpt Data"}), 400

        elif request.method == "PATCH":
            is_post = False
            for key in ("meatId", "seqno", "isHeated", "probexptData"):
                if key not in data.keys() or data[key] is None:
                    return jsonify({"msg": "Failed to PATCH Probexpt Data"}), 400

        probexpt_data = create_specific_probexpt_data(db_session, data, is_post)
        return jsonify({"msg": probexpt_data["msg"]}), probexpt_data["code"]
    except Exception as e:
        logger.exception(str(e))
        return (
            jsonify(
                {"msg": "Server Error", "time": datetime.now().strftime("%H:%M:%S")}
            ),
            500,
        )


# 예측 데이터 생성 및 수정
@add_api.route("/predict-data", methods=["GET", "POST"])
def add_specific_predict_data():
    try:
        if request.method == "POST":
            db_session = current_app.db_session
            data = request.get_json()
            if data:
                return _addSpecificPredictData(db_session, data)
            else:
                return jsonify({"msg": "No data in Request."}), 401
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

# 간단한 테스트용 Flask 서버
import os
import zipfile
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

@app.route("/")
def hello_world():
    return "Test Flask Server is Running!"

@app.route("/meat/add/upload/data", methods=["POST"])
def upload_bulk_data():
    """
    테스트용 데이터 업로드 엔드포인트
    """
    try:
        # 기본 경로 설정
        base_path = request.form.get('basePath', './uploads')
        csv_folder = request.form.get('csvPath', 'label')
        image_folder = request.form.get('imagePath', 'image')
        data_format = request.form.get('dataFormat', 'HSI')  # 데이터 형식 받기
        
        # 전체 경로 생성
        csv_dir = os.path.join(base_path, csv_folder)
        image_dir = os.path.join(base_path, image_folder)
        
        # 디렉토리 생성 (존재하지 않는 경우)
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(image_dir, exist_ok=True)
        
        print(f"CSV 저장 경로: {csv_dir}")
        print(f"이미지 저장 경로: {image_dir}")
        print(f"데이터 형식: {data_format}")
        
        # 업로드된 파일들 확인
        if 'label' not in request.files or 'image' not in request.files:
            return jsonify({
                "success": False,
                "message": "CSV 파일(label) 및 ZIP 파일(image)이 모두 필요합니다."
            }), 400
            
        label_file = request.files['label']
        image_file = request.files['image']
        
        print(f"받은 파일들: label={label_file.filename}, image={image_file.filename}")
        
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
        
        # 안전한 파일명 생성 (원본 파일명 유지)
        csv_filename = secure_filename(label_file.filename)
        zip_filename = secure_filename(image_file.filename)
        
        # 파일 저장 경로
        csv_path = os.path.join(csv_dir, csv_filename)
        zip_path = os.path.join(image_dir, zip_filename)
        
        print(f"저장할 경로: CSV={csv_path}, ZIP={zip_path}")
        
        # 덮어쓰기 옵션 확인
        overwrite = request.form.get('overwrite', 'false').lower() == 'true'
        
        # 중복 파일 확인 (덮어쓰기 옵션이 false인 경우만)
        if not overwrite and (os.path.exists(csv_path) or os.path.exists(zip_path)):
            existing_files = []
            if os.path.exists(csv_path):
                existing_files.append(f"CSV: {csv_filename}")
            if os.path.exists(zip_path):
                existing_files.append(f"ZIP: {zip_filename}")
            
            return jsonify({
                "success": False,
                "message": f"이미 존재하는 파일이 있습니다.\n{', '.join(existing_files)}\n기존 파일을 삭제한 후 다시 시도해주세요."
            }), 409  # 409 Conflict
        
        # 덮어쓰기 로그
        if overwrite:
            print("덮어쓰기 모드: 기존 파일을 교체합니다.")
        
        # 파일 저장
        label_file.save(csv_path)
        image_file.save(zip_path)
        
        print("파일 저장 완료")
        
        # ZIP 파일 유효성 검사
        file_count = 0
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                file_count = len(zip_ref.namelist())
                print(f"ZIP 파일 내 파일 수: {file_count}")
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
                print(f"CSV 라인 수: {csv_line_count}")
        except Exception as e:
            print(f"CSV 라인 수 계산 오류: {e}")
            csv_line_count = 0
        
        # 성공 응답
        response_data = {
            "success": True,
            "message": f"파일이 성공적으로 업로드되었습니다. (데이터 형식: {data_format})",
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
                "dataFormat": data_format,
                "uploaded_at": datetime.now().isoformat(),
                "base_path": base_path
            }
        }
        
        print("업로드 성공:", response_data)
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"파일 업로드 오류: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"서버 오류: {str(e)}",
            "time": datetime.now().strftime("%H:%M:%S")
        }), 500

if __name__ == "__main__":
    print("테스트 Flask 서버를 시작합니다...")
    print("업로드 디렉토리를 생성합니다...")
    os.makedirs("./uploads/label", exist_ok=True)
    os.makedirs("./uploads/image", exist_ok=True)
    print("서버 URL: http://localhost:8080")
    app.run(debug=True, port=8080, host="0.0.0.0")

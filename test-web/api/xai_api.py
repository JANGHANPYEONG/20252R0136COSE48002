"""
XAI 분석 API
"""

import os
import subprocess
import json
import shutil
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

xai_bp = Blueprint('xai', __name__)

# XAI 관련 경로 설정
XAI_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'XAI')
HEATMAP_DIR = os.path.join(XAI_DIR, 'image_heatmap')
NOTEBOOK_PATH = os.path.join(XAI_DIR, 'XAI.ipynb')
PYTHON_SCRIPT = os.path.join(XAI_DIR, 'xai_analysis.py')

def ensure_directories():
    """필요한 디렉토리 생성"""
    os.makedirs(XAI_DIR, exist_ok=True)
    os.makedirs(HEATMAP_DIR, exist_ok=True)

@xai_bp.route('/run-analysis', methods=['POST'])
def run_xai_analysis():
    """XAI 분석 실행"""
    try:
        ensure_directories()
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '데이터가 필요합니다'}), 400
            
        # 분석할 이미지 폴더 경로
        image_folder = data.get('imagePath')
        model_path = data.get('modelPath', './best_model.pt')
        
        if not image_folder:
            return jsonify({'error': '이미지 폴더 경로가 필요합니다'}), 400
            
        if not os.path.exists(image_folder):
            return jsonify({'error': f'이미지 폴더를 찾을 수 없습니다: {image_folder}'}), 400
            
        # 기존 heat map 이미지 정리
        if os.path.exists(HEATMAP_DIR):
            for file in os.listdir(HEATMAP_DIR):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    os.remove(os.path.join(HEATMAP_DIR, file))
                    
        # Python 스크립트 실행을 위한 환경변수 설정
        env = os.environ.copy()
        env['IMG_FOLDER'] = image_folder
        env['MODEL_PATH'] = model_path
        env['OUTPUT_DIR'] = HEATMAP_DIR
        
        # XAI 분석 실행
        # Jupyter notebook을 Python 스크립트로 변환하여 실행
        convert_cmd = [
            'jupyter', 'nbconvert', 
            '--to', 'python', 
            '--stdout', 
            NOTEBOOK_PATH
        ]
        
        print(f"[INFO] XAI 분석 시작...")
        print(f"[INFO] 이미지 폴더: {image_folder}")
        print(f"[INFO] 모델 경로: {model_path}")
        print(f"[INFO] 출력 폴더: {HEATMAP_DIR}")
        
        # notebook을 python 스크립트로 변환
        convert_result = subprocess.run(
            convert_cmd, 
            capture_output=True, 
            text=True,
            cwd=XAI_DIR
        )
        
        if convert_result.returncode != 0:
            return jsonify({
                'error': 'Notebook 변환 실패',
                'details': convert_result.stderr
            }), 500
            
        # Python 스크립트 저장
        with open(PYTHON_SCRIPT, 'w', encoding='utf-8') as f:
            # CONFIG 부분 수정
            script_content = convert_result.stdout
            script_content = script_content.replace(
                'IMG_FOLDER  = "./image"',
                f'IMG_FOLDER  = r"{image_folder}"'
            )
            script_content = script_content.replace(
                'MODEL_PATH  = "./best_model.pt"',
                f'MODEL_PATH  = r"{model_path}"'
            )
            script_content = script_content.replace(
                'OUTPUT_DIR  = "./image_heatmap"',
                f'OUTPUT_DIR  = r"{HEATMAP_DIR}"'
            )
            f.write(script_content)
        
        # Python 스크립트 실행
        python_cmd = ['python', PYTHON_SCRIPT]
        
        result = subprocess.run(
            python_cmd,
            capture_output=True,
            text=True,
            cwd=XAI_DIR,
            env=env,
            timeout=300  # 5분 타임아웃
        )
        
        if result.returncode != 0:
            return jsonify({
                'error': 'XAI 분석 실행 실패',
                'details': result.stderr,
                'stdout': result.stdout
            }), 500
            
        # 생성된 heat map 이미지 목록 조회
        heatmap_files = []
        if os.path.exists(HEATMAP_DIR):
            for file in os.listdir(HEATMAP_DIR):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    heatmap_files.append({
                        'filename': file,
                        'path': os.path.join(HEATMAP_DIR, file),
                        'url': f'/xai/heatmap/{file}'
                    })
        
        # 정리
        if os.path.exists(PYTHON_SCRIPT):
            os.remove(PYTHON_SCRIPT)
            
        return jsonify({
            'success': True,
            'message': 'XAI 분석이 완료되었습니다',
            'heatmapFiles': heatmap_files,
            'outputDir': HEATMAP_DIR,
            'stdout': result.stdout
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'XAI 분석이 시간 초과되었습니다 (5분)'}), 500
    except Exception as e:
        return jsonify({
            'error': f'XAI 분석 중 오류가 발생했습니다: {str(e)}'
        }), 500

@xai_bp.route('/heatmap/<filename>')
def serve_heatmap(filename):
    """Heat map 이미지 서빙"""
    try:
        filename = secure_filename(filename)
        file_path = os.path.join(HEATMAP_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다'}), 404
            
        from flask import send_file
        return send_file(file_path)
        
    except Exception as e:
        return jsonify({'error': f'파일 서빙 오류: {str(e)}'}), 500

@xai_bp.route('/heatmap-list')
def get_heatmap_list():
    """생성된 heat map 목록 조회"""
    try:
        ensure_directories()
        
        heatmap_files = []
        if os.path.exists(HEATMAP_DIR):
            for file in sorted(os.listdir(HEATMAP_DIR)):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(HEATMAP_DIR, file)
                    heatmap_files.append({
                        'filename': file,
                        'path': file_path,
                        'url': f'/xai/heatmap/{file}',
                        'size': os.path.getsize(file_path),
                        'modified': os.path.getmtime(file_path)
                    })
        
        return jsonify({
            'success': True,
            'heatmapFiles': heatmap_files,
            'total': len(heatmap_files)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Heat map 목록 조회 오류: {str(e)}'
        }), 500

@xai_bp.route('/clear-heatmaps', methods=['POST'])
def clear_heatmaps():
    """기존 heat map 파일 삭제"""
    try:
        if os.path.exists(HEATMAP_DIR):
            deleted_count = 0
            for file in os.listdir(HEATMAP_DIR):
                if file.endswith(('.png', '.jpg', '.jpeg')):
                    os.remove(os.path.join(HEATMAP_DIR, file))
                    deleted_count += 1
                    
            return jsonify({
                'success': True,
                'message': f'{deleted_count}개의 heat map 파일이 삭제되었습니다',
                'deletedCount': deleted_count
            })
        else:
            return jsonify({
                'success': True,
                'message': '삭제할 파일이 없습니다',
                'deletedCount': 0
            })
            
    except Exception as e:
        return jsonify({
            'error': f'Heat map 삭제 오류: {str(e)}'
        }), 500

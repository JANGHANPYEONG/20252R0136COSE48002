from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Literal, List
from datetime import datetime
import asyncio
import time
import subprocess
import json
import os
import tempfile

router = APIRouter()


# Pydantic 모델 정의
class PredictRequest(BaseModel):
    model_uri: str  # MLflow run_id 또는 모델 디렉토리 경로
    data_path: str  # 예측할 데이터 경로
    input_type: Literal["image", "vector"]

class PredictResponse(BaseModel):
    message: str
    prediction_result: Dict
    elapsed_time: float
    created_at: datetime


# 비동기 예측 함수
async def run_prediction(model_uri: str, data_path: str, input_type: str) -> Dict:
    """
    비동기로 예측을 실행하는 함수 (스크립트 실행 방식)
    """
    try:
        print(f"Starting prediction with model: {model_uri}, data: {data_path}, type: {input_type}")
        
        # MLflow run ID 형태 검증 및 정보 출력
        if len(model_uri) == 32:
            print(f"Detected MLflow run ID: {model_uri}")
        elif model_uri.startswith('mlflow://'):
            print(f"Detected MLflow URI: {model_uri}")
        else:
            print(f"Using local model path: {model_uri}")
        
        # data_path가 여러 경로인 경우 처리
        if ',' in data_path:
            data_paths = [path.strip() for path in data_path.split(',')]
            print(f"Multiple data paths detected: {len(data_paths)} files")
        else:
            data_paths = [data_path.strip()]
            print(f"Single data path: {data_path}")
        
        # 파일 존재 여부 확인
        for i, path in enumerate(data_paths):
            if not os.path.exists(path):
                raise FileNotFoundError(f"Data file not found: {path}")
            print(f"Data file {i+1} exists: {path}")
        
        # 스크립트 경로 설정 (동적 경로 계산)
        # 현재 파일(predict.py)에서 프로젝트 루트까지 이동: app/routers/predict.py -> ../../
        current_dir = os.path.dirname(os.path.abspath(__file__))  # app/routers
        project_root = os.path.dirname(os.path.dirname(current_dir))  # test-ML-backend
        training_hsi_dir = os.path.join(project_root, "training_HSI")
        
        if input_type == "image":
            script_path = os.path.join(training_hsi_dir, "predict_hsi.py")
        elif input_type == "vector":
            script_path = os.path.join(training_hsi_dir, "predict_vector.py")
        else:
            raise ValueError(f"Unsupported input_type: {input_type}")
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Prediction script not found: {script_path}")
        
        print(f"Using script: {script_path}")
        
        # 임시 결과 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_result_path = temp_file.name
        
        try:
            # 명령어 구성
            cmd = ["python", script_path]
            
            # 모델 로딩 방식 결정 (run_id vs model_dir)
            if len(model_uri) == 32:
                cmd.extend(["--run_id", model_uri])
            else:
                cmd.extend(["--model_dir", model_uri])
            
            # 데이터 경로들 추가 (input_type에 따라 파라미터명 다름)
            if input_type == "image":
                cmd.extend(["--image_paths"] + data_paths)
            elif input_type == "vector":
                cmd.extend(["--data_paths"] + data_paths)
            
            # 결과 파일 경로 추가
            cmd.extend(["--output", temp_result_path])
            
            print(f"Executing command: {' '.join(cmd)}")
            
            # 스크립트 실행 (비동기)
            print("Starting prediction script...")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=os.path.dirname(script_path)
            )
            
            stdout, stderr = await process.communicate()
            
            # 프로세스 결과 확인
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                print(f"Script execution failed with return code {process.returncode}")
                print(f"Error output: {error_msg}")
                raise RuntimeError(f"Prediction script failed: {error_msg}")
            
            # 표준 출력 로그 출력
            if stdout:
                stdout_text = stdout.decode('utf-8')
                print("Script output:")
                print(stdout_text)
            
            # 에러 출력도 확인
            if stderr:
                stderr_text = stderr.decode('utf-8')
                print("Script stderr:")
                print(stderr_text)
            
            # 결과 파일 읽기
            if not os.path.exists(temp_result_path):
                raise FileNotFoundError(f"Result file was not created: {temp_result_path}")
            
            # 파일 크기 확인
            file_size = os.path.getsize(temp_result_path)
            print(f"Result file size: {file_size} bytes")
            
            if file_size == 0:
                raise ValueError(f"Result file is empty: {temp_result_path}")
            
            # 파일 내용 확인 후 JSON 파싱
            with open(temp_result_path, 'r') as f:
                file_content = f.read()
                print(f"Result file content preview: {file_content[:200]}")
                
                if not file_content.strip():
                    raise ValueError("Result file is empty or contains only whitespace")
                
                try:
                    prediction_result = json.loads(file_content)
                except json.JSONDecodeError as e:
                    print(f"JSON parsing error: {e}")
                    print(f"File content: {file_content}")
                    raise ValueError(f"Invalid JSON in result file: {e}")
            
            print(f"Prediction completed successfully")
            print(f"Result: {prediction_result}")
            
            return prediction_result
            
        finally:
            # 임시 파일 정리
            if os.path.exists(temp_result_path):
                os.unlink(temp_result_path)
                print(f"Cleaned up temporary result file: {temp_result_path}")
        
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"Error during prediction: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise e


@router.post("/", response_model=PredictResponse)
async def predict(request: PredictRequest):
    """
    ML 모델 예측을 실행하는 엔드포인트
    """
    try:
        start_time = time.time()
        
        # 입력 검증
        if request.input_type not in ["image", "vector"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid input_type: {request.input_type}. Must be 'image' or 'vector'"
            )
        
        if not request.model_uri.strip():
            raise HTTPException(
                status_code=400,
                detail="model_uri cannot be empty"
            )
        
        if not request.data_path.strip():
            raise HTTPException(
                status_code=400,
                detail="data_path cannot be empty"
            )
        
        print(f"Prediction request received: model={request.model_uri}, type={request.input_type}")
        
        # 예측 실행
        prediction_result = await run_prediction(
            request.model_uri, 
            request.data_path, 
            request.input_type
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"Prediction completed in {elapsed_time:.2f} seconds")
        
        return PredictResponse(
            message=f"Prediction completed successfully for {request.input_type} model",
            prediction_result=prediction_result,
            elapsed_time=elapsed_time,
            created_at=datetime.now()
        )
        
    except HTTPException:
        # HTTPException은 그대로 재발생
        raise
    except Exception as e:
        print(f"Unexpected error in predict endpoint: {type(e).__name__}: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
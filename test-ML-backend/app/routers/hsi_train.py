from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal
import json
import tempfile
import re
import os
import csv
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult
import boto3
from botocore.exceptions import ClientError
import pandas as pd

from training_HSI.train_HSI_2d import main as train_hsi_2d

# Celery 및 APIRouter 설정
celery_app = Celery(
    "hsi_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# GPU 환경 최적화 설정
celery_app.conf.update(
    worker_prefetch_multiplier=1,  # GPU 메모리 절약
    task_acks_late=True,          # 작업 완료 후 ACK
    worker_max_tasks_per_child=None, # worker 재시작 비활성화 (solo pool 안정성 향상)
)

router = APIRouter()


# Pydantic 모델 정의
class HSITrainRequest(BaseModel):
    id_list: List[str]  # HSI 이미지 ID 리스트

class HSITrainResponse(BaseModel):
    message: str
    train_id: str
    process_pid: Optional[int] = None
    created_at: datetime

class HSITrainStatus(BaseModel):
    train_id: str
    status: Literal["PENDING", "TRAINING", "SUCCESS", "FAILURE", "REVOKED"]
    elapsed_time: Optional[float] = None  # 실행 시간 (초)
    error_message: Optional[str] = None
    result: Optional[Dict] = None


def get_s3_client():
    """S3 클라이언트를 생성합니다."""
    try:
        return boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
    except Exception as e:
        print(f"Failed to create S3 client: {e}")
        return None


def download_image_from_s3(s3_client, bucket_name: str, s3_key: str, local_path: str) -> bool:
    """S3에서 이미지를 다운로드합니다."""
    try:
        # 디렉토리 생성
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        
        # 이미지 다운로드
        s3_client.download_file(bucket_name, s3_key, local_path)
        print(f"Downloaded {s3_key} to {local_path}")
        return True
    except ClientError as e:
        print(f"Failed to download {s3_key}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error downloading {s3_key}: {e}")
        return False


def create_csv_file(id_list: List[str], cache_dir: str) -> str:
    """
    HSI 학습을 위한 CSV 파일을 생성합니다.
    
    Args:
        id_list: HSI 이미지 ID 리스트
        cache_dir: 이미지 캐시 디렉토리
        
    Returns:
        str: 생성된 CSV 파일 경로
    """
    # 임시 CSV 파일 생성
    csv_fd, csv_path = tempfile.mkstemp(suffix='.csv')
    os.close(csv_fd)
    
    # 데이터베이스 연결 및 데이터 조회
    from app.db.database import get_db
    from app.db.db_model import HSISensoryEval, HSIImagesBands, SpectralInfo
    
    db = next(get_db())
    
    try:
        # 1. spectral_info에서 모든 파장 조회
        spectral_infos = db.query(SpectralInfo).order_by(SpectralInfo.spectral_index).all()
        wavelengths = [info.wavelength_nm for info in spectral_infos]
        
        # 2. column_config.json 기반으로 CSV 헤더 생성
        headers = ['id_column']
        
        # 라벨 컬럼 추가 (regression + classification)
        label_columns = [
            "Marbling", "Meat Color", "Texture", "Surface Moisture", "Total",
            "GRADE_3", "GRADE_2", "GRADE_1", "GRADE_1+", "GRADE_1++"
        ]
        headers.extend(label_columns)
        
        # 파장 컬럼 추가
        headers.extend([str(w) for w in wavelengths])
        
        # 3. CSV 파일에 헤더 작성
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            
            # 4. 각 ID에 대해 데이터 행 생성
            for meat_id in id_list:
                # hsi_sensory_eval에서 해당 ID의 모든 레코드 조회
                hsi_records = db.query(HSISensoryEval).filter(
                    HSISensoryEval.id == meat_id
                ).all()
                
                for record in hsi_records:
                    # ID 컬럼 생성: {id}_{seqno}_{isRefrigerated}
                    row_id = f"{record.id}_{record.seqno}_{str(record.isRefrigerated).lower()}"
                    
                    # 라벨 데이터
                    row_data = [row_id]
                    
                    # 회귀 라벨 (1-10 스케일)
                    regression_labels = [
                        record.marbling or 0,
                        record.color or 0,
                        record.texture or 0,
                        record.surfaceMoisture or 0,
                        record.overall or 0
                    ]
                    row_data.extend(regression_labels)
                    
                    # 분류 라벨 (one-hot encoding)
                    # GRADE_3, GRADE_2, GRADE_1, GRADE_1+, GRADE_1++
                    grade_mapping = {
                        0: [1, 0, 0, 0, 0],  # GRADE_3
                        1: [0, 1, 0, 0, 0],  # GRADE_2
                        2: [0, 0, 1, 0, 0],  # GRADE_1
                        3: [0, 0, 0, 1, 0],  # GRADE_1+
                        4: [0, 0, 0, 0, 1]   # GRADE_1++
                    }
                    
                    if record.xai_gradeNum is not None:
                        grade_labels = grade_mapping.get(record.xai_gradeNum, [0, 0, 0, 0, 0])
                    else:
                        grade_labels = [0, 0, 0, 0, 0]
                    
                    row_data.extend(grade_labels)
                    
                    # 5. 이미지 경로 처리
                    s3_client = get_s3_client()
                    bucket_name = os.getenv('S3_BUCKET_NAME', 'deeplant-bucket')
                    
                    for wavelength in wavelengths:
                        # hsi_images_bands에서 해당 파장의 이미지 파일명 조회
                        spectral_info = next((s for s in spectral_infos if s.wavelength_nm == wavelength), None)
                        if not spectral_info:
                            row_data.append("")
                            continue
                        
                        hsi_image = db.query(HSIImagesBands).filter(
                            HSIImagesBands.id == record.id,
                            HSIImagesBands.seqno == record.seqno,
                            HSIImagesBands.isRefrigerated == record.isRefrigerated,
                            HSIImagesBands.spectral_index == spectral_info.spectral_index
                        ).first()
                        
                        if hsi_image and hsi_image.filename:
                            # S3에서 로컬 캐시로 이미지 다운로드
                            s3_key = f"train_dataset/HSI/{hsi_image.filename}"
                            cache_filename = f"{row_id}_{wavelength}.png"
                            local_cache_path = os.path.join(cache_dir, cache_filename)
                            
                            if s3_client:
                                if download_image_from_s3(s3_client, bucket_name, s3_key, local_cache_path):
                                    row_data.append(local_cache_path)
                                else:
                                    row_data.append("")
                            else:
                                row_data.append("")
                        else:
                            row_data.append("")
                    
                    # CSV에 행 작성
                    writer.writerow(row_data)
        
        print(f"CSV file created successfully: {csv_path}")
        return csv_path
        
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        raise
    finally:
        db.close()


def create_config_file(csv_path: str) -> str:
    """
    HSI 학습을 위한 설정 파일을 생성합니다.
    
    Args:
        csv_path: 생성된 CSV 파일 경로
        
    Returns:
        str: 생성된 설정 파일 경로
    """
    # 임시 설정 파일 생성
    config_fd, config_path = tempfile.mkstemp(suffix='.json')
    os.close(config_fd)
    
    # mlflow_config.json에서 experiment_name 가져오기
    mlflow_config_path = "training_HSI/configs/mlflow_config.json"
    experiment_name = "HSI_Model_Training"  # 기본값
    
    try:
        with open(mlflow_config_path, 'r') as f:
            mlflow_config = json.load(f)
            experiment_name = mlflow_config.get('experiment_name', experiment_name)
    except Exception as e:
        print(f"Warning: Could not read mlflow_config.json: {e}")
    
    # 설정 파일 내용 생성
    config = {
        "model": {
            "file": "models/HSI_image/hsi_resnet.py",
            "num_classes": 5
        },
        "data": {
            "csv": csv_path,
            "column_config": "training_HSI/configs/column_config.json",
            "batch_size": 16,
            "num_workers": 4,
            "val_split": 0.2,
            "test_split": 0.1,
            "crop_size": [224, 224],
            "use_flip": True,
            "use_rotation": True,
            "use_noise": True,
            "use_brightness_contrast": True,
            "scaler_mode": "normalized"
        },
        "train": {
            "epochs": 100,
            "optimizer": "adam",
            "lr": 0.001,
            "scheduler": "cosine",
            "save_interval": 10
        },
        "seed": 42,
        "plot_keys": ["cls_f1_score", "reg_r2", "combined_score"]
    }
    
    # 설정 파일 작성
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Config file created successfully: {config_path}")
    return config_path


def create_training_files(id_list: List[str]) -> tuple:
    """
    학습에 필요한 CSV 파일과 설정 파일을 생성합니다.
    
    Args:
        id_list: HSI 이미지 ID 리스트
        
    Returns:
        tuple: (csv_path, config_path)
    """
    try:
        # 캐시 디렉토리 생성
        cache_dir = "/tmp/hsi_train_image_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        # 1. CSV 파일 생성
        csv_path = create_csv_file(id_list, cache_dir)
        
        # 2. 설정 파일 생성
        config_path = create_config_file(csv_path)
        
        return csv_path, config_path
        
    except Exception as e:
        print(f"Error creating training files: {e}")
        raise


# Celery 백그라운드에서 HSI 학습을 실행하는 함수
@celery_app.task(bind=True)
def run_hsi_train_task(self, id_list: List[str]):
    import time
    import os
    import subprocess
    import sys
    
    try:
        # 시작 시간 기록
        start_time = time.time()
        
        # CSV 및 설정 파일 생성
        csv_path, config_path = create_training_files(id_list)
        
        # subprocess로 학습 프로세스 실행
        training_dir = "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI"
        
        # subprocess로 학습 실행 (Worker와 분리된 별도 프로세스)
        process = subprocess.Popen(
            [sys.executable, "train_HSI_2d.py", '--config', config_path],
            cwd=training_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 학습 상태 업데이트: TRAINING (subprocess PID 포함)
        self.update_state(state='TRAINING', meta={
            'input_type': 'hsi_image',
            'process_pid': process.pid,  # ← 이제 별도 프로세스 PID
            'start_time': start_time
        })
        
        try:
            print(f"Starting HSI training with config: {config_path}")
            print(f"Training subprocess PID: {process.pid}")
            
            # 프로세스 완료 대기
            stdout, stderr = process.communicate()
            
            # 프로세스 종료 코드 확인
            if process.returncode != 0:
                error_message = f"Training process failed with return code {process.returncode}\nSTDERR: {stderr}\nSTDOUT: {stdout}"
                raise Exception(error_message)
            
            # stdout에서 MLflow experiment ID, run ID 추출
            mlflow_experiment_id = None
            mlflow_run_id = None

            if stdout:
                import re
                lines = stdout.strip().split('\n')
                
                # 여러 패턴으로 MLflow run ID 추출 시도
                patterns = [
                    r'[a-f0-9]{32}',  # 32자리 16진수
                    r'MLflow run ID: ([a-f0-9]{32})',  # 명시적 표시
                    r'run_id=([a-f0-9]{32})',  # 파라미터 형태
                ]
                
                for line in lines:
                    line = line.strip()
                    
                    # 32자리 16진수 문자열 패턴으로 MLflow experiment ID, run ID 추출
                    if "Experiment ID" in line:
                        pattern = r"Experiment ID:\s*(\d+),\s*Run ID:\s*([a-f0-9]+)"
                        match = re.search(pattern, line)
                        if match:
                            mlflow_experiment_id, mlflow_run_id = match.groups()
                            break
                    
                    # 여러 패턴으로 MLflow run ID 추출 시도 (experiment ID가 없는 경우)
                    if not mlflow_run_id:
                        for pattern in patterns:
                            match = re.search(pattern, line)
                            if match:
                                mlflow_run_id = match.group(1) if len(match.groups()) > 0 else match.group()
                                break
                        if mlflow_run_id:
                            break
            
            # MLflow run ID를 찾지 못한 경우 로그 출력
            if not mlflow_run_id:
                print("Warning: MLflow run ID not found in stdout")
                print("Stdout content:", stdout[:500])  # 처음 500자만 출력
            else:
                print(f"Training completed with experiment ID: {mlflow_experiment_id}, run ID: {mlflow_run_id}")
            
            # 완료 시간 계산
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 학습 완료 - SUCCESS 상태로 업데이트
            self.update_state(state='SUCCESS', meta={
                'mlflow_experiment_id': mlflow_experiment_id,
                'mlflow_run_id': mlflow_run_id,
                'elapsed_time': elapsed_time
            })
            
            # 최종 결과 반환
            return {'mlflow_experiment_id': mlflow_experiment_id, 'mlflow_run_id': mlflow_run_id}

        finally:
            # 임시 파일들 삭제
            if os.path.exists(config_path):
                os.remove(config_path)
            if os.path.exists(csv_path):
                os.remove(csv_path)
        
    except Exception as e:
        # Celery가 자동으로 FAILURE 상태로 처리하도록 예외를 다시 발생시킴
        # 커스텀 에러 정보는 예외 메시지에 포함
        import traceback
        error_message = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"HSI Training failed: {error_message}")
        
        # 예외를 다시 발생시켜서 Celery가 자동으로 FAILURE 처리하도록 함
        raise Exception(error_message)


@router.post("/", response_model=HSITrainResponse)
async def start_hsi_train(request: HSITrainRequest):
    """
    HSI 이미지 모델 학습을 시작하는 엔드포인트
    """
    try:
        if not request.id_list:
            raise HTTPException(status_code=400, detail="ID list is required")
        
        # Celery 작업 시작
        task = run_hsi_train_task.apply_async(args=[request.id_list])
        
        # 작업이 시작될 때까지 잠시 기다려서 PID 가져오기
        import time
        process_pid = None
        for _ in range(10):  # 최대 1초 대기
            result = AsyncResult(task.id, app=celery_app)
            if result.state == 'TRAINING' and result.info:
                process_pid = result.info.get('process_pid')
                break
            time.sleep(0.1)
        
        return HSITrainResponse(
            message=f"HSI training started in background for {len(request.id_list)} images",
            train_id=task.id,
            process_pid=process_pid,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_id}", response_model=HSITrainStatus)
async def get_hsi_train_status(train_id: str):
    """
    HSI 학습 상태를 확인하는 엔드포인트
    """
    import time
    
    try:
        result = AsyncResult(train_id, app=celery_app)
        
        # 기본 상태 정보 (Redis에서 가져온 데이터로 업데이트됨)
        status_info = {
            "train_id": train_id,
            "status": result.state,
            "elapsed_time": None,
            "error_message": None,
            "result": None
        }
        
        if result.state == 'PENDING':
            # 작업이 아직 시작되지 않음
            status_info["elapsed_time"] = 0.0

        elif result.state == 'TRAINING':
            # 작업이 진행 중 - 현재 시간으로 경과 시간 계산
            if result.info:
                start_time = result.info.get('start_time')
                if start_time:
                    current_elapsed = time.time() - start_time
                    status_info["elapsed_time"] = current_elapsed
                
                # subprocess PID 확인 및 실제 실행 상태 검증
                process_pid = result.info.get('process_pid')
                if process_pid:
                    try:
                        import os
                        os.kill(process_pid, 0)  # 프로세스 존재 확인
                        # 프로세스가 존재하면 정상 진행 중
                        status_info.update({k: v for k, v in result.info.items() if k != 'start_time'})
                    except ProcessLookupError:
                        # subprocess가 종료되었는데 Celery 상태가 아직 업데이트 안됨
                        status_info["status"] = "FAILURE"
                        status_info["error_message"] = "Training subprocess terminated unexpectedly"
                else:
                    # start_time을 제외한 나머지 정보들 업데이트
                    status_info.update({k: v for k, v in result.info.items() if k != 'start_time'})

        elif result.state == 'SUCCESS':
            # 작업 완료
            status_info["result"] = result.result
            if result.info:
                status_info["elapsed_time"] = result.info.get("elapsed_time")

        elif result.state == 'FAILURE':
            # 작업 실패 - Celery가 자동으로 처리한 예외
            if result.info:
                # result.info는 예외 객체이므로 문자열로 변환
                status_info["error_message"] = str(result.info)
            else:
                status_info["error_message"] = "Training failed with unknown error"

        elif result.state == 'REVOKED':
            # 작업 취소됨
            status_info["error_message"] = "Training was cancelled"
            if result.info:
                start_time = result.info.get('start_time')
                if start_time:
                    status_info["elapsed_time"] = time.time() - start_time
                
                # 취소된 작업의 subprocess 상태 확인
                process_pid = result.info.get('process_pid')
                if process_pid:
                    try:
                        import os
                        os.kill(process_pid, 0)  # 프로세스 존재 확인
                        status_info["error_message"] = "Training cancellation requested, but subprocess is still running"
                    except ProcessLookupError:
                        status_info["error_message"] = "Training was cancelled and subprocess terminated successfully"
                
                status_info.update({k: v for k, v in result.info.items() if k not in ['start_time']})
        
        return HSITrainStatus(**status_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting training status: {str(e)}")


@router.delete("/{train_id}")
async def cancel_hsi_train(train_id: str):
    """
    HSI 학습 작업을 취소하는 엔드포인트
    """
    import signal
    import os
    import subprocess
    
    try:
        result = AsyncResult(train_id, app=celery_app)
        
        if result.state not in ["PENDING", "TRAINING"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel training in state {result.state}")
        
        # 1. Celery 작업 취소 (부드러운 방식 - worker 종료 방지)
        celery_app.control.revoke(train_id)
        
        # 2. 학습 subprocess만 안전하게 종료 (Celery Worker는 유지)
        process_pid = None
        if result.info and result.info.get('process_pid'):
            process_pid = result.info.get('process_pid')
            
            try:
                # 학습 subprocess만 종료 (Worker와 완전히 분리됨)
                os.kill(process_pid, signal.SIGTERM)
                print(f"Sent SIGTERM to training subprocess {process_pid}")
                
                # 정상 종료 대기
                import time
                time.sleep(3)
                
                # 여전히 실행 중이면 강제 종료 (Worker에 영향 없음)
                try:
                    os.kill(process_pid, 0)  # 프로세스 존재 확인
                    print(f"Training subprocess {process_pid} still running, sending SIGKILL")
                    os.kill(process_pid, signal.SIGKILL)
                    print(f"Training subprocess {process_pid} force terminated")
                except ProcessLookupError:
                    print(f"Training subprocess {process_pid} terminated successfully")
                    
            except ProcessLookupError:
                print(f"Training subprocess {process_pid} not found")
            except PermissionError:
                print(f"Permission denied to signal training subprocess {process_pid}")
        else:
            print(f"No training subprocess PID found for train_id {train_id}, only revoking Celery task")
        
        # 3. 수동으로 상태를 REVOKED로 업데이트 (worker 종료 방지)
        result.revoke()
        
        # 메시지 구성
        if process_pid:
            message = "HSI Training cancellation requested. The training subprocess has been terminated while Celery worker remains active."
        else:
            message = "HSI Training task has been revoked. No running training subprocess found to terminate."
        
        return {
            "message": message,
            "cancelled_pid": process_pid,
            "train_id": train_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling training: {str(e)}")

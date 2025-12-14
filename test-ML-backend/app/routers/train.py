"""
일반 RGB/HSI/벡터 학습 작업을 큐에 맡기는 라우터.

클라이언트로부터 설정을 받아 Celery 작업을 시작하고 상태를 조회한다.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Literal
import json
import tempfile
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult
from app.core.config import settings


# Celery 및 APIRouter 설정
# 중앙 설정에서 REDIS_URL 사용
REDIS_URL = settings.REDIS_URL
celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# GPU 환경 최적화 설정
celery_app.conf.update(
    worker_prefetch_multiplier=1,  # GPU 메모리 절약
    task_acks_late=True,          # 작업 완료 후 ACK
    worker_max_tasks_per_child=None, # worker 재시작 비활성화 (solo pool 안정성 향상)
    # task_time_limit=7200,         # 2시간 제한
    # task_soft_time_limit=6600,    # 1시간 50분 소프트 제한
)

router = APIRouter()


# Pydantic 모델 정의
class TrainRequest(BaseModel):
    config: Optional[Dict] = None
    input_type: Literal["hsi_image", "vector", "rgb_image"]

class TrainResponse(BaseModel):
    message: str
    train_id: str
    process_pid: Optional[int] = None
    created_at: datetime

class TrainStatus(BaseModel):
    train_id: str
    status: Literal["PENDING", "TRAINING", "SUCCESS", "FAILURE", "REVOKED"]
    elapsed_time: Optional[float] = None  # 실행 시간 (초)
    error_message: Optional[str] = None
    result: Optional[Dict] = None


# Celery 백그라운드에서 학습을 실행하는 함수
@celery_app.task(bind=True)
def run_train_task(self, config: Dict):
    import time
    import os
    import subprocess
    import sys
    
    try:
        # 시작 시간 기록
        start_time = time.time()
        
        # input_type 검증
        input_type = config.get("input_type")
        if input_type not in ["hsi_image", "vector", "rgb_image"]:
            raise ValueError(f"Invalid input_type: {input_type}. Must be 'hsi_image', 'vector', or 'rgb_image'")
        
        # 임시 config 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            config_path = f.name
        
        # subprocess로 학습 프로세스 실행 (OS/배포 환경에 따라 유연하게 경로 계산)
        # 1) 환경변수 TRAINING_DIR이 있으면 우선 사용
        # 2) 없으면 현재 파일 기준으로 test-ML-backend/training_HSI 폴더 상대경로 계산
        # 중앙 설정에서 TRAINING_DIR 사용
        training_dir = settings.TRAINING_DIR
        training_dir = os.path.normpath(training_dir)
        if not os.path.isdir(training_dir):
            raise NotADirectoryError(f"Training directory does not exist: {training_dir}")

        if config.get("input_type") == "hsi_image":
            script_name = "train_HSI_2d.py"
        elif config.get("input_type") == "vector":
            script_name = "train_vector.py"
        else:
            script_name = "train_RGB.py"
        
        # subprocess로 학습 실행 (Worker와 분리된 별도 프로세스)
        process = subprocess.Popen(
            [sys.executable, script_name, '--config', config_path],
            cwd=training_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 학습 상태 업데이트: TRAINING (subprocess PID 포함)
        self.update_state(state='TRAINING', meta={
            'input_type': input_type,
            'process_pid': process.pid,  # ← 이제 별도 프로세스 PID
            'start_time': start_time
        })
        
        try:
            print(f"Starting training with config: {config_path}")
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
            # 임시 config 파일 삭제
            if os.path.exists(config_path):
                os.remove(config_path)
        
    except Exception as e:
        # Celery가 자동으로 FAILURE 상태로 처리하도록 예외를 다시 발생시킴
        # 커스텀 에러 정보는 예외 메시지에 포함
        import traceback
        error_message = f"{type(e).__name__}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"Training failed: {error_message}")
        
        # 예외를 다시 발생시켜서 Celery가 자동으로 FAILURE 처리하도록 함
        raise Exception(error_message)


@router.post("/", response_model=TrainResponse)
async def start_train(request: TrainRequest):
    """
    ML 모델 학습을 시작하는 엔드포인트
    """
    try:
        config = request.config
        if not config:
            raise HTTPException(status_code=400, detail="Config is required")
        
        # config에 input_type 추가
        config["input_type"] = request.input_type
        
        # Celery 작업 시작
        task = run_train_task.apply_async(args=[config])
        
        # 작업이 시작될 때까지 잠시 기다려서 PID 가져오기
        import time
        process_pid = None
        for _ in range(10):  # 최대 1초 대기
            result = AsyncResult(task.id, app=celery_app)
            if result.state == 'TRAINING' and result.info:
                process_pid = result.info.get('process_pid')
                break
            time.sleep(0.1)
        
        return TrainResponse(
            message=f"Training started in background for {request.input_type} model",
            train_id=task.id,
            process_pid=process_pid,
            created_at=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{train_id}", response_model=TrainStatus)
async def get_train_status(train_id: str):
    """
    학습 상태를 확인하는 엔드포인트
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
        
        return TrainStatus(**status_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting training status: {str(e)}")


@router.delete("/{train_id}")
async def cancel_train(train_id: str):
    """
    학습 작업을 취소하는 엔드포인트
    """
    import signal
    import os
    
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
            message = "Training cancellation requested. The training subprocess has been terminated while Celery worker remains active."
        else:
            message = "Training task has been revoked. No running training subprocess found to terminate."
        
        return {
            "message": message,
            "cancelled_pid": process_pid,
            "train_id": train_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling training: {str(e)}")

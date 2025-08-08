from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Literal
import json
import tempfile
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult

from training_HSI.train_HSI_2d import main as train_hsi_2d
from training_HSI.train_vector import main as train_vector

# Celery 및 APIRouter 설정
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
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
    input_type: Literal["image", "vector"]

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
        if input_type not in ["image", "vector"]:
            raise ValueError(f"Invalid input_type: {input_type}. Must be 'image' or 'vector'")
        
        # 임시 config 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f, indent=2)
            config_path = f.name
        
        # subprocess로 학습 프로세스 실행
        training_dir = "/home/ubuntu/2025-Deeplant-Dev/20252R0136COSE48002/test-ML-backend/training_HSI"
        
        if config.get("input_type") == "image":
            script_name = "train_HSI_2d.py"
        else:
            script_name = "train_vector.py"
        
        # subprocess로 학습 실행 (Worker와 분리된 별도 프로세스)
        # MLflow run ID를 파일로 받기 위한 임시 파일 생성
        run_id_file = f"/tmp/mlflow_run_id_{self.request.id}.txt"
        
        process = subprocess.Popen(
            [sys.executable, script_name, '--config', config_path, '--run-id-file', run_id_file],
            cwd=training_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env={**os.environ, 'MLFLOW_RUN_ID_FILE': run_id_file}  # 환경 변수도 전달
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
            
            # stdout에서 MLflow run ID 추출 (파일 우선, stdout 백업)
            mlflow_run_id = None
            
            # 방법 1: 파일에서 run ID 읽기 (가장 안정적)
            if os.path.exists(run_id_file):
                try:
                    with open(run_id_file, 'r') as f:
                        file_run_id = f.read().strip()
                        if file_run_id and len(file_run_id) > 10:
                            mlflow_run_id = file_run_id
                            print(f"MLflow run ID from file: {mlflow_run_id}")
                    # 파일 정리
                    os.remove(run_id_file)
                except Exception as e:
                    print(f"Error reading run ID file: {e}")
            
            # 방법 2: stdout에서 찾기 (백업)
            if not mlflow_run_id and stdout:
                print(f"Trying to extract from stdout:\n{stdout}")
                lines = stdout.strip().split('\n')               
                # "MLflow run ended" 다음 줄에서 run ID 찾기
                for i, line in enumerate(lines):
                    line = line.strip()
                    if "mlflow run ended" in line.lower():
                        # 다음 줄이 있고 비어있지 않으면 그것이 run ID
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line and len(next_line) > 10 and not next_line.startswith('-'):
                                mlflow_run_id = next_line
                                print(f"MLflow run ID from stdout: {mlflow_run_id}")
                                break
                
                # "run id:" 패턴으로 찾기
                if not mlflow_run_id:
                    for line in reversed(lines):
                        line = line.strip()
                        if line and "run id:" in line.lower():
                            mlflow_run_id = line.split(':')[-1].strip()
                            print(f"MLflow run ID from 'run id:' pattern: {mlflow_run_id}")
                            break
            
            print(f"Training completed with run ID: {mlflow_run_id}")
            
            # 완료 시간 계산
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            # 학습 완료 - SUCCESS 상태로 업데이트
            self.update_state(state='SUCCESS', meta={
                'mlflow_run_id': mlflow_run_id,
                'elapsed_time': elapsed_time
            })
            
            # 최종 결과 반환
            return {'mlflow_run_id': mlflow_run_id}

        finally:
            # 임시 파일들 정리
            if os.path.exists(config_path):
                os.remove(config_path)
            # run_id_file은 이미 위에서 정리되었지만 확인차 한번 더
            if 'run_id_file' in locals() and os.path.exists(run_id_file):
                os.remove(run_id_file)
        
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
    import subprocess
    
    try:
        result = AsyncResult(train_id, app=celery_app)
        
        if result.state not in ["PENDING", "TRAINING"]:
            raise HTTPException(status_code=400, detail=f"Cannot cancel training in state {result.state}")
        
        # 1. Celery 작업 취소 (부드러운 방식 - worker 종료 방지)
        celery_app.control.revoke(train_id)
        
        # 2. PID를 통해 학습 프로세스만 정상 종료 시도
        process_pid = None
        if result.info and result.info.get('process_pid'):
            process_pid = result.info.get('process_pid')
            
            try:
                # SIGTERM으로 정상 종료 시도 (SIGKILL 제거)
                os.kill(process_pid, signal.SIGTERM)
                print(f"Sent SIGTERM to process {process_pid}")
                
                # 프로세스가 정상 종료될 시간을 줌
                import time
                time.sleep(3)
                
                # 프로세스가 여전히 존재하는지 확인만 하고, 강제 종료는 하지 않음
                try:
                    os.kill(process_pid, 0)  # 프로세스 존재 확인
                    print(f"Process {process_pid} still running after SIGTERM")
                except ProcessLookupError:
                    print(f"Process {process_pid} terminated successfully")
                    
            except ProcessLookupError:
                print(f"Process {process_pid} not found")
            except PermissionError:
                print(f"Permission denied to signal process {process_pid}")
        else:
            print(f"No process PID found for train_id {train_id}, only revoking Celery task")
        
        # 3. 수동으로 상태를 REVOKED로 업데이트 (worker 종료 방지)
        result.revoke()
        
        # 메시지 구성
        if process_pid:
            message = "Training cancellation requested. The process may take a few moments to stop gracefully."
        else:
            message = "Training task has been revoked. No running process found to terminate."
        
        return {
            "message": message,
            "cancelled_pid": process_pid,
            "train_id": train_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling training: {str(e)}") 
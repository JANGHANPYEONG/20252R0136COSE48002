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


@celery_app.task(bind=True)
def run_train_task(self, config: Dict):
    import time
    import os
    import multiprocessing
    from multiprocessing import Process, Queue
    
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
        
        # 별도 프로세스에서 학습 함수 실행하기 위한 래퍼 함수
        def train_wrapper(train_func, args, result_queue, error_queue):
            try:
                result = train_func(args)
                result_queue.put(result)
            except Exception as e:
                import traceback
                error_queue.put({
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        # 결과를 받기 위한 큐 생성
        result_queue = Queue()
        error_queue = Queue()
        
        # 학습 함수 선택
        if config.get("input_type") == "image":
            train_func = train_hsi_2d
        else:
            train_func = train_vector
        
        # 별도 프로세스에서 학습 실행
        process = Process(
            target=train_wrapper, 
            args=(train_func, ['--config', config_path], result_queue, error_queue)
        )
        process.start()
        
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
            process.join()
            
            # 결과 확인
            if not error_queue.empty():
                error_info = error_queue.get()
                raise Exception(f"Training failed: {error_info['error']}\n{error_info['traceback']}")
            
            if process.exitcode != 0:
                raise Exception(f"Training process failed with exit code {process.exitcode}")
            
            # 결과에서 MLflow run ID 가져오기
            if not result_queue.empty():
                mlflow_run_id = result_queue.get()
            else:
                raise Exception("No result returned from training process")
            
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
                
                # process PID 확인 및 실제 실행 상태 검증
                process_pid = result.info.get('process_pid')
                if process_pid:
                    try:
                        import os
                        os.kill(process_pid, 0)  # 프로세스 존재 확인
                        # 프로세스가 존재하면 정상 진행 중
                        status_info.update({k: v for k, v in result.info.items() if k != 'start_time'})
                    except ProcessLookupError:
                        # 프로세스가 종료되었는데 Celery 상태가 아직 업데이트 안됨
                        status_info["status"] = "FAILURE"
                        status_info["error_message"] = "Training process terminated unexpectedly"
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
                
                # 취소된 작업의 process 상태 확인
                process_pid = result.info.get('process_pid')
                if process_pid:
                    try:
                        import os
                        os.kill(process_pid, 0)  # 프로세스 존재 확인
                        status_info["error_message"] = "Training cancellation requested, but process is still running"
                    except ProcessLookupError:
                        status_info["error_message"] = "Training was cancelled and process terminated successfully"
                
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
        
        # 2. 학습 multiprocessing 프로세스만 안전하게 종료 (Celery Worker는 유지)
        process_pid = None
        if result.info and result.info.get('process_pid'):
            process_pid = result.info.get('process_pid')
            
            try:
                # 학습 multiprocessing 프로세스만 종료 (Worker와 완전히 분리됨)
                os.kill(process_pid, signal.SIGTERM)
                print(f"Sent SIGTERM to training process {process_pid}")
                
                # 정상 종료 대기
                import time
                time.sleep(3)
                
                # 여전히 실행 중이면 강제 종료 (Worker에 영향 없음)
                try:
                    os.kill(process_pid, 0)  # 프로세스 존재 확인
                    print(f"Training process {process_pid} still running, sending SIGKILL")
                    os.kill(process_pid, signal.SIGKILL)
                    print(f"Training process {process_pid} force terminated")
                except ProcessLookupError:
                    print(f"Training process {process_pid} terminated successfully")
                    
            except ProcessLookupError:
                print(f"Training process {process_pid} not found")
            except PermissionError:
                print(f"Permission denied to signal training process {process_pid}")
        else:
            print(f"No training process PID found for train_id {train_id}, only revoking Celery task")
        
        # 3. 수동으로 상태를 REVOKED로 업데이트 (worker 종료 방지)
        result.revoke()
        
        # 메시지 구성
        if process_pid:
            message = "Training cancellation requested. The training process has been terminated while Celery worker remains active."
        else:
            message = "Training task has been revoked. No running training process found to terminate."
        
        return {
            "message": message,
            "cancelled_pid": process_pid,
            "train_id": train_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling training: {str(e)}") 
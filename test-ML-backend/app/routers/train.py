from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Literal
from datetime import datetime
from celery import Celery
from celery.result import AsyncResult
from multiprocessing import get_context, Queue
import contextlib, io, re

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
    import sys
    import json
    import tempfile

    # 자식 프로세스에서 실행할 엔트리 함수
    def _train_entry(cfg: Dict, q: Queue):
        """
        별도 프로세스에서 학습 함수를 직접 호출.
        stdout/stderr 캡처 후 mlflow_run_id를 파싱해서 큐로 전달.
        """
        from training_HSI.train_HSI_2d import main as train_hsi_2d
        from training_HSI.train_vector import main as train_vector

        # 임시 config 파일 생성 (기존 스크립트가 --config CLI 인자를 기대한다면)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(cfg, f, indent=2)
            cfg_path = f.name

        # main()이 argparse로 sys.argv를 읽는 경우를 대비해 sys.argv 주입
        old_argv = sys.argv[:]
        sys.argv = [old_argv[0], "--config", cfg_path]

        buf = io.StringIO()
        try:
            mlflow_run_id = None
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                if cfg.get("input_type") == "image":
                    mlflow_run_id = train_hsi_2d()     # 함수 직접 호출
                else:
                    mlflow_run_id = train_vector()     # 함수 직접 호출
            out = buf.getvalue()

            q.put({"ok": True, "mlflow_run_id": mlflow_run_id, "logs": out})
        except Exception as e:
            q.put({"ok": False, "error": f"{type(e).__name__}: {e}"})
        finally:
            # 정리
            try:
                os.remove(cfg_path)
            except Exception:
                pass
            sys.argv = old_argv

    try:
        start_time = time.time()

        input_type = config.get("input_type")
        if input_type not in ["image", "vector"]:
            raise ValueError(f"Invalid input_type: {input_type}. Must be 'image' or 'vector'")

        # 별도 프로세스 생성 (macOS에서는 spawn 권장)
        ctx = get_context("spawn")
        q: Queue = ctx.Queue()
        proc = ctx.Process(target=_train_entry, args=(config, q))
        proc.start()

        # 상태 업데이트 (자식 PID 노출)
        self.update_state(state="TRAINING", meta={
            "input_type": input_type,
            "process_pid": proc.pid,
            "start_time": start_time
        })

        # 자식 종료 대기
        proc.join()

        # 결과 수거
        if not q.empty():
            res = q.get()
        else:
            res = {"ok": False, "error": "No result returned from training process"}

        if not res.get("ok"):
            raise Exception(res.get("error", "Training failed without error message"))

        mlflow_run_id = res.get("mlflow_run_id")

        elapsed = time.time() - start_time
        self.update_state(state="SUCCESS", meta={
            "mlflow_run_id": mlflow_run_id,
            "elapsed_time": elapsed
        })
        return {"mlflow_run_id": mlflow_run_id}

    except Exception as e:
        import traceback
        error_message = f"{type(e).__name__}: {e}\n\nTraceback:\n{traceback.format_exc()}"
        print(f"Training failed: {error_message}")
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
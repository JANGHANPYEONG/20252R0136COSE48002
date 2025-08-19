"""
실시간 학습 스트리밍 API 라우터

기존 학습 API와 연동하여 실시간으로 학습 진행 상황을 스트리밍합니다.

엔드포인트 개요:
- GET /train-stream/stream/{train_id} - SSE 스트리밍 연결
- GET /train-stream/metrics/{train_id} - 폴링 방식 메트릭 조회
- GET /train-stream/status/{train_id} - 학습 상태 조회

사용법:
1. POST /train/ 로 학습 시작 (기존 API 사용)
2. 반환된 train_id로 스트리밍 연결
3. MLflow run ID를 통해 실시간 메트릭 조회
"""

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio
import json
import time

from app.utils.metric_buffer import get_metric_buffer, InMemoryMetricBuffer
from app.utils.mlflow_client import get_mlflow_client, MLflowMetricsClient
from app.utils.streaming_manager import get_streaming_manager, StreamingManager
from app.routers.train import celery_app
from celery.result import AsyncResult

router = APIRouter(prefix="/train-stream", tags=["train-stream"])

# ------------------------ 요청/응답 모델 ------------------------

class MetricsResponse(BaseModel):
    items: list            # [{seq, ts, type, epoch, ...}, ...]
    next: int              # 다음 호출에서 after로 넣을 커서
    status: str            # "running" | "done"

class StreamStatusResponse(BaseModel):
    train_id: str
    status: str
    mlflow_run_id: Optional[str] = None
    active_connections: int = 0


# ------------------------ 의존성 주입 ------------------------

def get_buffer() -> InMemoryMetricBuffer:
    """메트릭 버퍼 의존성 주입"""
    return get_metric_buffer()

def get_mlflow_client_dep() -> MLflowMetricsClient:
    """MLflow 클라이언트 의존성 주입"""
    return get_mlflow_client()

def get_streaming_manager_dep() -> StreamingManager:
    """스트리밍 매니저 의존성 주입"""
    return get_streaming_manager()


# ------------------------ 백그라운드 메트릭 모니터링 ------------------------

async def monitor_mlflow_metrics(train_id: str, mlflow_run_id: str, 
                                buffer: InMemoryMetricBuffer, 
                                streaming_manager: StreamingManager) -> None:
    """
    MLflow에서 실시간으로 메트릭을 모니터링하고 스트리밍합니다.
    """
    mlflow_client = get_mlflow_client()
    last_step = 0
    
    try:
        while True:
            # MLflow에서 새 메트릭 가져오기
            new_metrics = mlflow_client.get_run_metrics(mlflow_run_id, after_step=last_step)
            
            for metrics in new_metrics:
                if metrics:
                    # 메트릭을 버퍼에 저장
                    buffer.publish(train_id, {
                        "type": "epoch",
                        "epoch": metrics.get("step", 0),
                        **metrics
                    })
                    
                    # SSE로 브로드캐스트
                    await streaming_manager.broadcast_metrics(train_id, {
                        "type": "metrics",
                        "train_id": train_id,
                        **metrics
                    })
                    
                    last_step = max(last_step, metrics.get("step", 0))
            
            # 학습 완료 확인
            run_status = mlflow_client.get_run_status(mlflow_run_id)
            if run_status in ["FINISHED", "FAILED"]:
                # 완료 메시지 전송
                final_metrics = mlflow_client.get_latest_metrics(mlflow_run_id)
                if final_metrics:
                    buffer.publish(train_id, {
                        "type": "final",
                        "train_id": train_id,
                        **final_metrics
                    })
                    
                    await streaming_manager.broadcast_metrics(train_id, {
                        "type": "final",
                        "train_id": train_id,
                        "status": run_status,
                        **final_metrics
                    })
                
                # 상태 업데이트
                await streaming_manager.broadcast_status(train_id, run_status.lower())
                buffer.mark_done(train_id)
                break
            
            # 2초 대기 후 다시 확인
            await asyncio.sleep(2)
            
    except Exception as e:
        print(f"Error monitoring metrics for train_id {train_id}: {e}")
        # 에러 상태 브로드캐스트
        await streaming_manager.broadcast_status(train_id, "error")
        buffer.mark_done(train_id)
    finally:
        # 연결 정리
        streaming_manager.cleanup_train_id(train_id)


# ------------------------ 라우트 핸들러 ------------------------

@router.get("/stream/{train_id}")
async def stream_training(
    train_id: str,
    background: BackgroundTasks,
    buffer: InMemoryMetricBuffer = Depends(get_buffer),
    streaming_manager: StreamingManager = Depends(get_streaming_manager_dep)
):
    """
    SSE 스트리밍 연결 엔드포인트.
    
    기존 학습 API로 시작한 학습의 실시간 진행 상황을 스트리밍합니다.
    """
    # Celery task 상태 확인
    result = AsyncResult(train_id, app=celery_app)
    
    if result.state == "PENDING":
        raise HTTPException(status_code=404, detail="Training task not found")
    
    # MLflow run ID 추출 (task가 완료되면 result에서 가져옴)
    mlflow_run_id = None
    if result.state == "SUCCESS" and result.result:
        mlflow_run_id = result.result.get('mlflow_run_id')
    
    if not mlflow_run_id:
        # task가 아직 실행 중이면 MLflow run ID를 기다림
        raise HTTPException(status_code=400, detail="MLflow run ID not available yet. Please wait for training to start.")
    
    # 스트리밍 매니저에 MLflow run ID 등록
    streaming_manager.set_mlflow_run_id(train_id, mlflow_run_id)
    
    # 메트릭 모니터링 백그라운드 태스크 시작
    background.add_task(
        monitor_mlflow_metrics, 
        train_id, 
        mlflow_run_id, 
        buffer, 
        streaming_manager
    )
    
    async def generate_stream():
        """SSE 스트림 생성"""
        queue = asyncio.Queue()
        
        try:
            # 스트리밍 매니저에 연결 등록
            streaming_manager.add_connection(train_id, queue)
            
            # 연결 시작 메시지
            yield f"data: {json.dumps({'type': 'connected', 'train_id': train_id})}\n\n"
            
            # 메트릭 스트리밍
            while True:
                try:
                    # 큐에서 메시지 대기 (30초 타임아웃)
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message
                    
                    # 메시지 처리 완료
                    queue.task_done()
                    
                except asyncio.TimeoutError:
                    # 하트비트 전송
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
                    
        except Exception as e:
            # 에러 메시지 전송
            error_msg = {
                "type": "error",
                "train_id": train_id,
                "error": str(e),
                "timestamp": time.time()
            }
            yield f"data: {json.dumps(error_msg)}\n\n"
            
        finally:
            # 연결 정리
            streaming_manager.remove_connection(train_id, queue)
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.get("/metrics/{train_id}", response_model=MetricsResponse)
def read_metrics(
    train_id: str,
    after: int = Query(0, description="마지막으로 받은 seq(없으면 0)"),
    limit: int = Query(100, ge=1, le=1000, description="한 번에 가져올 최대 개수"),
    buffer: InMemoryMetricBuffer = Depends(get_buffer)
):
    """
    폴링 방식 메트릭 조회 엔드포인트.
    
    SSE 대신 폴링을 사용하는 클라이언트를 위한 엔드포인트입니다.
    """
    return buffer.read(train_id, after=after, limit=limit)


@router.get("/status/{train_id}", response_model=StreamStatusResponse)
def get_stream_status(
    train_id: str,
    streaming_manager: StreamingManager = Depends(get_streaming_manager_dep),
    buffer: InMemoryMetricBuffer = Depends(get_buffer)
):
    """
    스트리밍 상태 조회 엔드포인트.
    """
    # Celery task 상태 확인
    result = AsyncResult(train_id, app=celery_app)
    
    # MLflow run ID 가져오기
    mlflow_run_id = streaming_manager.get_mlflow_run_id(train_id)
    
    # 활성 연결 수
    active_connections = streaming_manager.get_active_connections(train_id)
    
    # 버퍼 상태
    buffer_status = buffer.status(train_id)
    
    return StreamStatusResponse(
        train_id=train_id,
        status=buffer_status,
        mlflow_run_id=mlflow_run_id,
        active_connections=active_connections
    )


@router.get("/connections")
def get_connection_stats(
    streaming_manager: StreamingManager = Depends(get_streaming_manager_dep)
):
    """
    전체 연결 통계 조회 (디버깅용)
    """
    return {
        "total_connections": streaming_manager.get_total_connections(),
        "active_trains": len(streaming_manager.connections)
    }

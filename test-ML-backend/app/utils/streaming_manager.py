"""
스트리밍 매니저 모듈

SSE(Server-Sent Events) 연결을 관리하고 메트릭을 브로드캐스팅합니다.
"""

import asyncio
import json
from typing import Dict, Set, Any, Optional
from fastapi import HTTPException
import time


class StreamingManager:
    def __init__(self):
        """
        스트리밍 매니저 초기화
        """
        # train_id별로 연결된 클라이언트들을 관리
        self.connections: Dict[str, Set[asyncio.Queue]] = {}
        # train_id별 MLflow run ID 매핑
        self.train_to_mlflow: Dict[str, str] = {}
        # 활성 연결 수 추적
        self.active_connections = 0
    
    def add_connection(self, train_id: str, queue: asyncio.Queue) -> None:
        """
        새로운 SSE 연결을 추가합니다.
        
        Args:
            train_id: 학습 ID
            queue: 메시지를 전송할 큐
        """
        if train_id not in self.connections:
            self.connections[train_id] = set()
        
        self.connections[train_id].add(queue)
        self.active_connections += 1
        print(f"Added connection for train_id {train_id}. Total connections: {self.active_connections}")
    
    def remove_connection(self, train_id: str, queue: asyncio.Queue) -> None:
        """
        SSE 연결을 제거합니다.
        
        Args:
            train_id: 학습 ID
            queue: 제거할 큐
        """
        if train_id in self.connections:
            self.connections[train_id].discard(queue)
            if not self.connections[train_id]:
                del self.connections[train_id]
                # MLflow run ID도 정리
                self.train_to_mlflow.pop(train_id, None)
        
        self.active_connections = max(0, self.active_connections - 1)
        print(f"Removed connection for train_id {train_id}. Total connections: {self.active_connections}")
    
    def set_mlflow_run_id(self, train_id: str, mlflow_run_id: str) -> None:
        """
        train_id와 MLflow run_id를 매핑합니다.
        
        Args:
            train_id: 학습 ID
            mlflow_run_id: MLflow run ID
        """
        self.train_to_mlflow[train_id] = mlflow_run_id
        print(f"Mapped train_id {train_id} to MLflow run_id {mlflow_run_id}")
    
    def get_mlflow_run_id(self, train_id: str) -> Optional[str]:
        """
        train_id에 해당하는 MLflow run_id를 가져옵니다.
        
        Args:
            train_id: 학습 ID
            
        Returns:
            MLflow run ID 또는 None
        """
        return self.train_to_mlflow.get(train_id)
    
    async def broadcast_metrics(self, train_id: str, metrics: Dict[str, Any]) -> None:
        """
        특정 train_id의 모든 연결된 클라이언트에게 메트릭을 브로드캐스트합니다.
        
        Args:
            train_id: 학습 ID
            metrics: 브로드캐스트할 메트릭
        """
        if train_id not in self.connections:
            return
        
        # SSE 형식으로 메시지 생성
        message = f"data: {json.dumps(metrics)}\n\n"
        
        # 모든 연결된 클라이언트에게 전송
        disconnected_queues = set()
        
        for queue in self.connections[train_id]:
            try:
                await queue.put(message)
            except Exception as e:
                print(f"Error broadcasting to queue: {e}")
                disconnected_queues.add(queue)
        
        # 연결이 끊어진 큐들 정리
        for queue in disconnected_queues:
            self.remove_connection(train_id, queue)
    
    async def broadcast_status(self, train_id: str, status: str) -> None:
        """
        학습 상태를 브로드캐스트합니다.
        
        Args:
            train_id: 학습 ID
            status: 상태 메시지
        """
        status_message = {
            "type": "status",
            "train_id": train_id,
            "status": status,
            "timestamp": time.time()
        }
        await self.broadcast_metrics(train_id, status_message)
    
    def get_active_connections(self, train_id: str) -> int:
        """
        특정 train_id의 활성 연결 수를 반환합니다.
        
        Args:
            train_id: 학습 ID
            
        Returns:
            활성 연결 수
        """
        return len(self.connections.get(train_id, set()))
    
    def get_total_connections(self) -> int:
        """
        전체 활성 연결 수를 반환합니다.
        
        Returns:
            전체 활성 연결 수
        """
        return self.active_connections
    
    def has_connections(self, train_id: str) -> bool:
        """
        특정 train_id에 연결된 클라이언트가 있는지 확인합니다.
        
        Args:
            train_id: 학습 ID
            
        Returns:
            연결이 있으면 True, 없으면 False
        """
        return train_id in self.connections and len(self.connections[train_id]) > 0
    
    def cleanup_train_id(self, train_id: str) -> None:
        """
        특정 train_id의 모든 연결을 정리합니다.
        
        Args:
            train_id: 학습 ID
        """
        if train_id in self.connections:
            self.active_connections -= len(self.connections[train_id])
            del self.connections[train_id]
        
        self.train_to_mlflow.pop(train_id, None)
        print(f"Cleaned up train_id {train_id}")


# 전역 스트리밍 매니저 인스턴스
streaming_manager = StreamingManager()


def get_streaming_manager() -> StreamingManager:
    """
    의존성 주입용 팩토리 함수
    """
    return streaming_manager

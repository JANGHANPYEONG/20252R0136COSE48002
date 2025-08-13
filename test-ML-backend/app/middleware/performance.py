"""
성능 모니터링 미들웨어
"""

import time
import psutil
import logging
from collections import defaultdict
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict

logger = logging.getLogger("ml_server")


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """API 성능을 모니터링하는 미들웨어"""
    
    def __init__(self, app):
        super().__init__(app)
        self.request_times: Dict[str, list] = defaultdict(list)
        self.request_counts: Dict[str, int] = defaultdict(int)
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 요청 처리
        response = await call_next(request)
        
        # 성능 측정
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        process_time = end_time - start_time
        memory_diff = end_memory - start_memory
        
        # 엔드포인트별 통계 수집
        endpoint = f"{request.method} {request.url.path}"
        self.request_times[endpoint].append(process_time)
        self.request_counts[endpoint] += 1
        
        # 성능 헤더 추가
        response.headers["X-Process-Time"] = f"{process_time:.4f}"
        response.headers["X-Memory-Usage"] = f"{end_memory:.1f}MB"
        
        # 느린 요청 로깅 (1초 이상)
        if process_time > 1.0:
            logger.warning(
                f"Slow request detected - {endpoint} "
                f"Time: {process_time:.3f}s "
                f"Memory: {memory_diff:+.1f}MB"
            )
        
        # 메모리 사용량이 많은 요청 로깅 (50MB 이상)
        if memory_diff > 50:
            logger.warning(
                f"High memory usage - {endpoint} "
                f"Memory increase: {memory_diff:.1f}MB "
                f"Time: {process_time:.3f}s"
            )
        
        return response
    
    def get_stats(self) -> dict:
        """성능 통계 반환"""
        stats = {}
        for endpoint, times in self.request_times.items():
            if times:
                stats[endpoint] = {
                    "count": self.request_counts[endpoint],
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "recent_times": times[-10:]  # 최근 10개 요청
                }
        return stats


class ResourceLimitMiddleware(BaseHTTPMiddleware):
    """리소스 사용량을 제한하는 미들웨어"""
    
    def __init__(self, app, max_memory_mb: int = 1000, max_requests_per_minute: int = 1000):
        super().__init__(app)
        self.max_memory_mb = max_memory_mb
        self.max_requests_per_minute = max_requests_per_minute
        self.request_history: list = []
    
    async def dispatch(self, request: Request, call_next: Callable):
        current_time = time.time()
        
        # 1분 이내 요청 수 체크
        self.request_history = [t for t in self.request_history if current_time - t < 60]
        self.request_history.append(current_time)
        
        if len(self.request_history) > self.max_requests_per_minute:
            logger.warning(f"Rate limit exceeded: {len(self.request_history)} requests/minute")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "message": "Rate limit exceeded"}
            )
        
        # 메모리 사용량 체크
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        if current_memory > self.max_memory_mb:
            logger.error(f"Memory limit exceeded: {current_memory:.1f}MB > {self.max_memory_mb}MB")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=503,
                content={"error": "Service Unavailable", "message": "Server overloaded"}
            )
        
        response = await call_next(request)
        return response

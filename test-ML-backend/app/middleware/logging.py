"""
요청/응답 로깅 미들웨어
"""

import time
import json
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable

# 로거 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ml_server")


class LoggingMiddleware(BaseHTTPMiddleware):
    """모든 API 요청/응답을 로깅하는 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # 요청 정보 수집
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        url = str(request.url)
        
        # 요청 로깅
        logger.info(f"Request started - {method} {url} from {client_ip}")
        
        # 요청 처리
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # 응답 로깅
            logger.info(
                f"Request completed - {method} {url} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s "
                f"IP: {client_ip}"
            )
            
            # 응답 시간 헤더 추가
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed - {method} {url} "
                f"Error: {str(e)} "
                f"Time: {process_time:.3f}s "
                f"IP: {client_ip}"
            )
            raise


class DetailedLoggingMiddleware(BaseHTTPMiddleware):
    """상세한 디버그 로깅 (개발환경용)"""
    
    def __init__(self, app, enable_body_logging: bool = False):
        super().__init__(app)
        self.enable_body_logging = enable_body_logging
    
    async def dispatch(self, request: Request, call_next: Callable):
        if hasattr(request.app.state, 'settings'):
            settings = request.app.state.settings
            if settings.ENVIRONMENT != "development":
                return await call_next(request)
        
        start_time = time.time()
        
        # 요청 헤더 로깅
        headers = dict(request.headers)
        logger.debug(f"Request headers: {json.dumps(headers, indent=2)}")
        
        # 요청 본문 로깅 (개발환경에서만)
        if self.enable_body_logging and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    logger.debug(f"Request body: {body.decode('utf-8')[:500]}...")
            except Exception as e:
                logger.debug(f"Could not log request body: {e}")
        
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # 상세 성능 로깅
        logger.debug(
            f"Detailed timing - URL: {request.url} "
            f"Method: {request.method} "
            f"Status: {response.status_code} "
            f"Process time: {process_time:.4f}s"
        )
        
        return response

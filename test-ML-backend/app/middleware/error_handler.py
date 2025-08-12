"""
전역 예외 처리 미들웨어
"""

import traceback
import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from typing import Callable

logger = logging.getLogger("ml_server")


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """전역 예외를 처리하는 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # FastAPI HTTPException은 그대로 전달
            logger.warning(f"HTTP Exception: {e.status_code} - {e.detail}")
            raise
            
        except Exception as e:
            # 예상치 못한 예외 처리
            error_id = id(e)  # 에러 추적용 ID
            
            logger.error(
                f"Unhandled exception [ID: {error_id}] "
                f"URL: {request.url} "
                f"Method: {request.method} "
                f"Error: {str(e)}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            
            # 환경별 에러 응답
            if hasattr(request.app.state, 'settings'):
                settings = request.app.state.settings
                if settings.DEBUG and settings.ENVIRONMENT == "development":
                    # 개발환경: 상세 에러 정보 반환
                    return JSONResponse(
                        status_code=500,
                        content={
                            "error": "Internal Server Error",
                            "detail": str(e),
                            "error_id": error_id,
                            "traceback": traceback.format_exc().split('\n')
                        }
                    )
            
            # 프로덕션환경: 일반적인 에러 메시지만 반환
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "error_id": error_id
                }
            )


class ValidationErrorMiddleware(BaseHTTPMiddleware):
    """Pydantic 유효성 검사 에러를 보기 좋게 포맷팅"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            if "ValidationError" in str(type(e)):
                logger.warning(f"Validation error: {str(e)}")
                
                return JSONResponse(
                    status_code=422,
                    content={
                        "error": "Validation Error",
                        "message": "Invalid input data",
                        "details": str(e)
                    }
                )
            
            # 다른 예외는 다음 미들웨어로 전달
            raise

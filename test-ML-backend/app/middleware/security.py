"""
보안 관련 미들웨어
- 보안 헤더 추가
- Host 헤더 검증
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
import time


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더를 자동으로 추가하는 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # 개발환경에서는 Strict-Transport-Security 제외
        # 프로덕션에서만 HTTPS 강제
        if hasattr(request.app.state, 'settings'):
            settings = request.app.state.settings
            if settings.ENVIRONMENT == "production":
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class HostValidationMiddleware(BaseHTTPMiddleware):
    """허용된 Host 헤더만 허용하는 미들웨어"""
    
    def __init__(self, app, allowed_hosts: list = None):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or ["*"]
    
    async def dispatch(self, request: Request, call_next):
        # Host 헤더 검증
        if self.allowed_hosts != ["*"]:
            host = request.headers.get("host", "")
            if not any(
                host == allowed_host or 
                (allowed_host.startswith("*.") and host.endswith(allowed_host[2:]))
                for allowed_host in self.allowed_hosts
            ):
                return PlainTextResponse("Invalid host header", status_code=400)
        
        response = await call_next(request)
        return response

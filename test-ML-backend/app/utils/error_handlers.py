"""
에러 핸들링 유틸리티
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
from .logging_utils import get_logger

logger = get_logger(__name__)

class APIError(Exception):
    """커스텀 API 에러 클래스"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(APIError):
    """데이터 검증 에러"""
    
    def __init__(self, message: str = "Validation failed", field: str = None):
        self.field = field
        error_code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(message, 400, error_code)

class DatabaseError(APIError):
    """데이터베이스 에러"""
    
    def __init__(self, message: str = "Database operation failed", operation: str = None):
        self.operation = operation
        error_code = f"DB_ERROR_{operation.upper()}" if operation else "DB_ERROR"
        super().__init__(message, 500, error_code)

class NotFoundError(APIError):
    """리소스 찾을 수 없음 에러"""
    
    def __init__(self, resource: str = "Resource", resource_id: str = None):
        message = f"{resource} not found"
        if resource_id:
            message += f": {resource_id}"
        super().__init__(message, 404, "NOT_FOUND")

class UnauthorizedError(APIError):
    """인증 에러"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401, "UNAUTHORIZED")

class ForbiddenError(APIError):
    """권한 에러"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, 403, "FORBIDDEN")

class ConflictError(APIError):
    """충돌 에러"""
    
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, 409, "CONFLICT")

def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Dict[str, Any] = None
) -> JSONResponse:
    """
    표준 에러 응답 생성
    
    Args:
        status_code: HTTP 상태 코드
        message: 에러 메시지
        error_code: 에러 코드
        details: 추가 세부 정보
    
    Returns:
        JSONResponse 객체
    """
    content = {
        "error": True,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "status_code": status_code
    }
    
    if error_code:
        content["error_code"] = error_code
    
    if details:
        content["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )

def create_success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200
) -> JSONResponse:
    """
    표준 성공 응답 생성
    
    Args:
        data: 응답 데이터
        message: 성공 메시지
        status_code: HTTP 상태 코드
    
    Returns:
        JSONResponse 객체
    """
    content = {
        "error": False,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "status_code": status_code
    }
    
    if data is not None:
        content["data"] = data
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )

async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    API 에러 핸들러
    
    Args:
        request: FastAPI Request 객체
        exc: API 에러 객체
    
    Returns:
        에러 응답
    """
    logger.error(f"API Error: {exc.message} - Code: {exc.error_code} - Status: {exc.status_code}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_code=exc.error_code
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    일반 예외 핸들러
    
    Args:
        request: FastAPI Request 객체
        exc: 예외 객체
    
    Returns:
        에러 응답
    """
    error_trace = traceback.format_exc()
    logger.error(f"Unhandled Exception: {str(exc)}\\n{error_trace}")
    
    return create_error_response(
        status_code=500,
        message="Internal server error",
        error_code="INTERNAL_ERROR",
        details={"exception_type": type(exc).__name__}
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTP 예외 핸들러
    
    Args:
        request: FastAPI Request 객체
        exc: HTTP 예외 객체
    
    Returns:
        에러 응답
    """
    logger.warning(f"HTTP Exception: {exc.detail} - Status: {exc.status_code}")
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code="HTTP_ERROR"
    )

def handle_database_error(operation: str, error: Exception, table: str = None) -> DatabaseError:
    """
    데이터베이스 에러 처리
    
    Args:
        operation: 데이터베이스 작업 종류
        error: 발생한 에러
        table: 테이블명
    
    Returns:
        DatabaseError 객체
    """
    error_msg = f"Database {operation} failed"
    if table:
        error_msg += f" on table {table}"
    
    logger.error(f"{error_msg}: {str(error)}")
    return DatabaseError(error_msg, operation)

def handle_validation_error(field: str, value: Any, expected_type: str = None) -> ValidationError:
    """
    검증 에러 처리
    
    Args:
        field: 필드명
        value: 잘못된 값
        expected_type: 기대되는 타입
    
    Returns:
        ValidationError 객체
    """
    error_msg = f"Invalid value for field '{field}': {value}"
    if expected_type:
        error_msg += f" (expected {expected_type})"
    
    logger.warning(error_msg)
    return ValidationError(error_msg, field)

def safe_execute(func, *args, default_return=None, log_error=True, **kwargs):
    """
    안전한 함수 실행 (예외 처리)
    
    Args:
        func: 실행할 함수
        *args: 함수 인자
        default_return: 에러 시 반환할 기본값
        log_error: 에러 로깅 여부
        **kwargs: 함수 키워드 인자
    
    Returns:
        함수 실행 결과 또는 기본값
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_error:
            logger.error(f"Error executing {func.__name__}: {str(e)}")
        return default_return

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[ValidationError]:
    """
    필수 필드 검증
    
    Args:
        data: 검증할 데이터
        required_fields: 필수 필드 목록
    
    Returns:
        ValidationError 또는 None
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        return ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            field=missing_fields[0]
        )
    
    return None

def format_error_for_logging(error: Exception, context: Dict[str, Any] = None) -> str:
    """
    로깅용 에러 포맷팅
    
    Args:
        error: 에러 객체
        context: 추가 컨텍스트 정보
    
    Returns:
        포맷된 에러 문자열
    """
    error_info = {
        "type": type(error).__name__,
        "message": str(error),
        "traceback": traceback.format_exc()
    }
    
    if context:
        error_info["context"] = context
    
    return str(error_info)

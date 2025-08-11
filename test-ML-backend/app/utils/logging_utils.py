"""
통합 로깅 시스템
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pytz

def setup_logger(name: str = __name__, log_level: int = logging.DEBUG) -> logging.Logger:
    """
    로거 설정 함수
    
    Args:
        name: 로거 이름
        log_level: 로그 레벨
    
    Returns:
        설정된 로거 객체
    """
    # 로그 디렉토리 생성
    if not os.path.exists("log"):
        os.makedirs("log")
    
    # 로그 파일 경로
    log_file_path = os.path.join("log", "app.log")
    
    # 회전 파일 핸들러 설정 (최대 5MB, 마지막 5개 파일 유지)
    handler = RotatingFileHandler(
        log_file_path, 
        maxBytes=5 * 1024 * 1024, 
        backupCount=5,
        encoding='utf-8'
    )
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    
    # 로거 생성 및 설정
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # 기존 핸들러 제거 (중복 방지)
    if logger.handlers:
        logger.handlers.clear()
    
    logger.addHandler(handler)
    
    # 콘솔 핸들러도 추가 (개발 환경용)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# 기본 로거 인스턴스
logger = setup_logger()

def get_logger(name: str = None) -> logging.Logger:
    """
    로거 인스턴스 조회
    
    Args:
        name: 로거 이름 (None이면 기본 로거 반환)
    
    Returns:
        로거 객체
    """
    if name:
        return setup_logger(name)
    return logger

def log_api_call(endpoint: str, method: str, status_code: int, execution_time: float = None):
    """
    API 호출 로그 기록
    
    Args:
        endpoint: API 엔드포인트
        method: HTTP 메서드
        status_code: 응답 상태 코드
        execution_time: 실행 시간 (초)
    """
    log_msg = f"{method} {endpoint} - Status: {status_code}"
    if execution_time:
        log_msg += f" - Time: {execution_time:.3f}s"
    
    if status_code >= 500:
        logger.error(log_msg)
    elif status_code >= 400:
        logger.warning(log_msg)
    else:
        logger.info(log_msg)

def log_db_operation(operation: str, table: str, success: bool, error: str = None):
    """
    데이터베이스 작업 로그 기록
    
    Args:
        operation: 작업 종류 (SELECT, INSERT, UPDATE, DELETE)
        table: 테이블명
        success: 성공 여부
        error: 에러 메시지 (실패 시)
    """
    log_msg = f"DB {operation} on {table}"
    
    if success:
        logger.info(f"{log_msg} - SUCCESS")
    else:
        logger.error(f"{log_msg} - FAILED: {error}")

def log_ml_operation(model_name: str, operation: str, success: bool, metrics: dict = None, error: str = None):
    """
    ML 작업 로그 기록
    
    Args:
        model_name: 모델명
        operation: 작업 종류 (train, predict, evaluate)
        success: 성공 여부
        metrics: 성능 메트릭 (성공 시)
        error: 에러 메시지 (실패 시)
    """
    log_msg = f"ML {operation} - {model_name}"
    
    if success:
        if metrics:
            metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics.items()])
            logger.info(f"{log_msg} - SUCCESS - {metrics_str}")
        else:
            logger.info(f"{log_msg} - SUCCESS")
    else:
        logger.error(f"{log_msg} - FAILED: {error}")

def get_korea_time() -> datetime:
    """
    한국 시간 조회
    
    Returns:
        한국 시간 datetime 객체
    """
    korea_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(korea_tz)

def format_korea_time(dt: datetime = None, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    한국 시간 포맷팅
    
    Args:
        dt: datetime 객체 (None이면 현재 시간)
        format_string: 포맷 문자열
    
    Returns:
        포맷된 시간 문자열
    """
    if dt is None:
        dt = get_korea_time()
    return dt.strftime(format_string)

# 유틸리티 모듈 통합

# 상수 및 기본 데이터
from .constants import (
    SPECIES, SPECIES_MAPPING, CATTLE_LARGE_PARTS, PIG_LARGE_PARTS,
    CATTLE_SMALL_PARTS, PIG_SMALL_PARTS, MEAT_GRADES, PROCESSING_STATUS,
    APPROVAL_STATUS, get_species_id, get_species_name, get_large_parts,
    get_small_parts, get_meat_grades
)

# 로깅 시스템
from .logging_utils import (
    setup_logger, get_logger, log_api_call, log_db_operation,
    log_ml_operation, get_korea_time, format_korea_time, logger
)

# 데이터 검증 및 변환
from .validation import (
    safe_str, safe_int, safe_float, safe_bool, safe_json,
    convert_to_datetime, convert_to_string, validate_date_range,
    validate_email, validate_phone, sanitize_filename, truncate_string,
    normalize_whitespace, auto_convert_field, DEFAULT_USER_ID, DEFAULT_USER_TYPE
)

# 에러 핸들링
from .error_handlers import (
    APIError, ValidationError, DatabaseError, NotFoundError,
    UnauthorizedError, ForbiddenError, ConflictError,
    create_error_response, create_success_response,
    handle_database_error, handle_validation_error,
    safe_execute, validate_required_fields
)

# 기존 유틸리티 (하위 호환성)
from .ml_utils import *
from .opencv_utils import *
from .segmentation import *

# 하위 호환성을 위한 별칭
species = SPECIES
cattleLarge = CATTLE_LARGE_PARTS
pigLarge = PIG_LARGE_PARTS
cattleSmall = CATTLE_SMALL_PARTS
pigSmall = PIG_SMALL_PARTS
default_user_id = DEFAULT_USER_ID
default_user_type = DEFAULT_USER_TYPE
convert2datetime = convert_to_datetime

__all__ = [
    # 상수
    'SPECIES', 'SPECIES_MAPPING', 'CATTLE_LARGE_PARTS', 'PIG_LARGE_PARTS',
    'CATTLE_SMALL_PARTS', 'PIG_SMALL_PARTS', 'MEAT_GRADES', 'PROCESSING_STATUS',
    'APPROVAL_STATUS',
    
    # 상수 함수
    'get_species_id', 'get_species_name', 'get_large_parts', 'get_small_parts', 'get_meat_grades',
    
    # 로깅
    'setup_logger', 'get_logger', 'log_api_call', 'log_db_operation', 'log_ml_operation',
    'get_korea_time', 'format_korea_time', 'logger',
    
    # 검증/변환
    'safe_str', 'safe_int', 'safe_float', 'safe_bool', 'safe_json',
    'convert_to_datetime', 'convert_to_string', 'validate_date_range',
    'validate_email', 'validate_phone', 'sanitize_filename', 'truncate_string',
    'normalize_whitespace', 'auto_convert_field', 'DEFAULT_USER_ID', 'DEFAULT_USER_TYPE',
    
    # 에러 핸들링
    'APIError', 'ValidationError', 'DatabaseError', 'NotFoundError',
    'UnauthorizedError', 'ForbiddenError', 'ConflictError',
    'create_error_response', 'create_success_response',
    'handle_database_error', 'handle_validation_error',
    'safe_execute', 'validate_required_fields',
    
    # 하위 호환성
    'species', 'cattleLarge', 'pigLarge', 'cattleSmall', 'pigSmall',
    'default_user_id', 'default_user_type', 'convert2datetime'
]




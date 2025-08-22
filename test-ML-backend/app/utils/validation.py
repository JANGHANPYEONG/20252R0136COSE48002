"""
데이터 검증 및 변환 유틸리티
"""

from datetime import datetime
from typing import Any, Optional, Dict, Union
import json
import pytz

def safe_str(val: Any) -> Optional[str]:
    """
    안전한 문자열 변환
    
    Args:
        val: 변환할 값
    
    Returns:
        문자열 또는 None
    """
    try:
        if val is not None:
            return str(val)
        else:
            return None
    except Exception:
        return None

def safe_int(val: Any) -> Optional[int]:
    """
    안전한 정수 변환
    
    Args:
        val: 변환할 값
    
    Returns:
        정수 또는 None
    """
    try:
        return int(val)
    except (ValueError, TypeError):
        return None

def safe_float(val: Any) -> Optional[float]:
    """
    안전한 실수 변환
    
    Args:
        val: 변환할 값
    
    Returns:
        실수 또는 None
    """
    try:
        return float(val)
    except (ValueError, TypeError):
        return None

def safe_bool(val: Any) -> Optional[bool]:
    """
    안전한 불린 변환
    
    Args:
        val: 변환할 값
    
    Returns:
        불린 또는 None
    """
    try:
        return bool(val)
    except (ValueError, TypeError):
        return None

def safe_json(val: Any) -> Optional[Dict]:
    """
    안전한 JSON 변환
    
    Args:
        val: 변환할 값
    
    Returns:
        딕셔너리 또는 None
    """
    try:
        if isinstance(val, dict):
            return val
        elif isinstance(val, str):
            return json.loads(val)
        else:
            return None
    except (ValueError, TypeError, json.JSONDecodeError):
        return None

def convert_to_datetime(date_string: str, format_type: int = 0) -> Optional[datetime]:
    """
    문자열을 datetime으로 변환
    
    Args:
        date_string: 날짜/시간 문자열
        format_type: 포맷 타입
            0: "%Y-%m-%dT%H:%M:%S"
            1: 현재 한국 시간
            2: "%Y%m%d"
    
    Returns:
        datetime 객체 또는 None
    """
    if date_string is None:
        return None
    
    try:
        if format_type == 0:
            return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
        elif format_type == 1:
            tz = pytz.timezone("Asia/Seoul")
            return datetime.now(tz)
        elif format_type == 2:
            return datetime.strptime(date_string, "%Y%m%d")
        else:
            return None
    except (ValueError, TypeError):
        return None

def convert_to_string(date_object: datetime, format_type: int = 1) -> Optional[str]:
    """
    datetime을 문자열로 변환
    
    Args:
        date_object: datetime 객체
        format_type: 포맷 타입
            1: "%Y-%m-%dT%H:%M:%S"
            2: "%Y%m%d"
    
    Returns:
        문자열 또는 None
    """
    if date_object is None:
        return None
    
    try:
        if format_type == 1:
            return date_object.strftime("%Y-%m-%dT%H:%M:%S")
        elif format_type == 2:
            return date_object.strftime("%Y%m%d")
        else:
            return str(date_object)
    except Exception:
        return None

def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    날짜 범위 검증
    
    Args:
        start_date: 시작 날짜 (YYYY-MM-DD)
        end_date: 종료 날짜 (YYYY-MM-DD)
    
    Returns:
        유효한 범위인지 여부
    """
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        return start <= end
    except (ValueError, TypeError):
        return False

def validate_email(email: str) -> bool:
    """
    이메일 형식 검증
    
    Args:
        email: 이메일 주소
    
    Returns:
        유효한 이메일인지 여부
    """
    import re
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    전화번호 형식 검증 (한국)
    
    Args:
        phone: 전화번호
    
    Returns:
        유효한 전화번호인지 여부
    """
    import re
    if not phone:
        return False
    
    # 한국 전화번호 패턴
    pattern = r'^(010|011|016|017|018|019)-?\d{3,4}-?\d{4}$'
    return re.match(pattern, phone.replace('-', '')) is not None

def sanitize_filename(filename: str) -> str:
    """
    파일명 안전화 (특수문자 제거)
    
    Args:
        filename: 원본 파일명
    
    Returns:
        안전한 파일명
    """
    import re
    if not filename:
        return "unknown"
    
    # 위험한 문자 제거
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 연속된 언더스코어 제거
    sanitized = re.sub(r'_+', '_', sanitized)
    # 앞뒤 공백 및 점 제거
    sanitized = sanitized.strip(' .')
    
    return sanitized if sanitized else "unknown"

def truncate_string(text: str, max_length: int = 255) -> str:
    """
    문자열 길이 제한
    
    Args:
        text: 원본 텍스트
        max_length: 최대 길이
    
    Returns:
        길이가 제한된 텍스트
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def normalize_whitespace(text: str) -> str:
    """
    공백 정규화 (연속 공백 제거, 앞뒤 공백 제거)
    
    Args:
        text: 원본 텍스트
    
    Returns:
        정규화된 텍스트
    """
    import re
    if not text:
        return ""
    
    # 연속 공백을 하나로 변경
    normalized = re.sub(r'\s+', ' ', text)
    # 앞뒤 공백 제거
    return normalized.strip()

# 기본 상수들
DEFAULT_USER_ID = 'deeplant@example.com'
DEFAULT_USER_TYPE = 2

# 데이터 타입별 변환 매핑
DATETIME_FIELDS = {
    0: ["filmedAt", "createdAt"],
    1: ["loginAt", "updatedAt"], 
    2: ["butcheryYmd", "birthYmd", "date"]
}

STRING_FIELDS = [
    "id", "userId", "traceNum", "farmAddr", "farmerName", "name", 
    "company", "jobTitle", "homeAddr", "imagePath", "xai_imagePath", 
    "xai_gradeNum_imagePath"
]

INTEGER_FIELDS = ["period", "minute", "seqno", "isCompleted"]

FLOAT_FIELDS = [
    "marbling", "color", "texture", "surfaceMoisture", "overall", 
    "flavor", "juiciness", "umami", "palatability", "L", "a", "b", 
    "DL", "CL", "RW", "ph", "WBSF", "cardepsin_activity", "MFI", 
    "Collagen", "sourness", "bitterness", "richness"
]

JSON_FIELDS = ["tenderness"]
BOOLEAN_FIELDS = ["alarm", "isHeated"]

def auto_convert_field(data_dict: Dict, field_name: str, input_data: Any = None) -> Dict:
    """
    필드명에 따른 자동 타입 변환
    
    Args:
        data_dict: 데이터 딕셔너리
        field_name: 필드명
        input_data: 입력 데이터 (옵션)
    
    Returns:
        변환된 데이터 딕셔너리
    """
    value = data_dict.get(field_name)
    
    # datetime 변환
    for format_type, fields in DATETIME_FIELDS.items():
        if field_name in fields:
            data_dict[field_name] = convert_to_datetime(value, format_type)
            return data_dict
    
    # 기타 타입 변환
    if field_name in STRING_FIELDS:
        data_dict[field_name] = safe_str(value)
    elif field_name in INTEGER_FIELDS:
        data_dict[field_name] = safe_int(value)
    elif field_name in FLOAT_FIELDS:
        data_dict[field_name] = safe_float(value)
    elif field_name in JSON_FIELDS:
        data_dict[field_name] = safe_json(value)
    elif field_name in BOOLEAN_FIELDS:
        data_dict[field_name] = safe_bool(value)
    
    return data_dict

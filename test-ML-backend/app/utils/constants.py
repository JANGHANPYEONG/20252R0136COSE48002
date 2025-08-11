"""
축산물 관련 기본 데이터 상수들
"""

# 축종 정보
SPECIES = ["소", "돼지"]
SPECIES_MAPPING = {
    "cattle": 0,
    "pig": 1,
    "소": 0,
    "돼지": 1
}

# 소 대분류 부위
CATTLE_LARGE_PARTS = [
    "안심",
    "등심", 
    "채끝",
    "목심",
    "앞다리",
    "우둔",
    "설도",
    "양지",
    "사태",
    "갈비",
]

# 돼지 대분류 부위
PIG_LARGE_PARTS = [
    "안심",
    "등심",
    "목심",
    "앞다리",
    "갈비",
    "삼겹살",
    "뒷다리",
]

# 소 소분류 부위 (대분류 인덱스별)
CATTLE_SMALL_PARTS = {
    0: ["안심살"],
    1: [
        "윗등심",
        "꽃등심",
        "아래등심",
        "살치살",
    ],
    2: ["채끝살"],
    3: ["목심살"],
    4: [
        "꾸리살",
        "부채살",
        "앞다리살",
        "갈비덧살",
        "부채덮개살",
    ],
    5: [
        "우둔살",
        "홍두깨살",
    ],
    6: [
        "보섭살",
        "설깃살",
        "설깃머리살",
        "도가니살",
        "삼각살",
    ],
    7: [
        "양지머리",
        "차돌박이",
        "업진살",
        "업진안살",
        "치마양지",
        "치마살",
        "앞치마살",
    ],
    8: [
        "앞사태",
        "뒷사태",
        "뭉치사태",
    ],
    9: [
        "본갈비",
        "꽃갈비",
        "참갈비",
        "갈빗살",
        "마구리",
        "토시살",
        "안창살",
        "제비추리",
    ],
}

# 돼지 소분류 부위 (대분류 인덱스별)
PIG_SMALL_PARTS = {
    0: ["안심살"],
    1: [
        "등심살",
        "등심덧살",
    ],
    2: ["목심살"],
    3: [
        "앞다리살",
        "앞사태살",
        "항정살",
        "꾸리살",
        "부채살",
    ],
    4: [
        "갈비",
        "갈비살",
        "마구리",
        "토시살",
        "안창살",
        "제비추리",
    ],
    5: [
        "삼겹살",
        "갈매기살",
        "오돌삼겹",
        "브리스킷",
    ],
    6: [
        "뒷다리살",
        "볼기살",
        "설깃살",
        "도가니살",
        "홍두깨살",
        "보섭살",
        "뒷사태살",
    ],
}

# 등급 정보
MEAT_GRADES = {
    "cattle": ["1++", "1+", "1", "2", "3"],
    "pig": ["1+", "1", "2"]
}

# 처리 상태
PROCESSING_STATUS = {
    0: "신선육",
    1: "숙성육"
}

# 승인 상태
APPROVAL_STATUS = {
    0: "대기",
    1: "승인", 
    2: "거부"
}

def get_species_id(species_name: str) -> int:
    """축종명으로 ID 조회"""
    return SPECIES_MAPPING.get(species_name, -1)

def get_species_name(species_id: int) -> str:
    """축종 ID로 이름 조회"""
    if 0 <= species_id < len(SPECIES):
        return SPECIES[species_id]
    return "unknown"

def get_large_parts(species_id: int) -> list:
    """축종별 대분류 부위 조회"""
    if species_id == 0:
        return CATTLE_LARGE_PARTS.copy()
    elif species_id == 1:
        return PIG_LARGE_PARTS.copy()
    return []

def get_small_parts(species_id: int, large_part_id: int) -> list:
    """축종별 소분류 부위 조회"""
    if species_id == 0:
        return CATTLE_SMALL_PARTS.get(large_part_id, [])
    elif species_id == 1:
        return PIG_SMALL_PARTS.get(large_part_id, [])
    return []

def get_meat_grades(species_name: str) -> list:
    """축종별 등급 조회"""
    return MEAT_GRADES.get(species_name, [])

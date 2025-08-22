/**
 * 축산물 관련 기본 데이터 상수들
 */

// 축종 정보
export const SPECIES = ["소", "돼지"];
export const SPECIES_MAPPING = {
    "cattle": 0,
    "pig": 1,
    "소": 0,
    "돼지": 1
};

// 소 대분류 부위
export const CATTLE_LARGE_PARTS = [
    "안심",     // 00
    "등심",     // 01 
    "채끝",     // 02
    "목심",     // 03
    "앞다리",   // 04
    "우둔",     // 05
    "설도",     // 06
    "양지",     // 07
    "사태",     // 08
    "갈비",     // 09
];

// 돼지 대분류 부위
export const PIG_LARGE_PARTS = [
    "안심",     // 10
    "등심",     // 11
    "목심",     // 12
    "앞다리",   // 13
    "갈비",     // 14
    "삼겹살",   // 15
    "뒷다리",   // 16
];

// 소 소분류 부위 (대분류 인덱스별)
export const CATTLE_SMALL_PARTS = {
    0: ["안심살"],                                  // 000
    1: [                                           // 01X
        "윗등심",       // 010
        "꽃등심",       // 011
        "아래등심",     // 012
        "살치살",       // 013
    ],
    2: ["채끝살"],                                  // 020
    3: ["목심살"],                                  // 030
    4: [                                           // 04X
        "꾸리살",       // 040
        "부채살",       // 041
        "앞다리살",     // 042
        "갈비덧살",     // 043
        "부채덮개살",   // 044
    ],
    5: [                                           // 05X
        "우둔살",       // 050
        "홍두깨살",     // 051
    ],
    6: [                                           // 06X
        "보섭살",       // 060
        "설깃살",       // 061
        "설깃머리살",   // 062
    ],
    7: [                                           // 07X
        "뒷다리살",     // 070
        "볼기살",       // 071
        "설깃살",       // 072
        "도가니살",     // 073
        "홍두깨살",     // 074
        "보섭살",       // 075
        "뒷사태살",     // 076
    ],
};

// 돼지 소분류 부위 (대분류 인덱스별)
export const PIG_SMALL_PARTS = {
    0: ["안심살"],                                  // 100
    1: [                                           // 11X
        "윗등심",       // 110
        "아래등심",     // 111
    ],
    2: ["목심살"],                                  // 120
    3: [                                           // 13X
        "앞다리살",     // 130
        "앞사태살",     // 131
    ],
    4: [                                           // 14X
        "갈비살",       // 140
        "등갈비",       // 141
    ],
    5: ["삼겹살"],                                  // 150
    6: [                                           // 16X
        "뒷다리살",     // 160
        "볼기살",       // 161
        "뒷사태살",     // 162
    ],
};

/**
 * 축종명으로 ID 조회
 */
export function getSpeciesId(speciesName) {
    return SPECIES_MAPPING[speciesName] ?? -1;
}

/**
 * 축종 ID로 이름 조회
 */
export function getSpeciesName(speciesId) {
    if (0 <= speciesId && speciesId < SPECIES.length) {
        return SPECIES[speciesId];
    }
    return "unknown";
}

/**
 * 축종별 대분류 부위 조회
 */
export function getLargeParts(speciesId) {
    if (speciesId === 0) {
        return CATTLE_LARGE_PARTS.slice();
    } else if (speciesId === 1) {
        return PIG_LARGE_PARTS.slice();
    }
    return [];
}

// 부위명 → categoryId 직접 매핑 딕셔너리
const PART_TO_CATEGORY_MAP = {
    // 소 대분류 (00-09) - 중복되지 않는 것들만
    "채끝": "02",
    "양지": "07",
    "사태": "08",
    
    // 소 소분류 (000-099)
    "안심살": "000",
    "윗등심": "010",     // 소 소분류
    "꽃등심": "011",
    "아래등심": "012",   // 소 소분류
    "살치살": "013",
    "채끝살": "020",
    "목심살": "030",
    "꾸리살": "040",
    "부채살": "041",
    "앞다리살": "042",
    "갈비덧살": "043",
    "부채덮개살": "044",
    "우둔살": "050",
    "홍두깨살": "051",
    "보섭살": "060",
    "설깃살": "061",
    "설깃머리살": "062",
    "뒷다리살": "070",
    "볼기살": "071",
    "도가니살": "073",
    "뒷사태살": "076",
    
    // 돼지 대분류 (10-16) - 중복 부위는 돼지 우선
    "안심": "10",       // 돼지 우선
    "등심": "11",       // 돼지 우선
    "목심": "12",       // 돼지 우선
    "앞다리": "13",     // 돼지 우선
    "갈비": "14",       // 돼지 우선
    "삼겹살": "15",
    "뒷다리": "16",
    
    // 돼지 소분류 (100-199)
    "윗등심": "110",    // 돼지 소분류 우선 (소와 중복)
    "아래등심": "111",  // 돼지 소분류 우선 (소와 중복)
    "목심살": "120",    // 돼지 소분류
    "앞다리살": "130",  // 돼지 소분류 우선 (소와 중복)
    "앞사태살": "131",
    "갈비살": "140",
    "등갈비": "141",
    "뒷다리살": "160",  // 돼지 소분류 우선 (소와 중복)
    "볼기살": "161",    // 돼지 소분류 우선 (소와 중복)
    "뒷사태살": "162",  // 돼지 소분류 우선 (소와 중복)
};

/**
 * 부위명으로 categoryId 생성
 * @param {string} partName - 부위명 (예: '목심', '삼겹살', '채끝살')
 * @param {string} speciesName - 축종명 (예: '소', '돼지') - 선택적, 없으면 딕셔너리 우선순위 따름
 * @returns {number} - categoryId (예: 12, 15, 020)
 */
export function getCategoryId(partName, speciesName = null) {
    if (!partName) return -1;
    
    const trimmedPartName = partName.trim();
    
    // 직접 매핑 딕셔너리에서 찾기
    if (PART_TO_CATEGORY_MAP[trimmedPartName]) {
        const categoryIdStr = PART_TO_CATEGORY_MAP[trimmedPartName];
        return parseInt(categoryIdStr, 10);
    }
    
    // 축종을 명시적으로 지정했을 경우 해당 축종에서만 검색
    if (speciesName) {
        const speciesId = getSpeciesId(speciesName);
        return getCategoryIdBySpecies(trimmedPartName, speciesId);
    }
    
    return -1; // 찾지 못함
}

/**
 * 특정 축종에서 부위명으로 categoryId 검색
 */
function getCategoryIdBySpecies(partName, speciesId) {
    if (speciesId === 0) { // 소
        // 대분류에서 검색
        const largeIndex = CATTLE_LARGE_PARTS.indexOf(partName);
        if (largeIndex !== -1) {
            return largeIndex; // 00-09
        }
        
        // 소분류에서 검색
        for (const [largeIdx, smallParts] of Object.entries(CATTLE_SMALL_PARTS)) {
            const smallIndex = smallParts.indexOf(partName);
            if (smallIndex !== -1) {
                return parseInt(largeIdx) * 10 + smallIndex; // 010, 011, 012...
            }
        }
    } else if (speciesId === 1) { // 돼지
        // 대분류에서 검색
        const largeIndex = PIG_LARGE_PARTS.indexOf(partName);
        if (largeIndex !== -1) {
            return 10 + largeIndex; // 10-16
        }
        
        // 소분류에서 검색
        for (const [largeIdx, smallParts] of Object.entries(PIG_SMALL_PARTS)) {
            const smallIndex = smallParts.indexOf(partName);
            if (smallIndex !== -1) {
                return 100 + parseInt(largeIdx) * 10 + smallIndex; // 110, 111, 120...
            }
        }
    }
    
    return -1;
}

/**
 * categoryId로 부위명 직접 조회 (역매핑)
 * @param {number} categoryId - categoryId (예: 12, 15, 020)
 * @returns {string} - 부위명 (예: '목심', '삼겹살', '채끝살')
 */
export function getPartNameFromCategoryId(categoryId) {
    // 딕셔너리에서 역검색
    for (const [partName, categoryIdStr] of Object.entries(PART_TO_CATEGORY_MAP)) {
        if (parseInt(categoryIdStr, 10) === categoryId) {
            return partName;
        }
    }
    
    // 딕셔너리에 없는 경우 기존 로직으로 fallback
    const categoryInfo = getCategoryInfo(categoryId);
    return categoryInfo.partName;
}

/**
 * categoryId로 축종 및 부위명 조회
 */
export function getCategoryInfo(categoryId) {
    if (categoryId >= 100) { // 돼지 (100-199)
        const adjustedId = categoryId - 100;
        const largeIdx = Math.floor(adjustedId / 10);
        const smallIdx = adjustedId % 10;
        
        if (smallIdx === 0 && largeIdx < PIG_LARGE_PARTS.length) {
            // 대분류
            return {
                species: "돼지",
                speciesId: 1,
                partName: PIG_LARGE_PARTS[largeIdx],
                isLargePart: true
            };
        } else if (PIG_SMALL_PARTS[largeIdx] && PIG_SMALL_PARTS[largeIdx][smallIdx]) {
            // 소분류
            return {
                species: "돼지",
                speciesId: 1,
                partName: PIG_SMALL_PARTS[largeIdx][smallIdx],
                isLargePart: false,
                largePart: PIG_LARGE_PARTS[largeIdx]
            };
        }
    } else if (categoryId >= 10) { // 돼지 대분류 (10-16)
        const largeIdx = categoryId - 10;
        if (largeIdx < PIG_LARGE_PARTS.length) {
            return {
                species: "돼지",
                speciesId: 1,
                partName: PIG_LARGE_PARTS[largeIdx],
                isLargePart: true
            };
        }
    } else if (categoryId >= 0) { // 소 (0-99)
        if (categoryId < 10) {
            // 소 대분류 (0-9)
            if (categoryId < CATTLE_LARGE_PARTS.length) {
                return {
                    species: "소",
                    speciesId: 0,
                    partName: CATTLE_LARGE_PARTS[categoryId],
                    isLargePart: true
                };
            }
        } else {
            // 소 소분류 (10-99)
            const largeIdx = Math.floor(categoryId / 10);
            const smallIdx = categoryId % 10;
            
            if (CATTLE_SMALL_PARTS[largeIdx] && CATTLE_SMALL_PARTS[largeIdx][smallIdx]) {
                return {
                    species: "소",
                    speciesId: 0,
                    partName: CATTLE_SMALL_PARTS[largeIdx][smallIdx],
                    isLargePart: false,
                    largePart: CATTLE_LARGE_PARTS[largeIdx]
                };
            }
        }
    }
    
    return {
        species: "unknown",
        speciesId: -1,
        partName: "unknown",
        isLargePart: false
    };
}
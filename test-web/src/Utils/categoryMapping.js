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

/**
 * 부위명으로 categoryId 생성
 * @param {string} partName - 부위명 (예: '목심', '삼겹살', '윗등심')
 * @param {string} speciesName - 축종명 (예: '소', '돼지') - 선택적, 없으면 자동 추론
 * @returns {number} - categoryId (예: 03, 150, 010)
 */
export function getCategoryId(partName, speciesName = null) {
    if (!partName) return -1;
    
    const trimmedPartName = partName.trim();
    
    // 축종을 명시적으로 지정했을 경우
    if (speciesName) {
        const speciesId = getSpeciesId(speciesName);
        return getCategoryIdBySpecies(trimmedPartName, speciesId);
    }
    
    // 축종이 명시되지 않은 경우 모든 축종에서 검색
    // 소에서 먼저 검색
    let categoryId = getCategoryIdBySpecies(trimmedPartName, 0);
    if (categoryId !== -1) return categoryId;
    
    // 돼지에서 검색
    categoryId = getCategoryIdBySpecies(trimmedPartName, 1);
    if (categoryId !== -1) return categoryId;
    
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
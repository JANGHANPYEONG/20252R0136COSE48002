# MeatDetailPage 업그레이드 요구사항

## 현재 상황 분석

### API 응답 구조

```json
{
  "id": "ec711d89741eec656cf3",
  "meat": { ... },
  "deepAging": { "seqnos": [0] },
  "by_seqno_and_condition": [
    {
      "seqno": 0,
      "isRefrigerated": false,  // 0일차 (냉장)
      "sensory_eval": { ... },
      "ai_sensory_eval": { ... },
      "hsi_sensory_eval": { ... },
      "ai_hsi_sensory_eval": { ... },
      "hsi_images_bands": [
        {
          "spectral_index": 0,
          "filename": "ec711d89741eec656cf3_430nm.png",
          "topLeft": [1992, 941],
          "topRight": [2644, 941],
          "bottomRight": [2644, 1798],
          "bottomLeft": [1992, 1798]
        }
      ]
    }
  ]
}
```

### 테이블 구조 분석

- **Meat**: 기본 육류 정보
- **DeepAgingInfo**: seqno별 가공 정보
- **SensoryEval**: 관능검사 (seqno + isRefrigerated 조합)
- **AI_SensoryEval**: AI 예측값
- **HSISensoryEval**: HSI 관능검사
- **AI_HSISensoryEval**: HSI AI 예측값
- **HSIImagesBands**: 파장별 HSI 이미지 (spectral_index로 구분)

## 요구사항

### 1. HSI 이미지 표시

- 0일차 (isRefrigerated: false)와 7일차 (isRefrigerated: true) 이미지 표시
- 각 일차별로 파장별 HSI 이미지를 슬라이더로 표시
- `hsi_images_bands` 배열의 각 항목을 이미지로 렌더링

### 2. seqno별 탭 분리

- `deepAging.seqnos` 배열을 기반으로 탭 생성
- 각 탭은 해당 seqno의 데이터를 표시
- 현재는 seqno: 0만 있지만 확장 가능하도록 설계

### 3. 이미지 표시 방식

- 좌측: HSI 이미지 영역 (파장별 슬라이더)
- 우측: 상세정보 및 비교표
- 하단: 분석 그래프

## 구현 계획

### Phase 1: 데이터 구조 정규화 개선

- `normalizeItemFromBackend` 함수에서 HSI 이미지 데이터 처리 로직 추가
- `hsi_images_bands` 데이터를 이미지 경로와 함께 정규화

### Phase 2: UI 컴포넌트 추가

- HSI 이미지 슬라이더 컴포넌트 생성
- seqno별 탭 컴포넌트 생성
- 이미지 표시 영역 레이아웃 조정

### Phase 3: 데이터 바인딩

- 정규화된 HSI 데이터를 UI에 연결
- 파장별 이미지 전환 기능 구현
- 일차별 데이터 비교 표시

### Phase 4: 사용자 경험 개선

- 이미지 로딩 상태 표시
- 에러 처리 및 폴백 UI
- 반응형 레이아웃 최적화

## 기술적 고려사항

### 이미지 처리

- HSI 이미지는 `hsi_images_bands`의 `filename` 필드로 접근
- 이미지 경로는 S3 또는 로컬 서버에서 가져와야 함
- 이미지 로딩 실패 시 대체 UI 제공

### 성능 최적화

- 이미지 lazy loading 구현
- 파장별 이미지 캐싱
- 메모리 사용량 최적화

### 확장성

- 새로운 seqno 추가 시 자동 탭 생성
- 새로운 파장 추가 시 자동 슬라이더 업데이트
- 데이터 구조 변경 시 하위 호환성 유지

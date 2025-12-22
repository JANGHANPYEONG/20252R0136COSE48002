# test-web (DeePlant Web Frontend)

`test-web`는 DeePlant 서비스의 React 기반 프론트엔드입니다.
- CRA(react-scripts)로 개발/빌드
- 백엔드(ML/대시보드/업로드) API 호출
- 예측(Predict) 기능은 전역 진행/결과 알림(모달)로 UX 제공
- 로컬 개발 시 JSON 파일을 `test-data/result`에 저장하기 위한 보조 서버 제공

> 참고: 이 폴더에는 이미 `build/`가 포함되어 있으며, `server.js`는 해당 `build/`를 정적으로 서빙하면서 `/api/*`를 백엔드로 프록시하는 용도입니다.

---

## 빠른 시작

### 1) 의존성 설치

```bash
cd test-web
npm install
```

### 2) 프론트 개발 서버 실행

```bash
npm start
```

- 기본적으로 CRA 개발 서버가 실행됩니다(통상 `http://localhost:3000`).

### 3) (선택) 로컬 JSON 저장 서버 실행

엑셀→JSON 변환 결과를 로컬 폴더에 저장하고 싶다면 아래 서버를 함께 실행합니다.

```bash
npm run json-server
```

- 실행 파일: `local-json-server.js`
- 포트: `3001`
- 저장 위치: `test-web/test-data/result/` (실행 시 자동 생성)

---

## NPM 스크립트

`package.json` 기준:

- `npm start`: 개발 서버 실행
- `npm run build`: 프로덕션 빌드 생성(`build/`)
- `npm test`: 테스트 실행
- `npm run deploy`: `react-scripts build && firebase deploy` (Firebase CLI 및 설정 필요)
- `npm run json-server`: 로컬 JSON 저장 서버 실행 (`local-json-server.js`)

---

## 실행/배포 구성

### A. 개발 모드 (권장)

- `npm start`로 React 개발 서버를 사용합니다.
- 백엔드 API 주소는 주로 `src/config.js`의 `apiIP`를 사용합니다.

### B. 빌드 산출물 서빙 + API 프록시 (선택)

`server.js`는 Express로 `build/`를 서빙하며 `/api/*` 요청을 백엔드로 프록시합니다.

- 정적 서빙: `express.static(build)`
- 헬스체크: `GET /ping` → `pong`
- 프록시: `GET /api/*` → `http://${REACT_APP_SERVER_API}:${REACT_APP_SERVER_PORT}/*`

필요 환경변수(예시):

```dotenv
# server.js에서 사용
REACT_APP_PORT=5000
REACT_APP_SERVER_API=127.0.0.1
REACT_APP_SERVER_PORT=8000
```

> 주의: CRA 관례상 `REACT_APP_`는 프론트 번들 환경변수 prefix지만, 이 프로젝트에서는 `server.js`(Node 런타임)에서도 동일 prefix를 사용합니다.

---

## 백엔드 API 연결

### 기본 API 호스트

- `src/config.js`의 `apiIP`가 기본 백엔드 호스트로 사용됩니다.
  - 예: `export const apiIP = '3.38.117.43:8000';`

### 예측(Predict) 관련 API

- 개별 데이터 조회: `POST http://${apiIP}/dashboard/dashboard/individual` (body: `{ id }`)
- 예측 호출: `POST http://${apiIP}/hsipredict` (body: `{ id, seqno, isRefrigerated }`)

구현 위치:
- 예측 오케스트레이션: `src/API/predictData.js`
- 페이지(UI): `src/routes/Predict.js`

---

## 주요 기능 요약

### 1) Predict (AI Prediction)

- 사용자가 테이블에서 여러 항목을 선택 후 “예측” 실행
- 선택된 각 `id`에 대해 먼저 개별 데이터(`by_seqno_and_condition`)를 조회
- 조회된 `(id, seqno, isRefrigerated)` 조합별로 `/hsipredict`를 순차 호출
- 진행률/상태는 전역 컨텍스트로 관리되어 **다른 페이지로 이동해도 우측 상단 알림 형태로 유지**

관련 구성:
- 전역 상태: `src/context/PredictionContext.jsx`
- 전역 모달 마운트: `src/components/GlobalPredictionModals.jsx` (App 최상위에 항상 렌더링)
- 진행 모달: `src/components/PredictionProgressModal.jsx`
- 결과 모달: `src/components/PredictionResultModal.jsx`
- XAI 뷰어: `src/components/XAIViewer.jsx`

- 예측 API
  - Request: `{ id, seqno, isRefrigerated }`
  - Response: `predictions`(배열), `xai_image_urls`(S3 경로), `created_at`
- 예측 흐름
  - Dashboard/목록에서 선택한 각 `id`에 대해 개별 데이터 조회 후, `by_seqno_and_condition`의 모든 항목을 예측 대상으로 확장
  - 각 항목을 순차 처리하며 진행률(예: `2/11`)을 실시간 업데이트
- UX(오른쪽 상단 알림 형태)
  - 진행 상황/결과를 작은 알림 형태로 고정 표시
  - 최소화/최대화 가능
  - 페이지 이동 시에도 유지(전역 컨텍스트 + App 최상단 렌더)
  - 항목별 상태(대기/진행/완료/실패) 및 메시지 표시
  - 완료 시 결과 알림에서 ID별 그룹화 및 XAI 이미지 확인

### 2) DataRegister (데이터 등록 / 엑셀+이미지)

- 엑셀(XLSX)을 읽어 샘플 데이터 구성
- (옵션) ZIP 이미지가 있으면 압축 해제 후 개별 이미지 업로드 로직 수행
- JSON 생성/전송 로직이 여러 버전으로 존재하며, 최근 흐름은 “새로운 형식 JSON 생성 → BE 전송 → (옵션) 개별 이미지 업로드” 형태로 구성되어 있습니다.

#### 개별 이미지 업로드 구현

- 목표
  - 기존 “ZIP 통째 업로드” 방식에서 “ZIP 해제 → 개별 이미지 파일명 해싱 → presigned URL로 S3 직접 업로드” 방식으로 전환
- 주요 파일
  - `src/API/add/uploadIndividualImages.js`: 해시 파일명 생성, presigned URL 요청, S3 업로드, PNG→JPEG 변환
  - `src/components/ImageUploadProgress.js`: 업로드 진행률 UI
  - `src/routes/DataRegister.js`: 새 업로드 로직 통합 및 진행률 표시
- 로컬 저장(테스트)
  - 엑셀 데이터를 샘플별/통합 JSON으로 변환 후 `http://localhost:3001` 로컬 서버를 통해 `test-data/result`에 저장 가능
  - 로컬 서버 미실행 시 브라우저 다운로드로 폴백하는 로직이 존재
- BE 연동(업로드)
  - presigned URL 요청: `GET /upload/presigned-url?filename=...&content_type=image/jpeg`
  - presigned URL로 S3에 직접 업로드

로컬 JSON 저장(테스트/검증용):
- `src/API/add/newJsonConverter.js` 또는 `src/API/add/saveJsonToResult.js`에서 `http://localhost:3001/api/save-multiple-json` 호출
- 로컬 저장 서버는 `local-json-server.js`로 제공 (`npm run json-server`)

### 3) Meat Detail Page (상세 페이지 확장)

- `MEAT_DETAIL_PAGE_UPGRADE.md`에 API 응답 구조와 UI 확장 요구사항(HSI 이미지 밴드 슬라이더, seqno 탭 등) 정리
- 라우트: `/meat/:id`

#### MeatDetailPage 업그레이드 요구사항 요약 (MEAT_DETAIL_PAGE_UPGRADE.md)

- 데이터 구조
  - `deepAging.seqnos` 기반으로 seqno 탭 구성
  - `by_seqno_and_condition`에 seqno + 냉장/숙성 조건별 평가값과 `hsi_images_bands`(파장별 이미지/좌표)가 포함
- UI 요구사항
  - 좌측: HSI 이미지 영역(파장별 슬라이더)
  - 우측: 상세정보 및 비교표
  - 하단: 분석 그래프
- 기술 고려사항
  - 이미지 경로(S3 또는 로컬)와 로딩/에러 폴백
  - 성능: lazy loading, 캐싱, 메모리 최적화

  ### 4) Dashboard (데이터 관리/조회)

  - 기간/품종 등 필터 기반으로 데이터를 불러와 목록을 구성
  - 목록/현황/반려 데이터 등 탭 기반 뷰를 제공(구현은 페이지 및 컴포넌트 조합에 따라 달라질 수 있음)
  - 검색/필터 UI 제공
    - 필터 상태를 `localStorage`에 저장/복원하여 새로고침 후에도 유지
  - 데이터 그룹핑
    - 예: `butcheryYmd`(도축일자) 기준으로 배치처럼 묶어 표시
  - 선택된 항목을 Predict/Training 페이지로 전달
    - 선택한 `id` 목록을 전달하고, 새로고침 대비 `sessionStorage` 백업도 수행

  구현 위치(대표):
  - `src/routes/Dashboard.js`

  ### 5) Learning (AI Training)

  - 선택한 데이터(IDs)를 기반으로 모델 학습을 실행하는 페이지
  - HSI 학습
    - 선택한 `id` 리스트로 학습 시작 요청
    - 학습 상태를 주기적으로 조회(예: 10초 간격)하여 완료/실패를 UI에 반영
  - 학습 결과 히스토리
    - 결과를 `localStorage`에 저장하여 이전 학습 결과 비교표를 유지
  - 배포
    - 학습 결과를 히스토리에 누적한 뒤 배포 API 호출

  구현 위치(대표):
  - `src/routes/Learning.js` (HSI 학습 + 상태 폴링)
  - `src/routes/LearningRGB.js` (일부 학습은 백엔드 준비 전 MOCK 로직 포함)
  - `src/API/train/*`

---

## 폴더 구조 안내

- `src/routes/`
  - 페이지 단위 라우트 컴포넌트 (예: `Predict.js`, `DataRegister.js`, `MeatDetailPage.jsx`)
- `src/components/`
  - 재사용 UI 컴포넌트
  - 예측 전역 알림 모달/테이블/필터 등 포함
- `src/API/`
  - 백엔드 호출 유틸/도메인별 API 모듈
  - `add/`: 등록/업로드/JSON 변환
  - `predict/`: 예측 관련(일부는 `predictData.js`가 직접 담당)
- `src/context/`
  - 전역 상태(예: 예측 진행/결과) 관리
- `public/`
  - 정적 리소스, `index.html`
- `server.js`
  - `build/` 정적 서빙 + `/api/*` 프록시 (선택)
- `local-json-server.js`
  - 개발 편의용 로컬 파일 저장 API 서버 (JSON 저장/목록 조회)

---

## 로컬 JSON 저장 서버 API

`local-json-server.js` 기준:

- `POST /api/save-multiple-json`
  - body: `{ files: [{ fileName, content }] }`
- `POST /api/save-json`
  - body: `{ fileName, content }`
- `GET /api/saved-files`
  - 저장된 `.json` 파일 목록 반환

저장 위치:
- `test-web/test-data/result/`



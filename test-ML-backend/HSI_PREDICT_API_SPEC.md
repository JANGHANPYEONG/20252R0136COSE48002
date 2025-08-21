# HSI 예측 API 구현 명세서

## 1. API 구조

- **POST** `/hsipredict` - HSI 이미지 예측
- **POST** `/rgbpredict` - RGB 이미지 예측 (향후 구현)

## 2. HSI Predict API 요구사항

### 2.1 입력 (Request Body)

```json
{
  "id": "string",
  "seqno": "int",
  "isRefrigerated": "boolean"
}
```

### 2.2 처리 로직

1. **DB 조회**: `id`, `seqno`, `isRefrigerated`로 `hsi_images_bands` 테이블에서 모든 파장대 이미지 조회
2. **S3 이미지 다운로드**: `S3_BUCKET_NAME/train_dataset/HSI/` 경로에서 이미지 다운로드
3. **MLflow 모델 로드**: 특정 experiment에서 최신 `run_id`로 모델 로드
4. **예측 실행**: `predict_xai_hsi.py` 모듈로 예측 및 XAI 이미지 생성
5. **결과 저장**:
   - DB: `ai_hsi_sensory_eval` 테이블에 AI 예측값과 XAI 이미지 경로 저장
   - S3: XAI 이미지를 `hsi_xai_images/id/seqno/isRefrigerated/` 경로에 업로드

### 2.3 출력 (Response)

```json
{
  "predictions": ["float", "float", ...],
  "xai_image_urls": ["string", "string", ...]
}
```

## 3. 필요한 설정 파일

### 3.1 MLflow 설정

- `mlflow_config.json`에 experiment 이름 추가
- 최신 run_id 자동 조회 로직

### 3.2 캐싱 설정

- `cache_configs.json`에 캐싱 폴더 경로 및 설정 추가
- 이미지 캐싱 폴더: `predict_image_cache`
- XAI 이미지 캐싱 폴더: `xai_cache`

## 4. DB 테이블 구조

### 4.1 hsi_images_bands (복합키: id, seqno, isRefrigerated, spectral_index)

- spectral_index → spectral_info 테이블의 주키

### 4.2 spectral_info

- wavelength_nm: 파장 정보

### 4.3 hsi_sensory_eval (복합키: id, seqno, isRefrigerated)

- 정답값: marbling, color, texture, surfaceMoisture, overall
- 정답 이미지 경로: imagePath

### 4.4 ai_hsi_sensory_eval (복합키: id, seqno, isRefrigerated)

- AI 예측값: marbling, color, texture, surfaceMoisture, overall
- XAI 이미지 경로: xai_imagePath

## 5. 구현 순서

1. ✅ DB 모델 확인 및 테이블 구조 파악
2. ✅ 설정 파일 생성 (MLflow, 캐싱)
3. ✅ HSI Predict API 엔드포인트 생성
4. ✅ DB 조회 및 S3 다운로드 로직 구현
5. ✅ MLflow run_id 조회 로직 구현
6. ✅ predict_xai_hsi.py 연동
7. ✅ 결과 저장 (DB, S3) 로직 구현
8. 🔄 테스트 및 검증 (진행 중)

## 6. 구현 완료된 내용

### 6.1 API 엔드포인트

- **POST** `/hsipredict/` - HSI 이미지 예측 API

### 6.2 주요 기능

- DB에서 HSI 이미지 정보 조회 (`hsi_images_bands`, `spectral_info` 테이블)
- S3에서 이미지 다운로드 (기존 `s3_downloader` 모듈 활용)
- MLflow에서 최신 run_id 자동 조회
- `predict_xai_hsi.py` 스크립트 실행으로 예측 및 XAI 이미지 생성
- XAI 이미지를 S3에 업로드 (기존 `s3_uploader` 모듈 활용)
- 예측 결과를 DB에 저장 (`ai_hsi_sensory_eval` 테이블)

### 6.3 설정 파일

- `mlflow_config.json`: MLflow 설정 (experiment 이름, tracking URI 등)
- `cache_configs.json`: 캐싱 설정 (폴더 경로, 캐시 설정 등)
- 캐싱 폴더: `/tmp/hsi_predict_image_cache`, `/tmp/hsi_xai_cache`

### 6.4 테스트

- `test_hsi_predict.py`: API 테스트 스크립트

## 7. 사용 방법

### 7.1 서버 실행

```bash
cd test-ML-backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 7.2 API 호출

```bash
curl -X POST "http://localhost:8000/hsi_predict/" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_meat_001",
    "seqno": 1,
    "isRefrigerated": false
  }'
```

### 7.3 테스트 실행

```bash
cd test-ML-backend
python test_hsi_predict.py
```

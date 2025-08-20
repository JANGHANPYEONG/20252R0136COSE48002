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
   - DB: `hsi_sensory_eval` 테이블에 예측값과 XAI 이미지 경로 저장
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

- 이미지 캐싱 폴더 경로
- XAI 이미지 캐싱 폴더 경로

## 4. DB 테이블 구조

### 4.1 hsi_images_bands (복합키: id, seqno, isRefrigerated, spectral_index)

- spectral_index → spectral_info 테이블의 주키

### 4.2 spectral_info

- wavelength_nm: 파장 정보

### 4.3 hsi_sensory_eval (복합키: id, seqno, isRefrigerated)

- 예측값: marbling, color, texture, surfaceMoisture, overall
- XAI 이미지 경로: xai_imagePath

## 5. 구현 순서

1. DB 모델 확인 및 테이블 구조 파악
2. 설정 파일 생성 (MLflow, 캐싱)
3. HSI Predict API 엔드포인트 생성
4. DB 조회 및 S3 다운로드 로직 구현
5. MLflow run_id 조회 로직 구현
6. predict_xai_hsi.py 연동
7. 결과 저장 (DB, S3) 로직 구현
8. 테스트 및 검증

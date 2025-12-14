# 고려대학교 산학협력프로젝트 딥플랜트

<div align="center">
<img width="300" alt="image" src="https://raw.githubusercontent.com/SincerityHun/Deep_Plant1_Final/main/web/images/l_deeplant.png">
</div>

> 개발기간: 2025.06 ~ 
>
> Built with Python

## 프로젝트 개요

육류에 대한 고객/구매자의 맛에 대한 선호도(Tasty preference) 데이터를 육류 이미지와 분석된 미각 데이터로 나누어 체계적으로 수집하고 이를 기반으로 이미지 기반의 육류에 관한 상세한 맛 데이터를 자동으로 분류하고 예측하는 인공지능 예측 모델을 구축하여 향후 고객/구매자들에게 최적화된 육류 개인화 추천을 위한 시스템 개발을 목표로 하며 프로젝트를 추진했습니다.

## 서비스 화면

### Web Admin

육류 및 유저 데이터의 조회/입력/수정/통계/예측 등 관리 및 조회가 가능한 어드민 웹 페이지입니다.

관리자 및 연구자가 사용하기 위한 페이지로 개발되었습니다.

> 접속 주소 : http://deeplant-web.s3-website.ap-northeast-2.amazonaws.com

![ｈｏｍｅ](https://github.com/user-attachments/assets/06083c08-2898-4e8e-9f08-76f98d23366b)

### Mobile App

육류 맛 예측 인공지능 위한 데이터 수집에 사용되는 어플리케이션입니다.  
육류 이력 번호 조회, 사진 촬영, 관능평가 및 실험 데이터 등록, 조회, 수정이 가능합니다.

> APK 설치 경로 : [http://deeplant-web.s3-website.ap-northeast-2.amazonaws.com](https://deeplant-app.s3.ap-northeast-2.amazonaws.com/deepaging_1.1.1.apk)

<img src="https://github.com/user-attachments/assets/02ee4b02-4b0f-400a-8091-41756434a96e" width="400">

## 프로젝트 구현

### 아키텍쳐 구조도

<img width="800" alt="image" src="https://github.com/user-attachments/assets/074f9dc5-c115-4475-aaab-517b2632c9e7">

## 프로젝트 실행

### Production 환경

1. git repository clone

2. [환경 변수 및 Secret 변수 설정]

3. git push origin main

### Develop 환경

#### Web

1. `git clone https://github.com/deun115/20242R0136COSE48002.git`
2. `cd test-web`
3. `npm install`
4. `npm run start`

#### App

1. [flutter](https://docs.flutter.dev/get-started/install) 설치
2. [Android Studio](https://developer.android.com/studio?hl=ko)를 활용하여 에뮬레이터 실행 혹은 실제 모바일 기기 연결
3. `git clone https://github.com/deun115/20242R0136COSE48002.git`
4. `cd app/structure`
5. `flutter pub get`
6. `flutter run`

#### Backend & MLflow 서버 실행

**스크립트 기반 실행 (권장)**

프로젝트의 백엔드와 MLflow 서버는 `test-ML-backend/training_HSI/scripts/` 디렉토리에 있는 스크립트를 사용하여 실행할 수 있습니다.

**1) MLflow 서버 실행**

```bash
cd test-ML-backend/training_HSI/scripts/
./run_mlflow.sh
```

- MLflow 서버가 포트 5000에서 실행됩니다
- `configs/mlflow_config.json`의 설정을 기반으로 실행됩니다
- 백엔드 스토어와 아티팩트 저장소를 자동으로 설정합니다

**2) 백엔드 서버 실행**

```bash
cd test-ML-backend/training_HSI/scripts/
./run_backend.sh
```

- FastAPI 백엔드 서버가 포트 8000에서 실행됩니다
- Celery 워커가 백그라운드에서 실행됩니다
- tmux 세션을 사용하여 여러 프로세스를 관리합니다

**3) 포트 5000 프로세스 종료**

```bash
cd test-ML-backend/training_HSI/scripts/
./kill_5000_script.sh
```

- MLflow 서버 등 포트 5000을 사용하는 프로세스를 안전하게 종료합니다

**4) 가상환경을 통한 로컬 실행**

```bash
# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
cd test-ML-backend
pip install -r requirements_mlops.txt

# MLflow 서버 실행
cd training_HSI/scripts/
./run_mlflow.sh

# 새 터미널에서 백엔드 실행
cd test-ML-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 백엔드 아키텍처

### FastAPI 기반 백엔드

- **메인 서버**: `app/main.py`에서 FastAPI 애플리케이션 초기화
- **라우터 구조**: 각 기능별로 모듈화된 API 엔드포인트
  - `/train`: 모델 학습 API
  - `/predict`: 예측 API
  - `/meat`: 육류 데이터 관리
  - `/user`: 사용자 관리
  - `/statistic`: 통계 데이터
  - `/data-upload`: 데이터 업로드
  - `/xai`: 설명 가능한 AI
  - `/hsi-predict`: HSI 예측
  - `/hsi-train`: HSI 학습
  - `/spectral`: 스펙트럼 정보
  - `/dashboard`: 대시보드

### 미들웨어 및 보안

- CORS 설정
- 로깅 미들웨어
- 성능 모니터링
- 전역 예외 처리
- Firebase 인증

### 데이터베이스

- PostgreSQL 연결
- SQLAlchemy ORM
- Alembic 마이그레이션

## Training 파이프라인

### HSI (Hyperspectral Imaging) 학습 파이프라인

`test-ML-backend/training_HSI/` 디렉토리는 HSI 데이터를 사용한 딥러닝 모델 학습을 위한 완전한 파이프라인을 제공합니다.

#### 지원 모델 아키텍처

- **HSI Image Models**:
  - ResNet, 2D CNN, ViT, CNN-Transformer
  - Dual Branch Regression, HybridSN
  - SSANet, SSSERN, SpectrumNet
- **RGB Image Models**: ResNet 기반 모델
- **Vector Models**: PLSR, Random Forest, Hybrid 모델

#### 주요 기능

- **멀티태스크 학습**: 분류와 회귀 태스크를 동시에 학습
- **데이터 증강**: 랜덤 크롭, 뒤집기, 회전, 노이즈 추가
- **MLflow 통합**: 실험 추적, 메트릭 로깅, 모델 저장
- **Early Stopping**: 검증 손실 기반 자동 중단
- **AMP (Automatic Mixed Precision)**: GPU 메모리 최적화
- **Gradient Clipping**: 학습 안정성 향상

#### 데이터 처리

- **StandardScaler 모드**: normalized, raw, off 옵션
- **데이터 누출 방지**: 훈련 데이터로만 스케일러 학습
- **메모리 최적화**: 무작위 픽셀 샘플링

#### 설정 파일

- **column_config.json**: 데이터 컬럼, 라벨 타입, 파장 정보 정의
- **모델별 config**: 각 모델의 하이퍼파라미터 및 학습 설정
- **MLflow 설정**: 실험 이름, 추적 URI, 아티팩트 저장소

#### 실행 방법

```bash
# HSI 2D CNN 학습
python train_HSI_2d.py --config configs/HSI_image/hsi_resnet.json

# RGB 이미지 학습
python train_RGB.py --config configs/RGB_image/rgb_resnet.json

# 벡터 데이터 학습
python train_vector.py --config configs/HSI_vector/vector_plsr.json
```

## 참여자

| 정진성 (Jinseong Jung)                                                                              | 송재헌 (Jaeheon Song)                                                                                | 김강민 (Kangmin Kim)                                                                          | 김우진 (Woojin Kim)                                                                          | 서연지 (Yeonji Seo)                                                                         | 이정민 (Jeongmin Lee)                                                                            | 김명하 (Myeongha Kim)                                                                          | 황기현 (Kihyun Hwang)                                                                        | 김보민 (Bomin Kim)                                                                       |
| --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| <img src="https://avatars.githubusercontent.com/JANGHANPYEONG" width="160px" alt="Jinseong Jung" /> | <img src="https://avatars.githubusercontent.com/Songjaeheon0923" width="160px" alt="Jaeheon Song" /> | <img src="https://avatars.githubusercontent.com/The-Numb3" width="160px" alt="Kangmin Kim" /> | <img src="https://avatars.githubusercontent.com/3sirn3203" width="160px" alt="Woojin Kim" /> | <img src="https://avatars.githubusercontent.com/t2easure" width="160px" alt="Yeonji Seo" /> | <img src="https://avatars.githubusercontent.com/KUCSEPotato" width="160px" alt="Jeongmin Lee" /> | <img src="https://avatars.githubusercontent.com/myeonghah" width="160px" alt="Myeongha Kim" /> | <img src="https://avatars.githubusercontent.com/hkihyun" width="160px" alt="Kihyun Hwang" /> | <img src="https://avatars.githubusercontent.com/kminbo" width="160px" alt="Bomin Kim" /> |
| [GitHub: @JANGHANPYEONG](https://github.com/JANGHANPYEONG)                                          | [GitHub: @Songjaeheon0923](https://github.com/Songjaeheon0923)                                       | [GitHub: @The-Numb3](https://github.com/The-Numb3)                                            | [GitHub: @3sirn3203](https://github.com/3sirn3203)                                           | [GitHub: @t2easure](https://github.com/t2easure)                                            | [GitHub: @KUCSEPotato](https://github.com/KUCSEPotato)                                           | [GitHub: @myeonghah](https://github.com/myeonghah)                                             | [GitHub: @hkihyun](https://github.com/hkihyun)                                               | [GitHub: @kminbo](https://github.com/kminbo)                                             |
| 고려대학교 컴퓨터학과                                                                               | 고려대학교 컴퓨터학과                                                                                | 고려대학교 컴퓨터학과                                                                         | 고려대학교 컴퓨터학과                                                                        | 고려대학교 컴퓨터학과                                                                       | 고려대학교 컴퓨터학과                                                                            | 고려대학교 컴퓨터학과                                                                          | 고려대학교 컴퓨터학과                                                                        | 고려대학교 컴퓨터학과                                                                    |

## Project Tech Stack

### Environment

![Android Studio](https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white)
![Visual Studio Code](https://img.shields.io/badge/Visual%20Studio%20Code-007ACC?style=for-the-badge&logo=Visual%20Studio%20Code&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=Git&logoColor=white)
![Github](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=GitHub&logoColor=white)

### Release

![Amazone EC2](https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=amazon-ec2&logoColor=white)
![Amazone S3](https://img.shields.io/badge/Amazon%20S3-569A31?style=for-the-badge&logo=amazon-s3&logoColor=white)
![Amazone RDS](https://img.shields.io/badge/Amazon%20RDS-527FFF?style=for-the-badge&logo=amazon-rds&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=Docker&logoColor=white)
![Github Action](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)

### Development

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Flutter](https://img.shields.io/badge/Flutter-%2302569B.svg?style=for-the-badge&logo=Flutter&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white)
![Postgresql](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=Postgresql&logoColor=white)
![MLflow](https://img.shields.io/badge/MLflow-019733?style=for-the-badge&logo=MLflow&logoColor=white)

### Communication

![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=Slack&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white)

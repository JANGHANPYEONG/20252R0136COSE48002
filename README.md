# 고려대학교 산학협력프로젝트 딥플랜트
<div align="center">
<img width="300" alt="image" src="https://raw.githubusercontent.com/SincerityHun/Deep_Plant1_Final/main/web/images/l_deeplant.png">
</div>

> 개발기간: 2024.05 ~ 2024.12
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
1. ``git clone https://github.com/deun115/20242R0136COSE48002.git``
2. ``cd test-web``
3. ``npm install``
4. ``npm run start``

#### App
1. [flutter](https://docs.flutter.dev/get-started/install) 설치
2. [Android Studio](https://developer.android.com/studio?hl=ko)를 활용하여 에뮬레이터 실행 혹은 실제 모바일 기기 연결
3. ``git clone https://github.com/deun115/20242R0136COSE48002.git``
4. ``cd app/structure``
5. ``flutter pub get``
6. ``flutter run``
   
#### Backend
**1) Docker-Compose로 실행하기**

1. cd test-flask/
   - docker-compose.yml 파일이 위치한 경로로 이동
2. docker ps
3. docker compose version
   - 도커와 도커 컴포즈 설치 여부 확인
4. ``sudo docker-compose up-d``
   - docker compose build 및 실행
  
**2) 가상환경을 통해 로컬에서 실행하기**
1. ``python3 -m venv venv``
2. ``source venv/bin/activate``
     - 가상환경 생성 및 실행
4. cd test-backend/
5. ``docker run -d -p 5000:5000 --name mlflow-server ghcr.io/mlflow/mlflow mlflow server --host 0.0.0.0``
     - 공식 도커 이미지를 활용하여 mlflow 서버 키기
6. ``pip install -r requirements-dev.txt``
     - 서버 실행에 필요한 파이썬 패키지 설치
8. ``gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 600 app:app``
     - flask 서버 실행
     - 만약 터미널에서 로그 확인하고 싶다면 ``--log-level [info|debug]`` argument 추가

## 참여자
| 이원준 (Wonjun Lee) | 원하진 (Hajin Won) | 최순혁 (Sunhyuk Choi) | 최승민 (Seungmin Choi) | 양은서 (Eunseo Yang) | 최다영 (Dayoung Choi) | 김태관 (Taekwan Kim) | 김태우 (Taewoo Kim) |
|----------|----------|----------|----------|----------|----------|----------|----------|
| <img width="160px" src="https://avatars.githubusercontent.com/u/97330728?v=4" alt="Wonjun Lee" />    | <img src="https://avatars.githubusercontent.com/u/8970523?v=4" width="200">     | <img src="https://avatars.githubusercontent.com/recon48" width="200">     | <img src="https://avatars.githubusercontent.com/sdouf5054" width="200">     | <img width="160px" src="https://avatars.githubusercontent.com/u/141890722?v=4" alt="Eunseo Yang" />     | <img src="https://avatars.githubusercontent.com/u/80742780?v=4" width="200">     | <img src="https://avatars.githubusercontent.com/u/147288887?v=4" width="200">     | <img src="https://avatars.githubusercontent.com/skitw427" width="200">     |
| [GitHub: @wonjuneee](https://github.com/wonjuneee)    | [GitHub: @wonhj12](https://github.com/wonhj12)       | [GitHub: @recon48](https://github.com/recon48)     | [GitHub: @sdouf5054](https://github.com/sdouf5054)     | [GitHub: @deun115](https://github.com/deun115)     | [GitHub: @dayoung20](https://github.com/dayoung20)     | [GitHub: @TTKKWAN](https://github.com/TTKKWAN)         | [GitHub: @skitw427](https://github.com/skitw427)     |
| 고려대학교 컴퓨터학과 3학년    | 고려대학교 컴퓨터학과 3학년     | 고려대학교 컴퓨터학과 3학년     | 고려대학교 컴퓨터학과 3학년     | 고려대학교 컴퓨터학과 4학년     | 고려대학교 데이터과학과 3학년     | 고려대학교 컴퓨터학과 2학년     | 고려대학교 컴퓨터학과 3학년     |


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
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=Flask&logoColor=white)
![Postgresql](https://img.shields.io/badge/PostgreSQL-336791?style=for-the-badge&logo=Postgresql&logoColor=white)

### Communication

![Slack](https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=Slack&logoColor=white)
![Notion](https://img.shields.io/badge/Notion-000000?style=for-the-badge&logo=Notion&logoColor=white)

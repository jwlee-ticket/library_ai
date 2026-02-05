# Library Sales

온톨로지 기반 공연 인텔리전스 시스템

Library Sales는 공연의 기획 → 제작 → 판매 전 단계의 데이터를 구조화하고 분석하여 데이터 기반 의사결정을 지원하는 시스템입니다.

## 기술 스택

- **Backend**: Django 5.2.8
- **Database**: PostgreSQL
- **Frontend**: Django Templates + Tailwind CSS
- **Charts**: Chart.js
- **Data Processing**: pandas, openpyxl
- **WSGI Server**: Gunicorn 21.2.0
- **Deployment**: GCP Compute Engine (VM) + Nginx + Gunicorn

## 빠른 시작

1. PostgreSQL 설치 및 실행
2. 가상환경 생성 및 활성화: `python -m venv venv && source venv/bin/activate`
3. 패키지 설치: `pip install -r requirements.txt`
4. 환경 변수 설정: `.env` 파일 생성
5. Tailwind CSS 설정: `python manage.py tailwind init && python manage.py tailwind build`
6. 마이그레이션: `python manage.py migrate`
7. 관리자 계정 생성: `python manage.py createsuperuser`
8. 개발 서버 실행: `python manage.py runserver`
9. Tailwind CSS 개발 모드 (별도 터미널): `python manage.py tailwind dev`

## 문서

- **[개발 가이드](docs/development-guide.md)**: 개발 환경 설정, 프로젝트 구조, 시스템 아키텍처, 데이터 관계, 개발 원칙, 배포 가이드
- **[디자인 시스템](docs/design-system.md)**: 컬러 시스템, 타이포그래피, 컴포넌트 가이드, 레이아웃 패턴, 차트 스타일, 숫자 포맷팅

## 프로젝트 구조

```
config/                   # Django 프로젝트 설정
├── core/                 # 공통 기능 (인증)
├── performance/          # 공연 관리
├── data_management/      # 데이터 관리 (매출, 마케팅, 리뷰)
├── dashboard/            # 대시보드
├── theme/                # Tailwind CSS 설정
├── templates/            # 템플릿
└── deploy/               # 배포 설정 파일
```
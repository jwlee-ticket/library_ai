# Library AI

공연 판매 데이터 분석 및 시각화 시스템

## 프로젝트 구조

```
config/                   # Django 프로젝트 루트
├── settings/             # 설정 파일 (base/dev/prod 분리)
├── core/                 # 공통 기능
├── performance/          # 공연 관리
├── sales/                # 판매 데이터 업로드
├── templates/            # 공통 템플릿 (base.html 등)
├── static/               # 정적 파일 (CSS, JS)
└── media/                # 업로드 파일
```

## 기술 스택

- **Backend**: Django
- **Database**: PostgreSQL
- **Frontend**: Django Templates + Tailwind CSS (django-tailwind)
- **Charts**: Chart.js (직관적인 시각화 중심)
- **Data Processing**: pandas (엑셀 파일 처리 및 데이터 분석)
- **Environment**: django-environ
- **Deployment**: GCP (Cloud Run / App Engine)

## 주요 기능

### MVP
- 공연 관리
- 판매 데이터 엑셀 업로드
- 카테고리별 대시보드 (통합/연극/뮤지컬/콘서트)
- 단일 공연 대시보드

## URL 구조

```
/                            → 통합 대시보드
/dashboard/theater/          → 연극 대시보드
/dashboard/musical/          → 뮤지컬 대시보드
/dashboard/concert/          → 콘서트 대시보드
/performance/                → 공연 목록
/performance/create/         → 공연 등록
/performance/<id>/dashboard/ → 단일 공연 대시보드
/sales/upload/               → 판매 데이터 업로드
```

## 개발 환경 설정

1. PostgreSQL 설치 및 실행
2. 가상환경 생성 및 활성화
3. `.env` 파일 생성 (django-environ 사용)
4. 패키지 설치: `pip install -r requirements.txt`
5. 마이그레이션: `python manage.py migrate`
6. 개발 서버 실행: `python manage.py runserver`

## 디자인 시스템

- **브랜드 컬러**: #f65938
- **배경**: 흰색 (#ffffff)
- **텍스트**: 검은색 (#000000)
- **보조 텍스트**: 회색 (#666666)
- **폰트**: Pretendard
- **스타일**: Mixpanel 스타일 참고 (심플한 인터페이스, 명확한 정보 구조, 데이터 시각화 중심)

## 데이터 관리

- **자동 영역**: 엑셀 파일 업로드 (판매 데이터)
- **수동 영역**: 웹 폼 입력 (공연 기본 정보)

## 개발 원칙

- 서비스 레이어 분리 (views.py와 services.py 분리)
- 앱별 템플릿 구조
- Django Admin 최소 커스터마이징
- 비전문가(공연업계 종사자)가 쉽게 이해할 수 있는 직관적인 데이터 시각화
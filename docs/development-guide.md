# 개발 가이드

Library AI 프로젝트의 개발 가이드입니다.

## 1. 기술 스펙

### Backend
- **Framework**: Django 5.2.8 (LTS)
- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **Database Adapter**: psycopg2-binary 2.9.11 - PostgreSQL Python 어댑터
- **ORM**: Django ORM

### Frontend
- **Templates**: Django Templates
- **CSS Framework**: Tailwind CSS 4.x (django-tailwind)
- **Charts**: Chart.js
- **Font**: Pretendard

### Data Processing
- **pandas**: 2.3.3 - 데이터 분석 및 처리
- **openpyxl**: 3.1.5 - Excel 파일 처리

### Image Processing
- **Pillow**: 11.0.0 - 이미지 처리

### Environment & Deployment
- **django-environ**: 0.12.0 - 환경 변수 관리
- **gunicorn**: 21.2.0 - WSGI 서버 (프로덕션)
- **Deployment**: GCP Compute Engine (VM) + Nginx + Gunicorn

### Utilities
- **python-dateutil**: 2.9.0.post0 - 날짜/시간 처리 유틸리티

### 주요 의존성
```
Django==5.2.8
psycopg2-binary==2.9.11
django-environ==0.12.0
django-tailwind==4.4.1
pandas==2.3.3
openpyxl==3.1.5
Pillow==11.0.0
python-dateutil==2.9.0.post0
gunicorn==21.2.0
```

---

## 2. 개발 환경 설정

### 필수 요구사항
- Python 3.11 이상
- PostgreSQL 12 이상
- Node.js 18 이상 (Tailwind CSS 빌드용)

### 환경 설정 단계

#### 1. 저장소 클론
```bash
git clone <repository-url>
cd library_ai
```

#### 2. 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

#### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

#### 4. 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (필요한 값 설정)
# SECRET_KEY, DEBUG, DATABASE_URL, ALLOWED_HOSTS 등
```

#### 5. PostgreSQL 데이터베이스 설정
```bash
# PostgreSQL 접속
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE library_ai;

# 사용자 생성 및 권한 부여
CREATE USER library_ai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE library_ai TO library_ai_user;
```

#### 6. Tailwind CSS 설정
```bash
# Tailwind CSS 초기화
python manage.py tailwind init

# Tailwind CSS 빌드
python manage.py tailwind build
```

#### 7. 데이터베이스 마이그레이션
```bash
# 마이그레이션 생성
python manage.py makemigrations

# 마이그레이션 적용
python manage.py migrate
```

#### 8. 관리자 계정 생성
```bash
python manage.py createsuperuser
```

#### 9. 개발 서버 실행
```bash
# Django 개발 서버 실행
python manage.py runserver

# Tailwind CSS 개발 모드 (별도 터미널)
python manage.py tailwind dev
```

### 개발 워크플로우
1. 코드 수정
2. Tailwind CSS 자동 빌드 (개발 모드 실행 시)
3. 브라우저에서 확인 (`http://localhost:8000`)

### 환경 변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 다음 변수들을 설정합니다:

```bash
# 필수 설정
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 데이터베이스 설정
DATABASE_URL=postgresql://library_ai_user:your_password@localhost:5432/library_ai

# 프로덕션 설정 (프로덕션 환경에서만)
SECURE_SSL_REDIRECT=False
DB_CONN_MAX_AGE=600
```

---

## 3. 프로젝트 구조

```
library_ai/
├── config/                    # Django 프로젝트 설정
│   ├── settings.py           # 프로젝트 설정
│   ├── urls.py               # 메인 URL 설정
│   ├── wsgi.py               # WSGI 설정
│   └── asgi.py               # ASGI 설정
│
├── core/                      # 공통 기능
│   ├── models.py             # 공통 모델 (현재 없음)
│   ├── views.py              # 로그인/로그아웃 뷰
│   ├── forms.py              # 인증 폼
│   ├── admin.py              # User Admin 커스터마이징
│   ├── mixins.py             # 공용 Mixin (현재 없음)
│   ├── signals.py            # 시그널 (현재 없음)
│   ├── urls.py               # 인증 URL
│   └── templatetags/         # 커스텀 템플릿 태그
│       ├── custom_filters.py
│       └── performance_tags.py
│
├── performance/               # 공연 관리 앱
│   ├── models.py             # Performance 모델
│   ├── views.py              # CRUD 뷰
│   ├── forms.py              # Performance 폼
│   ├── admin.py              # Performance Admin
│   └── urls.py               # 공연 URL
│
├── data_management/          # 데이터 관리 앱
│   ├── models.py             # PerformanceSales 모델
│   ├── views.py              # 매출 관리 뷰
│   ├── forms.py              # 매출 폼
│   ├── admin.py              # 매출 Admin
│   └── urls.py               # 데이터 관리 URL
│
├── dashboard/                # 대시보드 앱
│   ├── views.py              # 대시보드 뷰 (공연별, 장르별)
│   └── urls.py               # 대시보드 URL
│
├── deploy/                    # 배포 설정 파일
│   ├── deploy-vm.sh          # VM 배포 스크립트
│   ├── gunicorn.service      # Gunicorn systemd 서비스 파일
│   └── nginx.conf            # Nginx 설정 파일
│
├── theme/                    # Tailwind CSS 설정
│   ├── static_src/
│   │   └── src/
│   │       └── styles.css    # Tailwind CSS 소스
│   └── static/
│       └── css/
│           └── dist/
│               └── styles.css # 빌드된 CSS
│
├── templates/                # 공통 템플릿
│   ├── base.html             # 기본 레이아웃
│   ├── components/           # 재사용 컴포넌트
│   │   ├── action_buttons.html
│   │   ├── genre_dropdown.html
│   │   ├── pagination.html
│   │   └── search_filter.html
│   ├── core/                 # 인증 템플릿
│   │   └── login.html
│   ├── performance/           # 공연 템플릿
│   │   ├── list.html
│   │   ├── detail.html
│   │   ├── form.html
│   │   └── confirm_delete.html
│   ├── data_management/      # 데이터 관리 템플릿
│   │   ├── performance_list.html
│   │   └── concert_sales/
│   │       └── detail.html
│   └── dashboard/            # 대시보드 템플릿
│       ├── main.html         # 통합 대시보드
│       ├── list.html         # 공연 목록 대시보드
│       ├── detail.html       # 공통 상세 대시보드
│       └── concert/          # 콘서트 장르별 대시보드
│           ├── detail.html   # 콘서트 상세 대시보드
│           └── overview.html # 콘서트 통합 대시보드
│
├── docs/                      # 문서
│   ├── design-system.md      # 디자인 시스템 가이드
│   └── development-guide.md  # 개발 가이드 (본 문서)
│
├── static/                    # 정적 파일
│   ├── js/                    # JavaScript 파일
│   │   ├── base.js            # 공통 JavaScript
│   │   ├── concert_sales_detail.js      # 공연 매출 상세 페이지
│   │   ├── concert_dashboard_detail.js  # 콘서트 대시보드 상세
│   │   └── concert_aggregated_dashboard.js  # 콘서트 통합 대시보드
│   └── css/                   # CSS 파일 (빌드된 파일)
├── media/                     # 업로드 파일
├── venv/                      # 가상환경 (gitignore)
├── manage.py                  # Django 관리 스크립트
├── requirements.txt           # Python 의존성
└── README.md                  # 프로젝트 개요
```

### 앱별 역할

#### core
- 사용자 인증 (로그인/로그아웃)
- 커스텀 템플릿 태그 및 필터
- 공통 유틸리티

#### performance
- 공연 정보 관리 (CRUD)
- 공연별 동적 설정값 관리 (좌석 등급, 예매처, 할인권종 등)
- 공연 목록, 상세, 등록, 수정, 삭제

#### data_management
- 매출 데이터 관리 (공연 공통)
- 마케팅 데이터 관리 (개발 예정)
- 리뷰 데이터 관리 (개발 예정)
- 공연 기반 데이터 입력 및 관리

#### dashboard
- 공연 목록 대시보드 (장르별 필터링, 검색)
- 공연별 상세 대시보드 (장르별 동적 템플릿 로딩)
- 콘서트 상세 대시보드:
  - 일간 매출/판매 매수 그래프 (Chart.js)
  - 예매처별, 입금/미입금 필터링
  - 등급별 판매 현황 (테이블 + 파이 차트)
  - 할인권종별 판매 현황
  - 성별/연령대별 판매 현황 (바 차트)
  - 결제수단별 판매 현황
  - 카드별 매출 집계
  - 판매경로별 판매 현황 (테이블 + 파이 차트)
  - 지역별 판매 현황 (테이블 + 파이 차트)
- 콘서트 통합 대시보드:
  - 전체 콘서트 매출/판매 매수 현황
  - 목표액 달성 현황 (개별 공연별 진행률)
  - 기간별 매출 그래프 (일간/주간/월간, Stacked Bar Chart)
  - 기간별 매출 테이블

---

## 4. 시스템 구조도

### 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "Client Layer"
        User[사용자 브라우저]
    end
    
    subgraph "Presentation Layer"
        Templates[Django Templates<br/>+ Tailwind CSS]
        Base[base.html<br/>기본 레이아웃]
        Components[Components<br/>재사용 컴포넌트]
        Pages[Pages<br/>페이지 템플릿]
        
        Templates --> Base
        Templates --> Components
        Templates --> Pages
    end
    
    subgraph "Application Layer"
        CoreViews[Core Views<br/>인증/로그인]
        PerfViews[Performance Views<br/>공연 관리]
        DataViews[Data Management Views<br/>매출/마케팅/리뷰]
        DashViews[Dashboard Views<br/>대시보드]
    end
    
    subgraph "Business Logic Layer"
        Forms[Django Forms<br/>데이터 검증]
        Services[Services<br/>비즈니스 로직]
    end
    
    subgraph "Data Layer"
        UserModel[User Model]
        PerfModel[Performance Model]
        SalesModel[PerformanceSales Model]
        MarketingModel[Marketing Model]
        ReviewModel[Review Model]
    end
    
    subgraph "Database"
        PostgreSQL[(PostgreSQL<br/>Database)]
    end
    
    User --> Templates
    Templates --> CoreViews
    Templates --> PerfViews
    Templates --> DataViews
    Templates --> DashViews
    
    CoreViews --> Forms
    PerfViews --> Forms
    DataViews --> Forms
    
    Forms --> Services
    Services --> UserModel
    Services --> PerfModel
    Services --> SalesModel
    Services --> MarketingModel
    Services --> ReviewModel
    
    UserModel --> PostgreSQL
    PerfModel --> PostgreSQL
    SalesModel --> PostgreSQL
    MarketingModel --> PostgreSQL
    ReviewModel --> PostgreSQL
    
    PostgreSQL --> Services
    Services --> Forms
    Forms --> Templates
    Templates --> User
    
    style User fill:#f65938,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style PerfModel fill:#2a3038,color:#fff
```

### 데이터 흐름

```mermaid
flowchart LR
    Start([사용자 입력]) --> Forms[Django Forms<br/>데이터 검증]
    Forms -->|검증 성공| Views[Django Views<br/>비즈니스 로직]
    Forms -->|검증 실패| Error[에러 메시지<br/>사용자에게 표시]
    Views --> Models[Django Models<br/>데이터 저장]
    Models --> DB[(PostgreSQL<br/>Database)]
    DB -->|조회| Views2[Django Views<br/>데이터 조회]
    Views2 --> Templates[Django Templates<br/>렌더링]
    Templates --> End([사용자에게 표시])
    
    style Start fill:#16a34a,color:#fff
    style End fill:#16a34a,color:#fff
    style Error fill:#dc2626,color:#fff
    style DB fill:#336791,color:#fff
```

### 요청 처리 흐름

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Browser as 브라우저
    participant URLs as config/urls.py
    participant AppURLs as 앱별 urls.py
    participant Views as views.py
    participant Models as models.py
    participant DB as PostgreSQL
    
    User->>Browser: HTTP Request
    Browser->>URLs: URL 라우팅
    URLs->>AppURLs: 앱별 라우팅
    AppURLs->>Views: 뷰 함수/클래스 호출
    
    alt 데이터 조회
        Views->>Models: 데이터 조회 요청
        Models->>DB: SQL 쿼리 실행
        DB-->>Models: 데이터 반환
        Models-->>Views: 모델 객체 반환
        Views->>Views: 템플릿 렌더링
    else 데이터 저장
        Views->>Models: 데이터 저장 요청
        Models->>DB: INSERT/UPDATE 쿼리
        DB-->>Models: 저장 완료
        Models-->>Views: 저장 결과 반환
        Views->>Views: 템플릿 렌더링
    end
    
    Views-->>Browser: HTTP Response (HTML)
    Browser-->>User: 페이지 표시
```

---

## 5. 데이터 관계 다이어그램

### ERD (Entity Relationship Diagram)

```mermaid
erDiagram
    USER ||--o{ PERFORMANCE : creates
    PERFORMANCE ||--o{ SEAT_GRADE : has
    PERFORMANCE ||--o{ BOOKING_SITE : has
    PERFORMANCE ||--o{ DISCOUNT_TYPE : has
    PERFORMANCE ||--o{ PERFORMANCE_DAILY_SALES : has
    PERFORMANCE ||--o{ PERFORMANCE_FINAL_SALES : has
    PERFORMANCE ||--o{ MARKETING : has
    PERFORMANCE ||--o{ REVIEW : has
    
    SEAT_GRADE ||--o{ PERFORMANCE_DAILY_SALES_GRADE : used_in
    SEAT_GRADE ||--o{ PERFORMANCE_FINAL_SALES_GRADE : used_in
    SEAT_GRADE }o--o{ DISCOUNT_TYPE : applicable_to
    BOOKING_SITE ||--o{ PERFORMANCE_DAILY_SALES : used_in
    BOOKING_SITE ||--o{ PERFORMANCE_FINAL_SALES : used_in
    PERFORMANCE_DAILY_SALES ||--o{ PERFORMANCE_DAILY_SALES_GRADE : has
    PERFORMANCE_FINAL_SALES ||--o{ PERFORMANCE_FINAL_SALES_GRADE : has
    
    USER {
        int id PK
        string username
        string email
        string first_name
        datetime date_joined
    }
    
    PERFORMANCE {
        int id PK
        string title "공연명"
        string genre "연극/뮤지컬/콘서트/전시"
        string venue "공연장"
        string address "공연장 주소"
        date performance_start
        date performance_end
        date sales_start
        date sales_end
        decimal target_revenue "목표 매출"
        decimal break_even_point "손익분기점"
        decimal total_production_cost "총 제작비"
        image seat_map
        datetime created_at
        datetime updated_at
    }
    
    SEAT_GRADE {
        int id PK
        int performance_id FK
        string name "등급명"
        decimal price "티켓 가격"
        int seat_count "좌석 수"
        int order "정렬 순서"
    }
    
    BOOKING_SITE {
        int id PK
        int performance_id FK
        string name "예매처명"
        string url "예매 URL"
    }
    
    DISCOUNT_TYPE {
        int id PK
        int performance_id FK
        string name "할인권종명"
        date start_date "할인 시작일"
        date end_date "할인 종료일"
        int discount_rate "할인율"
    }
    
    PERFORMANCE_DAILY_SALES {
        int id PK
        int performance_id FK
        int booking_site_id FK
        date date "판매일"
        decimal paid_revenue "입금 판매액"
        int paid_ticket_count "입금 판매 매수"
        decimal unpaid_revenue "미입금 판매액"
        int unpaid_ticket_count "미입금 판매 매수"
        datetime created_at
        datetime updated_at
    }
    
    PERFORMANCE_DAILY_SALES_GRADE {
        int id PK
        int daily_sales_id FK
        int seat_grade_id FK
        int paid_count "입금 판매 매수"
        int unpaid_count "미입금 판매 매수"
        int free_count "무료 매수"
    }
    
    PERFORMANCE_FINAL_SALES {
        int id PK
        int performance_id FK
        int booking_site_id FK
        json grade_sales_summary "등급별 판매 현황"
        json booking_site_discount_sales "예매처별 할인 판매"
        json age_gender_sales "성별/연령대별 판매"
        json payment_method_sales "결제수단별 판매"
        json card_sales_summary "카드별 매출 집계"
        json sales_channel_sales "판매경로별 판매"
        json region_sales "지역별 판매"
        datetime created_at
        datetime updated_at
    }
    
    PERFORMANCE_FINAL_SALES_GRADE {
        int id PK
        int final_sales_id FK
        int seat_grade_id FK
        int paid_count "입금 판매 매수"
        int unpaid_count "미입금 판매 매수"
        int free_count "무료 매수"
        decimal paid_revenue "입금 매출액"
        decimal total_revenue "총 매출액"
        decimal paid_occupancy_rate "입금 점유율"
        decimal total_occupancy_rate "총 점유율"
    }
    
    MARKETING {
        int id PK
        int performance_id FK
        "개발 예정"
    }
    
    REVIEW {
        int id PK
        int performance_id FK
        "개발 예정"
    }
```

### 데이터 관계 설명

#### 1. Performance (공연) - 중심 엔티티
- 모든 데이터의 중심이 되는 엔티티
- 정규화된 모델을 통한 동적 설정값 관리:
  - **SeatGrade**: 좌석 등급 (등급명, 티켓 가격, 좌석 수)
  - **BookingSite**: 예매처 (예매처명, 예매 URL)
  - **DiscountType**: 할인권종 (할인권종명, 할인 기간, 할인율, 적용 가능한 등급)

#### 2. Sales (매출) - Performance 기반
- **PerformanceDailySales**: 일별 매출 데이터 (예매처별, 입금/미입금 구분)
- **PerformanceDailySalesGrade**: 일별 등급별 판매 데이터 (입금/미입금/무료 매수)
- **PerformanceFinalSales**: 최종 집계 데이터 (등급별, 성별/연령대별, 결제수단별 등)
- **PerformanceFinalSalesGrade**: 최종 등급별 판매 데이터 (매출액, 점유율 포함)
- `performance` ForeignKey로 Performance 참조
- `booking_site` ForeignKey로 BookingSite 참조
- `seat_grade` ForeignKey로 SeatGrade 참조
- Performance에서 정의한 값만 사용 가능:
  - `booking_site`: Performance의 `booking_sites`에서 선택
  - `seat_grade`: Performance의 `seat_grades`에서 선택

#### 4. 데이터 무결성 보장
- Performance에서 정의하지 않은 값은 Sales에서 사용 불가
- ForeignKey 관계를 통한 데이터 일관성 보장
- 폼 검증을 통한 추가 데이터 무결성 보장
- `unique_together`를 통한 중복 방지

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
│   ├── models.py             # User 모델 (Django 기본)
│   ├── views.py              # 로그인/로그아웃 뷰
│   ├── forms.py              # 인증 폼
│   ├── admin.py              # User Admin 커스터마이징
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
│   ├── models.py             # ConcertSales 모델
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
│   │       ├── list.html
│   │       ├── form.html
│   │       └── confirm_delete.html
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
│   │   ├── concert_sales_detail.js      # 콘서트 매출 상세 페이지
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
- 공연별 동적 설정값 관리 (좌석 등급, 예매처 등)
- 공연 목록, 상세, 등록, 수정, 삭제

#### data_management
- 매출 데이터 관리 (현재: 콘서트)
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
        SalesModel[ConcertSales Model]
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
    PERFORMANCE ||--o{ CONCERT_DAILY_SALES : has
    PERFORMANCE ||--o{ CONCERT_FINAL_SALES : has
    PERFORMANCE ||--o{ MUSICAL_SALES : has
    PERFORMANCE ||--o{ THEATER_SALES : has
    PERFORMANCE ||--o{ MARKETING : has
    PERFORMANCE ||--o{ REVIEW : has
    
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
        int total_seats "총 좌석 수"
        json seat_grades "동적 설정: 좌석 등급"
        json ticket_prices "동적 설정: 티켓 가격"
        json seat_counts "동적 설정: 좌석 수"
        json discounts "동적 설정: 할인율"
        json booking_sites "동적 설정: 예매처"
        json crew "제작진"
        json casting "캐스팅"
        image seat_map
        datetime created_at
        datetime updated_at
    }
    
    CONCERT_DAILY_SALES {
        int id PK
        int performance_id FK
        date date "판매일"
        string booking_site "예매처"
        decimal revenue "매출"
        int ticket_count "판매 매수"
        boolean is_paid "입금 여부"
        datetime created_at
        datetime updated_at
    }
    
    CONCERT_FINAL_SALES {
        int id PK
        int performance_id FK
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
    
    MUSICAL_SALES {
        int id PK
        int performance_id FK
        "개발 예정"
    }
    
    THEATER_SALES {
        int id PK
        int performance_id FK
        "개발 예정"
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
- 동적 설정값을 JSON 필드로 관리:
  - `seat_grades`: 좌석 등급 리스트 (예: ["VIP", "R석", "S석"])
  - `booking_sites`: 예매처 리스트 (예: [{"인터파크": "https://..."}])
  - `ticket_prices`: 티켓 가격 딕셔너리 (예: {"VIP": 150000})
  - `seat_counts`: 좌석 수 딕셔너리 (예: {"VIP": 50})
  - `discounts`: 할인율 딕셔너리 (예: {"VIP": {"조조할인": 10}})

#### 2. Sales (매출) - Performance 기반
- **ConcertDailySales**: 일별 매출 데이터 (예매처별, 입금/미입금 구분)
- **ConcertFinalSales**: 최종 집계 데이터 (등급별, 성별/연령대별, 결제수단별 등)
- `MusicalSales`, `TheaterSales` 등 장르별 모델 (개발 예정)
- `performance` ForeignKey로 Performance 참조
- Performance에서 정의한 값만 사용 가능:
  - `booking_site`: Performance의 `booking_sites`에서 선택
  - `grade_sales_summary`: Performance의 `seat_grades` 기반

#### 3. 데이터 무결성 보장
- Performance에서 정의하지 않은 값은 Sales에서 사용 불가
- 폼 검증을 통해 데이터 일관성 보장
- `limit_choices_to`로 장르별 필터링

---

## 6. 개발 원칙

### 1. 공연 중심 데이터 구조 (온톨로지)
- **원칙**: 모든 데이터는 공연(Performance)을 중심으로 구조화
- **구현**: 
  - Performance에서 동적 설정값 정의
  - 하위 데이터(Sales, Marketing, Review)는 Performance의 설정값만 사용
  - 데이터 검증을 통한 무결성 보장

### 2. 동적 설정 가능한 구조
- **원칙**: 시스템 고정값 제거, 사용자가 공연별로 직접 정의
- **구현**:
  - JSON 필드를 활용한 유연한 데이터 구조
  - 폼에서 동적 입력 필드 생성
  - 예외 처리 강화

### 3. 사용자 중심 설계
- **원칙**: 비전문가(공연업계 종사자)가 쉽게 사용할 수 있는 인터페이스
- **구현**:
  - 직관적인 UI/UX
  - 친근한 톤앤보이스 (어요/해요 체)
  - 명확한 에러 메시지 및 도움말

### 4. 코드 네이밍 가이드
- **HTML/CSS 클래스**: 소문자 또는 kebab-case (`btn-primary`, `card-dashboard`)
- **Python 클래스**: PascalCase (`Performance`, `ConcertSales`)
- **외부 서비스 이름 사용 금지**: `TossButton`, `MixpanelCard` 등 사용하지 않음

### 5. 서비스 레이어 분리
- **원칙**: views.py와 services.py 분리 (향후 적용)
- **현재**: views.py에 비즈니스 로직 포함
- **향후**: 복잡한 로직은 services.py로 분리 예정

### 6. 앱별 템플릿 구조
- **원칙**: 각 앱의 템플릿은 `templates/{app_name}/` 디렉토리에 위치
- **공통 컴포넌트**: `templates/components/` 디렉토리에 재사용 컴포넌트
- **기본 레이아웃**: `templates/base.html`

### 7. Django Admin 최소 커스터마이징
- **원칙**: Django Admin은 개발/관리용으로만 사용
- **구현**: 기본 Admin 기능 활용, 최소한의 커스터마이징만 수행

### 8. 데이터 검증
- **원칙**: 폼 레벨과 모델 레벨에서 이중 검증
- **구현**:
  - `forms.py`에서 폼 검증
  - `models.py`에서 모델 검증
  - Performance의 설정값 기반 검증

### 9. 에러 처리
- **원칙**: 사용자 친화적인 에러 메시지 제공
- **구현**:
  - Django Messages Framework 활용
  - 친근한 톤의 에러 메시지
  - 해결 방법 제시

### 10. 확장 가능한 구조
- **원칙**: 새로운 장르, 새로운 데이터 타입 추가 용이
- **구현**:
  - 앱별 독립적인 구조
  - 공통 인터페이스 활용
  - 재사용 가능한 컴포넌트

---

## 7. 배포 가이드

### 배포 환경
- **인프라**: GCP Compute Engine (VM)
- **웹 서버**: Nginx
- **WSGI 서버**: Gunicorn
- **데이터베이스**: GCP Cloud SQL (PostgreSQL)

### 배포 구조

```mermaid
graph TB
    subgraph "Client"
        Browser[사용자 브라우저]
    end
    
    subgraph "GCP Compute Engine VM"
        subgraph "Web Server Layer"
            Nginx[Nginx<br/>포트 80<br/>Reverse Proxy]
        end
        
        subgraph "Application Layer"
            Gunicorn[Gunicorn<br/>WSGI 서버<br/>Django Application]
        end
        
        subgraph "File System"
            StaticFiles[정적 파일<br/>/var/www/library-ai/staticfiles]
            MediaFiles[미디어 파일<br/>/var/www/library-ai/media]
            SocketFile[Unix Socket<br/>/var/www/library-ai/library-ai.sock]
        end
    end
    
    subgraph "GCP Cloud SQL"
        PostgreSQL[(PostgreSQL<br/>Database)]
    end
    
    Browser -->|HTTP Request| Nginx
    Nginx -->|정적 파일| StaticFiles
    Nginx -->|미디어 파일| MediaFiles
    Nginx -->|Unix Socket| SocketFile
    SocketFile --> Gunicorn
    Gunicorn -->|TCP/IP<br/>SQL Query| PostgreSQL
    PostgreSQL -->|Query Result| Gunicorn
    Gunicorn -->|Response| SocketFile
    SocketFile --> Nginx
    Nginx -->|HTTP Response| Browser
    
    style Browser fill:#f65938,color:#fff
    style Nginx fill:#009639,color:#fff
    style Gunicorn fill:#2a3038,color:#fff
    style PostgreSQL fill:#336791,color:#fff
    style SocketFile fill:#78716c,color:#fff
```

### 배포 파일 구조

```
deploy/
├── deploy-vm.sh          # VM 배포 스크립트
├── gunicorn.service      # Gunicorn systemd 서비스 파일
└── nginx.conf            # Nginx 서버 설정 파일
```

### 배포 프로세스

#### 1. VM 초기 설정 (최초 1회)

VM에 SSH 접속 후 다음 명령어 실행:

```bash
# 시스템 업데이트 및 필수 패키지 설치
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.11 python3.11-venv python3-pip postgresql-client nginx git

# 프로젝트 디렉토리 생성
sudo mkdir -p /var/www/library-ai
sudo chown -R $USER:$USER /var/www/library-ai

# Git 저장소 클론
cd /var/www/library-ai
git clone <repository-url> .

# 가상환경 생성 및 의존성 설치
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (DATABASE_URL, SECRET_KEY 등)

# Tailwind CSS 빌드 및 정적 파일 수집
python manage.py tailwind build
python manage.py collectstatic --noinput

# 데이터베이스 마이그레이션
python manage.py migrate

# Gunicorn 서비스 설정
sudo cp deploy/gunicorn.service /etc/systemd/system/library-ai.service
sudo systemctl daemon-reload
sudo systemctl enable library-ai
sudo systemctl start library-ai

# Nginx 설정
sudo cp deploy/nginx.conf /etc/nginx/sites-available/library-ai
sudo ln -s /etc/nginx/sites-available/library-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 2. 배포 스크립트 실행

코드 변경 후 VM에서 배포:

```bash
cd /var/www/library-ai
source venv/bin/activate
./deploy/deploy-vm.sh
```

배포 스크립트가 자동으로 수행하는 작업:
1. 소유권을 현재 사용자로 변경
2. `git pull` 실행
3. 의존성 설치 (`pip install -r requirements.txt`)
4. Tailwind CSS 빌드 (`python manage.py tailwind build`)
5. 정적 파일 수집 (`python manage.py collectstatic`)
6. 데이터베이스 마이그레이션 (`python manage.py migrate`)
7. 소유권을 `www-data`로 변경 (venv 제외)
8. Gunicorn 재시작 (`sudo systemctl restart library-ai`)

### 환경 변수 설정 (프로덕션)

VM의 `/var/www/library-ai/.env` 파일에 다음 변수 설정:

```bash
# 필수 설정
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-vm-ip

# 데이터베이스 설정 (Cloud SQL)
DATABASE_URL=postgresql://library_ai_user:password@cloud-sql-ip:5432/library_ai

# 프로덕션 보안 설정
SECURE_SSL_REDIRECT=False  # Nginx가 HTTPS 처리
DB_CONN_MAX_AGE=600
```

### 서비스 관리

```bash
# Gunicorn 서비스 상태 확인
sudo systemctl status library-ai

# Gunicorn 재시작
sudo systemctl restart library-ai

# Gunicorn 로그 확인
sudo journalctl -u library-ai -f

# Nginx 재시작
sudo systemctl restart nginx

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
```

### 주의사항

1. **소유권 관리**: 
   - Git 작업 시: 현재 사용자 소유 필요
   - Gunicorn 실행 시: `www-data` 소유 필요
   - 배포 스크립트가 자동으로 처리

2. **venv 디렉토리**: 
   - 항상 현재 사용자 소유로 유지 (실행 권한 보장)

3. **정적 파일**: 
   - `collectstatic` 후 `staticfiles` 디렉토리는 `www-data` 소유

4. **데이터베이스 연결**: 
   - Cloud SQL 인스턴스의 Authorized Networks에 VM IP 추가 필요

---

## 참고 자료

- [Django 공식 문서](https://docs.djangoproject.com/)
- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [Chart.js 문서](https://www.chartjs.org/docs/)
- [디자인 시스템 가이드](./design-system.md)


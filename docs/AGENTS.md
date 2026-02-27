# AGENTS 가이드라인

이 문서는 `@docs/AGENTS.md`를 참조할 때 프로젝트 구현에 적용할 최소 가이드라인이다.

---

## 디자인

- 스타일: Tailwind CSS, 실제 반영 기준은 `static/css/input.css`이며 컬러·간격 토큰은 `@theme`에서 관리한다.
- 컴포넌트 기준: `docs/daisyui-components-2026.md`를 우선 참조하고, 화면 구현 시 daisyUI 컴포넌트를 최우선으로 사용한다.
- 공통 색상 규칙: 브랜드 `#f65938`, 버튼 배경 `#2a3038`, 기본 텍스트 `#000000`, 기본 배경 `#ffffff`, 사이드바/헤더 배경 `#f3f4f5`를 항상 사용한다.
- 전역 액션 색상 규칙: `btn-primary`, `radio-primary` 등 활성/선택 상태 색상은 모든 화면에서 `#2a3038`로 통일하고, oklch 기본 테마색 노출을 금지한다.
- 컬러 시스템:
  - 브랜드 메인: `--color-brand` (#f65938) — 로고, 강조 요소에 사용. Tailwind: `bg-brand`, `text-brand`
  - 텍스트/버튼 배경: `--color-primary` (#2a3038) — 주요 텍스트, 버튼 배경에 사용. Tailwind: `bg-primary`, `text-primary`
  - 배경: `#ffffff` — 페이지·카드 배경. Tailwind: `bg-white`
  - 사이드바/헤더 배경: `--color-surface` (#f3f4f5) — 사이드바, 상단 헤더 배경. Tailwind: `bg-surface`
  - Success: `--color-success` (#16a34a) — 성공 상태
  - Danger: `--color-danger` (#dc2626) — 오류, 삭제 등 위험 액션
  - Secondary: `--color-secondary` (#78716c) — 보조 텍스트, 비활성 상태
- 폰트: Pretendard, 본문은 `text-base`/`text-sm`, 제목은 `text-xl`~`text-3xl`·`font-semibold`를 사용한다.
- 컴포넌트: 버튼·카드·입력은 `rounded-lg`/`rounded-xl`, 패딩 `px-4 py-3` 또는 `p-6`/`p-8` 수준으로 통일한다.
- 카드 레이아웃 간격: 카드 간 `세로/가로` 간격은 기본보다 넓게 유지한다(`gap-8` 이상, 섹션 간 `mb-14` 이상 권장).
- 대시보드 간격 규칙: 페이지 타이틀과 첫 카드 섹션, 카드 섹션 상호 간 간격이 겹쳐 보이지 않도록 `mb-14`~`mb-16` 수준의 여백을 기본 적용한다.
- 테이블 헤더 가독성 규칙: 헤더 행은 본문과 구분되는 배경색(`bg-surface`)을 기본 적용한다.
- 카드 내 콘텐츠 순서 규칙: 카드에서는 항상 `타이틀`을 먼저 배치하고, 필터는 타이틀 아래에 배치한다.
- 카드 중첩 금지 규칙: 카드 내부에 또 다른 카드(`card`)를 중첩하지 않는다. 카드 내부 구분은 여백/타이포/단순 보더로 처리한다.
- 필터 레이아웃 규칙: 기간 필터는 기본 `1열 블록`으로 구성하고, 순서는 `일간/주간/월간` → `기간(시작일~종료일)` → `적용` 순으로 통일한다.
- 링크/호버: `hover:bg-*-100`, `hover:text-primary`, `transition-colors` 또는 `transition-all duration-200`을 사용한다.
- 숫자: 천 단위 구분자(콤마)로 표시한다.
- 디스크립션 문구: 로그인 등 주요 화면의 부가 설명 텍스트는 기본적으로 노출하지 않는다.

---

## 개발

- 파일 생성/삭제: 사용자가 명시적으로 요청한 경우에만 수행한다.
- 코드 변경 전: 전체 구조를 파악한 뒤, 어떤 파일에 어떤 변경을 할지 사용자에게 제안하고 확인을 받는다.
- 변경 후: 변경 내용을 명시하고, 린터 오류를 확인·수정한다.
- 미사용 파일/코드는 확인 즉시 제거하고, 중복 역할 파일은 하나의 진입 파일로 통합한다.
- 백엔드: Django 5.x, Python 3.11+, 설정·DB URL·시크릿은 `.env`·`django-environ`으로 관리한다.
- 프론트: Django 템플릿 + `static/`(JS/CSS), CSS 빌드는 `static/css/input.css` → `output.css`(Tailwind + daisyUI) 기준이다.
- UI 구현: 가능한 경우 daisyUI 컴포넌트(`btn`, `card`, `table`, `modal`, `dropdown`, `menu` 등)를 우선·적극적으로 사용한다.
- 정적 파일: `STATICFILES_DIRS = [BASE_DIR / 'static']`, 배포 시 `collectstatic` → `staticfiles`를 사용한다.
- API 응답: JSON은 `JsonResponse({ 'success': True/False, 'data'|'error': ... })` 형태로 통일한다.
- 인증: 관리자/대시보드 등 보호된 뷰에는 `@login_required`를 적용한다.

---

## 인프라

- 로컬: `python manage.py runserver`, CSS 감시는 `static/css/tailwindcss ... --watch`로 실행한다.
- 프로덕션: `DEBUG=False`, `ALLOWED_HOSTS`·`SECRET_KEY`·`DATABASE_URL`은 환경 변수로 설정한다.
- WSGI: Gunicorn 사용, 정적 파일은 Nginx 등 리버스 프록시에서 서빙한다.
- 배포: `pip install -r requirements.txt`, CSS 빌드, `collectstatic`, `migrate` 순서로 실행한다.
- 비밀/키: 코드·커밋에 시크릿·API 키를 넣지 않고, `.env` 또는 서버 환경 변수만 사용한다.

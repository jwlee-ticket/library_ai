# 디자인 시스템

Library AI 프로젝트의 디자인 시스템 가이드입니다.

## 디자인 원칙

본 프로젝트는 **토스(Toss) 디자인 철학**을 기반으로 하되, **Mixpanel의 데이터 대시보드 구조**를 참고하여 디자인되었습니다. 토스의 친근하고 부드러운 디자인과 Mixpanel의 데이터 중심 구조를 결합하여, 공연업계 종사자들이 쉽고 편하게 사용할 수 있는 대시보드를 만듭니다.

### 디자인 철학: 토스 + Mixpanel 결합

**토스의 친근함과 부드러움:**
- **친근한 커뮤니케이션**: 딱딱하지 않고 부드럽고 친근한 톤으로 사용자와 소통
- **명확하고 간결한 표현**: 복잡한 정보도 쉽고 명확하게 전달
- **여유 있는 공간**: 충분한 여백으로 편안한 느낌 제공
- **부드러운 시각적 요소**: 둥근 모서리, 부드러운 그림자로 따뜻한 느낌
- **직관적인 인터페이스**: 누구나 쉽게 사용할 수 있는 명확한 구조

**Mixpanel의 데이터 중심 구조:**
- **데이터 시각화 중심**: 차트와 그래프를 명확하고 읽기 쉽게 표현
- **명확한 정보 계층**: 데이터를 논리적으로 배치하여 쉽게 탐색하고 이해
- **섹션 기반 레이아웃**: 좌우 분할 구조로 설명과 데이터를 명확히 구분
- **효율적인 공간 활용**: 데이터 카드 그리드를 통한 정보 밀도 최적화

### 사용자 중심 설계
- 비전문가(공연업계 종사자)가 부담 없이 사용할 수 있는 친근한 디자인
- 복잡한 데이터도 쉽고 명확하게 표현하여 이해하기 쉽게
- 데이터 분석 도구의 강력함과 사용 편의성의 균형

## 톤앤보이스

Library AI는 공연업계 종사자들이 편안하고 자신감 있게 사용할 수 있도록 **따뜻하고 다정하며, 명확하고 간결한** 커뮤니케이션을 지향합니다.

- **따뜻하고 다정함**: 사용자를 배려하는 친근한 말투로, 딱딱한 업무용 표현보다는 자연스러운 대화 톤을 사용합니다. 사용자의 실수를 비난하지 않고 도움을 제공합니다.
- **명확하고 간결함**: 전문 용어를 피하고 누구나 이해할 수 있는 표현을 사용하며, 불필요한 설명을 제거하고 핵심만 전달합니다.
- **어요/해요 체 사용**: "공연이 성공적으로 등록되었어요", "삭제된 공연은 복구할 수 없어요"처럼 어요/해요 체를 사용하여 친근한 느낌을 줍니다.
- **사용자 중심**: 사용자의 성공을 응원하는 긍정적인 메시지와, 문제 발생 시 해결 방법을 제시하는 도움말을 제공합니다.

## 코드 네이밍 가이드

**중요**: 코드에는 외부 서비스 이름(토스, Mixpanel 등)을 사용하지 않습니다.

### HTML/CSS 클래스명 (소문자 또는 kebab-case)
- `btn-primary`, `btn-success`, `btn-danger`
- `card`, `card-dashboard`
- `input`, `input-text`
- `chart`, `chart-line`, `chart-bar`

### Python 클래스명 (PascalCase)
- `Button`, `PrimaryButton`, `SecondaryButton`
- `Card`, `DashboardCard`
- `Input`, `TextInput`
- `Chart`, `LineChart`, `BarChart`

### 잘못된 네이밍 (사용 금지)
- `TossButton`, `toss-button`
- `MixpanelButton`, `mixpanel-button`
- `TossCard`, `toss-card`
- `MixpanelCard`, `mixpanel-card`

일반적인 컴포넌트 이름을 사용하여 기능과 역할을 명확하게 표현합니다.

## 컬러 시스템

### 브랜드 컬러
- **Brand**: `#f65938` - 로고, 브랜드명, 브랜드 요소에만 사용 (Tailwind: `bg-[#f65938]`)

### 액션 컬러
- **Primary**: `#2a3038` - 주요 액션 버튼 (확인, 저장, 제출 등) (Tailwind: `bg-[#2a3038]`)
- **Success**: `#16a34a` - 성공 메시지, 완료 버튼 (Tailwind: `bg-[#16a34a]`)
- **Danger**: `#dc2626` - 삭제, 취소, 경고 버튼 (Tailwind: `bg-[#dc2626]`)
- **Secondary**: `#78716c` - 보조 버튼, 비활성화 상태 (Tailwind: `bg-[#78716c]`)

### 링크 컬러
- **Link**: `#2a3038` - 텍스트 링크, 네비게이션 링크 (Tailwind: `text-[#2a3038]`)

### 배경
- **White**: `#ffffff` - 기본 배경색 (Tailwind: `bg-white`)
- **Dark Slate**: `#2a3038` - 어두운 배경, 강조 영역, 구분선 (Tailwind: `bg-[#2a3038]`)

### 텍스트
- **Primary Text**: `#000000` - 주요 텍스트, 제목 (Tailwind: `text-black`)
- **Secondary Text**: `#666666` - 보조 텍스트, 설명, 라벨 (Tailwind: `text-gray-600`)
- **Dark Text**: `#2a3038` - 강조 텍스트, 어두운 배경 위의 텍스트 (Tailwind: `text-[#2a3038]`)

### 사용 예시
```html
<!-- 브랜드 컬러 (로고, 브랜드명) -->
<div class="text-[#f65938] font-semibold text-lg">Library AI</div>

<!-- Dark Slate 배경 (사이드바, 강조 영역) -->
<div class="bg-[#2a3038] text-white p-6 rounded-xl">
  <h3 class="text-white font-semibold">강조 영역</h3>
</div>

<!-- Dark Slate 텍스트 (강조 텍스트) -->
<h2 class="text-[#2a3038] text-2xl font-semibold">강조 제목</h2>

<!-- Dark Slate 구분선 -->
<div class="border-t border-[#2a3038] opacity-20 my-6"></div>

<!-- Primary 버튼 (확인, 저장) -->
<button class="bg-[#2a3038] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#2a3038]/90 active:bg-[#2a3038]/80 transition-colors shadow-sm">
  확인
</button>

<!-- Success 버튼 -->
<button class="bg-[#16a34a] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#15803d] transition-colors shadow-sm">
  완료
</button>

<!-- Danger 버튼 -->
<button class="bg-[#dc2626] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#b91c1c] transition-colors shadow-sm">
  삭제
</button>

<!-- 링크 -->
<a href="#" class="text-[#2a3038] hover:text-[#2a3038]/80 hover:underline transition-colors">링크 텍스트</a>

<!-- Primary 텍스트 -->
<h1 class="text-black text-2xl font-semibold mb-2">제목</h1>

<!-- Secondary 텍스트 -->
<p class="text-gray-600 text-base leading-relaxed">보조 설명</p>
```

## 타이포그래피

### 폰트
- **폰트 패밀리**: Pretendard
- **폰트 스택**: `'Pretendard', -apple-system, BlinkMacSystemFont, sans-serif`

### 폰트 크기
- **제목 1**: `text-3xl` (1.875rem / 30px) - 페이지 제목
- **제목 2**: `text-2xl` (1.5rem / 24px) - 섹션 제목
- **제목 3**: `text-xl` (1.25rem / 20px) - 소제목
- **본문**: `text-base` (1rem / 16px) - 기본 텍스트
- **보조 텍스트**: `text-sm` (0.875rem / 14px) - 설명, 라벨

### 폰트 가중치
- **Regular**: `font-normal` (400) - 기본 텍스트
- **Medium**: `font-medium` (500) - 강조 텍스트
- **Semibold**: `font-semibold` (600) - 제목
- **Bold**: `font-bold` (700) - 강한 강조

### 사용 예시
```html
<h1 class="text-3xl font-semibold text-black">페이지 제목</h1>
<h2 class="text-2xl font-semibold text-black">섹션 제목</h2>
<p class="text-base font-normal text-black">본문 텍스트</p>
<span class="text-sm font-normal text-gray-600">보조 텍스트</span>
```

## 간격 시스템

Tailwind CSS의 간격 시스템을 사용합니다.

### 주요 간격
- `p-2` (0.5rem / 8px) - 작은 패딩
- `p-4` (1rem / 16px) - 기본 패딩
- `p-6` (1.5rem / 24px) - 큰 패딩
- `p-8` (2rem / 32px) - 매우 큰 패딩

### 간격 사용 규칙
- 카드 내부: `p-6` 또는 `p-8` (더 넉넉한 여백)
- 섹션 간격: `mb-8` 또는 `mb-12` (충분한 공간)
- 요소 간격: `gap-6` 또는 `space-y-6` (편안한 간격)
- 버튼 패딩: `px-6 py-3` (터치하기 좋은 크기)

### 사용 예시
```html
<!-- 넉넉한 여백을 활용한 레이아웃 -->
<div class="p-8 mb-12">
  <h2 class="mb-6 text-2xl font-semibold">제목</h2>
  <p class="mb-4 text-base leading-relaxed">내용</p>
</div>

<!-- 카드 내부 여백 -->
<div class="bg-white rounded-xl p-8 mb-8">
  <h3 class="mb-6">카드 제목</h3>
  <p class="mb-4">카드 내용</p>
</div>
```

## 컴포넌트 가이드

### 버튼

#### Primary Button (확인, 저장, 제출)
브랜드 컬러와 조화로운 어두운 슬레이트 색상의 주요 액션 버튼입니다.
```html
<button class="bg-[#2a3038] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#2a3038]/90 active:bg-[#2a3038]/80 transition-colors shadow-sm">
  확인
</button>
```

#### Success Button (완료, 성공)
성공이나 완료를 나타내는 버튼입니다.
```html
<button class="bg-[#16a34a] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#15803d] active:bg-[#166534] transition-colors shadow-sm">
  완료
</button>
```

#### Danger Button (삭제, 취소, 경고)
주의가 필요한 액션을 나타내는 버튼입니다.
```html
<button class="bg-[#dc2626] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#b91c1c] active:bg-[#991b1b] transition-colors shadow-sm">
  삭제
</button>
```

#### Secondary Button (보조 액션)
보조적인 액션을 위한 버튼입니다.
```html
<button class="bg-[#78716c] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#57534e] active:bg-[#44403c] transition-colors shadow-sm">
  취소
</button>
```

#### Outline Button
부드러운 테두리 스타일의 버튼입니다.
```html
<button class="bg-white text-black border-2 border-gray-200 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 hover:border-gray-300 transition-colors">
  취소
</button>
```

### 입력 필드

#### Text Input
부드럽고 친근한 느낌의 입력 필드입니다.
```html
<div class="mb-4">
  <label class="block text-sm font-medium text-black mb-2">라벨</label>
  <input type="text" class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-[#2a3038] focus:ring-2 focus:ring-[#2a3038]/20 transition-colors">
</div>
```

#### Password Input
비밀번호 입력 필드입니다.
```html
<div class="mb-4">
  <label class="block text-sm font-medium text-black mb-2">비밀번호</label>
  <input type="password" class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-[#2a3038] focus:ring-2 focus:ring-[#2a3038]/20 transition-colors">
</div>
```

### 카드/컨테이너

#### 기본 카드
부드럽고 친근한 느낌의 기본 카드입니다.
```html
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 hover:shadow-md transition-shadow">
  <h3 class="text-xl font-semibold text-black mb-4">카드 제목</h3>
  <p class="text-base text-gray-600 leading-relaxed">카드 내용</p>
</div>
```

#### 대시보드 카드
대시보드에서 사용하는 카드입니다.
```html
<div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6 hover:shadow-md transition-shadow">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-xl font-semibold text-black">대시보드 제목</h3>
    <span class="text-sm text-gray-600">2025년 11월</span>
  </div>
  <!-- 차트 또는 데이터 -->
</div>
```

#### 데이터 카드 (섹션 내)
섹션 내에서 사용하는 데이터 카드입니다. 최소 높이를 설정하여 일관된 레이아웃을 유지합니다.

```html
<div class="bg-white rounded-xl border border-gray-100 p-6 min-h-[200px] flex flex-col hover:shadow-md transition-shadow">
  <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
  <!-- 차트 또는 데이터 -->
</div>
```

#### 잠금 상태 카드
권한이 없는 데이터를 표시할 때 사용하는 카드입니다. 친근한 메시지로 안내합니다.

```html
<div class="bg-white rounded-xl border border-gray-100 p-6 min-h-[200px] flex flex-col">
  <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
  <div class="flex-1 flex items-center justify-center flex-col text-gray-400">
    <svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
    </svg>
    <p class="text-sm text-gray-500">이 데이터를 보려면 권한이 필요합니다</p>
  </div>
</div>
```

### 차트 스타일

Chart.js를 사용하며, 다음 스타일을 적용합니다:

#### 컬러 팔레트
- Primary (액션): `#2a3038`
- Success: `#16a34a`
- Danger: `#dc2626`
- Background: `#ffffff`
- Grid: `#e5e5e5`

#### 차트 설정 예시
```javascript
const chartConfig = {
  backgroundColor: '#ffffff',
  borderColor: '#2a3038',  // Primary 액션 컬러
  pointBackgroundColor: '#2a3038',
  successColor: '#16a34a',  // Success 컬러
  dangerColor: '#dc2626',   // Danger 컬러
  gridColor: '#e5e5e5',
  textColor: '#000000',
  fontFamily: 'Pretendard, sans-serif',
};
```

## 레이아웃

### 대시보드 메인 레이아웃 구조

토스 디자인 철학을 적용한 데이터 대시보드 레이아웃입니다. Mixpanel의 데이터 중심 구조를 참고하되, 토스의 친근하고 부드러운 디자인 스타일을 적용합니다.

#### 전체 구조
- 최상위 컨테이너: 전체 화면 높이, 흰색 배경, flex 레이아웃
- 좌측 사이드바: 고정 위치, 흰색 배경, 오른쪽 테두리로 구분, 전체 화면 높이
- 메인 영역: 사이드바 너비만큼 왼쪽 마진, flex 컬럼 레이아웃
  - 상단 헤더: sticky 위치, 흰색 배경, 하단 테두리
  - 메인 콘텐츠: 스크롤 가능, 넉넉한 패딩 적용

#### 좌측 사이드바
- 고정 위치 (fixed)
- 배경 옵션:
  - 흰색 배경 (`bg-white`) - 기본 스타일
  - 어두운 배경 (`bg-[#2a3038]`) - 브랜드 컬러와 조화로운 강조 스타일
- 오른쪽 테두리로 구분 (`border-r border-gray-100` 또는 어두운 배경 시 `border-r border-[#1f252b]`)
- 전체 화면 높이
- 네비게이션 메뉴 포함
- 부드러운 호버 효과:
  - 흰색 배경: `hover:bg-gray-50`
  - 어두운 배경: `hover:bg-[#1f252b]` (더 어두운 톤)

#### 상단 헤더
- Sticky 위치 (스크롤 시 상단 고정)
- 흰색 배경
- 하단 테두리 (`border-b border-gray-100`)
- 브레드크럼, 날짜 선택기, 액션 버튼 등 포함
- 넉넉한 패딩 (`px-6 py-4`)

### 데이터 대시보드 레이아웃 패턴

토스의 친근한 디자인과 Mixpanel의 데이터 중심 구조를 결합한 대시보드 레이아웃입니다.

#### 섹션 레이아웃 (좌우 분할)
각 섹션은 좌측에 설명 텍스트, 우측에 데이터 카드 그리드로 구성됩니다. 토스 스타일의 넉넉한 여백과 부드러운 카드 디자인을 적용합니다.

**구조:**
- 섹션 컨테이너: 충분한 하단 여백 (`mb-12` 또는 `mb-16`)
- 좌측 설명 영역: 1/3 너비, 친근한 설명 텍스트
- 우측 데이터 영역: 2/3 너비, 카드 그리드 (2x2 또는 2x1)

**특징:**
- 넉넉한 여백으로 편안한 느낌
- 부드러운 카드 디자인 (`rounded-xl`, `border-gray-100`)
- 호버 효과로 인터랙티브한 느낌 (`hover:shadow-md`)
- 명확한 정보 계층 구조

#### 데이터 카드 그리드
- 2열 그리드: `grid-cols-1 md:grid-cols-2`
- 카드 간격: `gap-6` (편안한 간격)
- 카드 스타일: `rounded-xl`, `border-gray-100`, `p-6` 또는 `p-8`
- 최소 높이: `min-h-[200px]` (일관된 레이아웃)

#### 날짜 선택기 영역
헤더 하단에 날짜 선택 버튼들을 배치합니다. 토스 스타일의 부드러운 버튼 디자인을 적용합니다.

**버튼 스타일:**
- 기본 버튼: `px-4 py-2 rounded-lg border-2 border-gray-200 hover:bg-gray-50`
- 활성 버튼: `bg-[#2a3038]/10 border-[#2a3038]/30 text-[#2a3038]`
- 부드러운 전환: `transition-colors`

#### 브레드크럼
현재 위치를 명확하게 표시합니다. 토스 스타일의 친근한 톤으로 표현합니다.

**스타일:**
- 텍스트 크기: `text-sm`
- 색상: 기본 `text-gray-600`, 현재 페이지 `text-black font-medium`
- 구분자: `/` 또는 `>` 사용

## 아이콘/이미지

### 아이콘
- 필요 시 Heroicons 또는 유사한 라이브러리 사용
- 크기: `w-5 h-5` (기본), `w-6 h-6` (큰 아이콘)
- 색상: `text-black` 또는 `text-gray-600`

### 이미지
- 최적화된 이미지 사용
- 반응형: `w-full` 또는 `max-w-full`
- 라운드: 필요 시 `rounded-lg`

## 사용 가이드

### DO
- 친근하고 부드러운 톤으로 사용자와 소통
- 충분한 여백으로 편안한 느낌 제공
- 둥근 모서리와 부드러운 그림자 활용
- 명확하고 간결한 표현
- 일관된 컬러 사용
- 읽기 쉬운 폰트 크기

### DON'T
- 딱딱하고 차가운 느낌의 디자인
- 과도한 색상 사용
- 복잡하고 어려운 레이아웃
- 작은 폰트 크기
- 밀집되고 답답한 요소 배치
- 날카롭고 각진 디자인 요소

## 참고

- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [Chart.js 문서](https://www.chartjs.org/docs/)
- [Pretendard 폰트](https://github.com/orioncactus/pretendard)


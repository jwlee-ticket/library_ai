# 디자인 시스템

Library AI 프로젝트의 디자인 시스템 가이드입니다.

## 디자인 원칙

본 프로젝트는 **Mixpanel 스타일**을 참고하여 디자인되었습니다. Mixpanel의 디자인 철학을 따르되, 코드에는 외부 서비스 이름을 사용하지 않습니다.

### 참고 스타일: Mixpanel
- **심플한 인터페이스**: 불필요한 요소를 최소화하여 핵심 정보에 집중
- **명확한 정보 구조**: 데이터를 논리적으로 배치하여 쉽게 탐색하고 이해
- **데이터 시각화 중심**: 차트와 그래프를 명확하고 읽기 쉽게 표현
- **일관된 색상 사용**: 주요 기능과 데이터 포인트를 강조하기 위해 일관된 색상 팔레트 활용
- **반응형 디자인**: 다양한 디바이스와 화면 크기에 최적화

### 사용자 중심 설계
- 비전문가(공연업계 종사자)가 쉽게 이해할 수 있는 직관적인 디자인
- 복잡한 데이터를 명확하게 표현

## 코드 네이밍 가이드

**중요**: 코드에는 외부 서비스 이름(Mixpanel 등)을 사용하지 않습니다.

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
- `MixpanelButton`, `mixpanel-button`
- `MixpanelCard`, `mixpanel-card`
- `MixpanelChart`, `mixpanel-chart`

일반적인 컴포넌트 이름을 사용하여 기능과 역할을 명확하게 표현합니다.

## 컬러 시스템

### 브랜드 컬러
- **Brand**: `#f65938` <span style="display: inline-block; width: 20px; height: 20px; background-color: #f65938; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 로고, 브랜드명, 브랜드 요소에만 사용
  - Tailwind: `bg-[#f65938]` 또는 커스텀 클래스

### 액션 컬러
- **Primary**: `#3b82f6` <span style="display: inline-block; width: 20px; height: 20px; background-color: #3b82f6; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 주요 액션 버튼 (확인, 저장, 제출 등)
  - Tailwind: `bg-blue-500`

- **Success**: `#10b981` <span style="display: inline-block; width: 20px; height: 20px; background-color: #10b981; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 성공 메시지, 완료 버튼
  - Tailwind: `bg-green-500`

- **Danger**: `#ef4444` <span style="display: inline-block; width: 20px; height: 20px; background-color: #ef4444; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 삭제, 취소, 경고 버튼
  - Tailwind: `bg-red-500`

- **Secondary**: `#6b7280` <span style="display: inline-block; width: 20px; height: 20px; background-color: #6b7280; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 보조 버튼, 비활성화 상태
  - Tailwind: `bg-gray-500`

### 링크 컬러
- **Link**: `#2563eb` <span style="display: inline-block; width: 20px; height: 20px; background-color: #2563eb; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 텍스트 링크, 네비게이션 링크
  - Tailwind: `text-blue-600`

### 배경
- **White**: `#ffffff` <span style="display: inline-block; width: 20px; height: 20px; background-color: #ffffff; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 기본 배경색
  - Tailwind: `bg-white`

### 텍스트
- **Primary Text**: `#000000` <span style="display: inline-block; width: 20px; height: 20px; background-color: #000000; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 주요 텍스트, 제목
  - Tailwind: `text-black`

- **Secondary Text**: `#666666` <span style="display: inline-block; width: 20px; height: 20px; background-color: #666666; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
  - 보조 텍스트, 설명, 라벨
  - Tailwind: `text-gray-600`

### 사용 예시
```html
<!-- 브랜드 컬러 (로고, 브랜드명) -->
<div class="text-[#f65938] font-semibold">Library AI</div>

<!-- Primary 버튼 (확인, 저장) -->
<button class="bg-blue-500 text-white px-4 py-2 rounded">
  확인
</button>

<!-- Success 버튼 -->
<button class="bg-green-500 text-white px-4 py-2 rounded">
  완료
</button>

<!-- Danger 버튼 -->
<button class="bg-red-500 text-white px-4 py-2 rounded">
  삭제
</button>

<!-- 링크 -->
<a href="#" class="text-blue-600 hover:underline">링크 텍스트</a>

<!-- Primary 텍스트 -->
<h1 class="text-black">제목</h1>

<!-- Secondary 텍스트 -->
<p class="text-gray-600">보조 설명</p>
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
- 카드 내부: `p-6`
- 섹션 간격: `mb-8`
- 요소 간격: `gap-4` 또는 `space-y-4`

### 사용 예시
```html
<div class="p-6 mb-8">
  <h2 class="mb-4">제목</h2>
  <p class="mb-2">내용</p>
</div>
```

## 컴포넌트 가이드

### 버튼

#### Primary Button (확인, 저장, 제출)
```html
<button class="bg-blue-500 text-white px-4 py-2 rounded font-medium hover:bg-blue-600 active:bg-blue-700">
  확인
</button>
```

#### Success Button (완료, 성공)
```html
<button class="bg-green-500 text-white px-4 py-2 rounded font-medium hover:bg-green-600 active:bg-green-700">
  완료
</button>
```

#### Danger Button (삭제, 취소, 경고)
```html
<button class="bg-red-500 text-white px-4 py-2 rounded font-medium hover:bg-red-600 active:bg-red-700">
  삭제
</button>
```

#### Secondary Button (보조 액션)
```html
<button class="bg-gray-500 text-white px-4 py-2 rounded font-medium hover:bg-gray-600 active:bg-gray-700">
  취소
</button>
```

#### Outline Button
```html
<button class="bg-white text-black border border-gray-300 px-4 py-2 rounded font-medium hover:bg-gray-50">
  취소
</button>
```

### 입력 필드

#### Text Input
```html
<div class="mb-4">
  <label class="block text-sm font-medium text-black mb-2">라벨</label>
  <input type="text" class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500">
</div>
```

#### Password Input
```html
<div class="mb-4">
  <label class="block text-sm font-medium text-black mb-2">비밀번호</label>
  <input type="password" class="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-blue-500">
</div>
```

### 카드/컨테이너

#### 기본 카드
```html
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
  <h3 class="text-xl font-semibold text-black mb-4">카드 제목</h3>
  <p class="text-base text-gray-600">카드 내용</p>
</div>
```

#### 대시보드 카드
```html
<div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
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
<div class="bg-white rounded-lg border border-gray-200 p-6 min-h-[200px] flex flex-col">
  <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
  <!-- 차트 또는 데이터 -->
</div>
```

#### 잠금 상태 카드
권한이 없는 데이터를 표시할 때 사용하는 카드입니다.

```html
<div class="bg-white rounded-lg border border-gray-200 p-6 min-h-[200px] flex flex-col">
  <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
  <div class="flex-1 flex items-center justify-center flex-col text-gray-400">
    <svg class="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
    </svg>
    <p class="text-sm">Unauthorized for report's data view</p>
  </div>
</div>
```

### 차트 스타일

Chart.js를 사용하며, 다음 스타일을 적용합니다:

#### 컬러 팔레트
- Primary (액션): `#3b82f6` <span style="display: inline-block; width: 20px; height: 20px; background-color: #3b82f6; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
- Success: `#10b981` <span style="display: inline-block; width: 20px; height: 20px; background-color: #10b981; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
- Danger: `#ef4444` <span style="display: inline-block; width: 20px; height: 20px; background-color: #ef4444; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
- Background: `#ffffff` <span style="display: inline-block; width: 20px; height: 20px; background-color: #ffffff; border: 1px solid #e5e5e5; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>
- Grid: `#e5e5e5` <span style="display: inline-block; width: 20px; height: 20px; background-color: #e5e5e5; border: 1px solid #cccccc; border-radius: 3px; vertical-align: middle; margin-left: 8px;"></span>

#### 차트 설정 예시
```javascript
const chartConfig = {
  backgroundColor: '#ffffff',
  borderColor: '#3b82f6',  // Primary 액션 컬러
  pointBackgroundColor: '#3b82f6',
  gridColor: '#e5e5e5',
  textColor: '#000000',
  fontFamily: 'Pretendard, sans-serif',
};
```

## 레이아웃

### 대시보드 메인 레이아웃 구조

Mixpanel 스타일의 대시보드 메인 페이지 레이아웃입니다.

#### 전체 구조
```html
<div class="min-h-screen bg-white flex">
  <!-- 좌측 사이드바 (고정) -->
  <aside class="w-64 bg-gray-800 text-white fixed left-0 top-0 h-screen">
    <!-- 사이드바 내용 -->
  </aside>
  
  <!-- 메인 영역 (사이드바 너비만큼 왼쪽 마진) -->
  <div class="flex-1 flex flex-col ml-64">
    <!-- 상단 헤더 -->
    <header class="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
      <!-- 브레드크럼, 날짜 선택기, 액션 버튼 -->
    </header>
    
    <!-- 메인 콘텐츠 -->
    <main class="flex-1 overflow-y-auto p-6 bg-white">
      <!-- 페이지 제목 -->
      <h1 class="text-3xl font-semibold text-black mb-8">페이지 제목</h1>
      
      <!-- 섹션들 -->
      <!-- 페이지 내용 -->
    </main>
  </div>
</div>
```

### 섹션 레이아웃 패턴

#### 좌우 분할 레이아웃 (텍스트 + 카드 그리드)
각 섹션은 좌측에 설명 텍스트, 우측에 데이터 카드 그리드로 구성됩니다. 섹션 간 충분한 간격을 유지합니다.

```html
<!-- 섹션 컨테이너 -->
<div class="mb-16">
  <!-- 섹션 제목 -->
  <h2 class="text-2xl font-semibold text-black mb-8">섹션 제목</h2>
  
  <!-- 좌우 분할 레이아웃 -->
  <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
    <!-- 좌측: 설명 텍스트 -->
    <div class="lg:col-span-1">
      <h3 class="text-xl font-semibold text-black mb-4">설명 제목</h3>
      <p class="text-base text-gray-600 mb-4 leading-relaxed">설명 텍스트가 여기에 표시됩니다. 여러 문단으로 구성될 수 있습니다.</p>
      
      <!-- 불릿 포인트 -->
      <ul class="list-disc list-inside text-base text-gray-600 mb-4 space-y-2">
        <li>첫 번째 포인트</li>
        <li>두 번째 포인트</li>
        <li>세 번째 포인트</li>
      </ul>
      
      <!-- Tip 섹션 -->
      <div class="bg-blue-50 border border-blue-200 rounded p-4">
        <p class="text-sm font-medium text-blue-900 mb-1">Tip</p>
        <p class="text-sm text-blue-800">유용한 팁이나 추가 정보가 여기에 표시됩니다.</p>
      </div>
    </div>
    
    <!-- 우측: 카드 그리드 (2x2 또는 2x1) -->
    <div class="lg:col-span-2">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- 카드 1 -->
        <div class="bg-white rounded-lg border border-gray-200 p-6 min-h-[200px] flex flex-col">
          <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
          <!-- 차트 또는 데이터 -->
          <!-- 잠금 상태 예시 -->
          <div class="flex-1 flex items-center justify-center flex-col text-gray-400">
            <svg class="w-12 h-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
            </svg>
            <p class="text-sm">Unauthorized for report's data view</p>
          </div>
        </div>
        
        <!-- 카드 2 -->
        <div class="bg-white rounded-lg border border-gray-200 p-6 min-h-[200px] flex flex-col">
          <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
          <!-- 차트 또는 데이터 -->
        </div>
        
        <!-- 카드 3 (2x1 레이아웃의 경우) -->
        <div class="bg-white rounded-lg border border-gray-200 p-6 min-h-[200px] flex flex-col md:col-span-2">
          <h4 class="text-lg font-semibold text-black mb-4">카드 제목</h4>
          <!-- 차트 또는 데이터 -->
        </div>
      </div>
    </div>
  </div>
</div>
```

#### 좌측 사이드바
```html
<aside class="w-64 bg-gray-800 text-white flex flex-col h-screen fixed left-0 top-0">
  <!-- 상단: Create New 버튼 -->
  <div class="p-4 border-b border-gray-700">
    <button class="w-full bg-blue-500 text-white px-4 py-2 rounded font-medium hover:bg-blue-600">
      Create New
    </button>
  </div>
  
  <!-- 네비게이션 메뉴 -->
  <nav class="flex-1 p-4 overflow-y-auto">
    <ul class="space-y-1 mb-6">
      <li>
        <a href="#" class="flex items-center gap-3 px-3 py-2 rounded hover:bg-gray-700 text-sm">
          Search
        </a>
      </li>
      <li>
        <a href="#" class="flex items-center gap-3 px-3 py-2 rounded hover:bg-gray-700 text-sm">
          Discover
        </a>
      </li>
      <li>
        <a href="#" class="flex items-center gap-3 px-3 py-2 rounded hover:bg-gray-700 text-sm">
          Data
        </a>
      </li>
      <li>
        <a href="#" class="flex items-center gap-3 px-3 py-2 rounded hover:bg-gray-700 text-sm">
          Session Replay
        </a>
      </li>
    </ul>
    
    <!-- 템플릿 섹션 -->
    <div class="mb-6">
      <div class="flex items-center justify-between px-3 py-2 mb-2">
        <span class="text-xs font-semibold text-gray-400 uppercase">Templates</span>
        <button class="text-gray-400 hover:text-white">▼</button>
      </div>
      <ul class="space-y-1">
        <li>
          <a href="#" class="flex items-center gap-2 px-3 py-2 rounded bg-gray-700 text-sm font-medium">
            Marketing KPIs Sample Template
          </a>
        </li>
        <!-- 추가 템플릿들 -->
      </ul>
    </div>
    
    <!-- 학습 섹션 -->
    <div class="px-3 py-2 border-t border-gray-700">
      <a href="#" class="text-sm text-gray-400 hover:text-white">Learning Center</a>
    </div>
  </nav>
  
  <!-- 하단: 설정, 프로필 -->
  <div class="p-4 border-t border-gray-700">
    <div class="flex items-center justify-between">
      <button class="text-gray-400 hover:text-white">
        <!-- 설정 아이콘 -->
      </button>
      <button class="text-gray-400 hover:text-white">
        <!-- 프로필 아이콘 -->
      </button>
    </div>
  </div>
</aside>
```

#### 상단 헤더
```html
<header class="bg-white border-b border-gray-200 px-6 py-4 ml-64">
  <!-- 상단: 브레드크럼, 액션 버튼 -->
  <div class="flex items-center justify-between mb-3">
    <div class="flex items-center gap-2 text-sm text-gray-600">
      <span>E-Commerce</span>
      <span>/</span>
      <span class="text-black font-medium">Marketing KPIs Sample Template</span>
    </div>
    <div class="flex items-center gap-4">
      <button class="text-gray-600 hover:text-black text-sm">Subscribe</button>
      <button class="text-gray-600 hover:text-black text-sm">Share</button>
      <button class="text-gray-600 hover:text-black text-sm">Favorite</button>
      <button class="text-gray-600 hover:text-black text-sm">More</button>
    </div>
  </div>
  
  <!-- 하단: 날짜 선택기 -->
  <div class="flex items-center gap-2 flex-wrap">
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">Custom</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">Today</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">Yesterday</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">7D</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">30D</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">3M</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">6M</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">YTD</button>
    <button class="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50">Default</button>
    <button class="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 ml-auto">
      Use this board
    </button>
  </div>
  
  <!-- 알림 배너 (선택사항) -->
  <div class="mt-3 p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
    Welcome! You are viewing a demo project
  </div>
</header>
```

### 그리드 시스템
- Tailwind CSS Grid 사용
- 카드 그리드: `grid-cols-1 md:grid-cols-2` (2열)
- 좌우 분할: `grid-cols-1 lg:grid-cols-3` (좌측 1/3, 우측 2/3)

### 반응형 브레이크포인트
- **sm**: 640px 이상
- **md**: 768px 이상
- **lg**: 1024px 이상
- **xl**: 1280px 이상

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
- 일관된 컬러 사용
- 명확한 정보 계층 구조
- 충분한 여백
- 읽기 쉬운 폰트 크기

### DON'T
- 과도한 색상 사용
- 복잡한 레이아웃
- 작은 폰트 크기
- 밀집된 요소 배치

## 참고

- [Tailwind CSS 문서](https://tailwindcss.com/docs)
- [Chart.js 문서](https://www.chartjs.org/docs/)
- [Pretendard 폰트](https://github.com/orioncactus/pretendard)


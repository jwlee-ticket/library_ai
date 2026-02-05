// 콘서트 통합 대시보드 JavaScript
// 데이터는 HTML의 <script type="application/json" id="concert-aggregated-data"> 태그에서 로드됩니다.

// 전역 변수
let summaryDataUrl = null;
let periodRevenueUrl = null;
let periodRevenueChart = null;
let currentPeriodData = null;
let currentTablePeriodData = null;

/**
 * JSON 안전 파싱 함수
 */
function parseJsonSafely(jsonString) {
    if (!jsonString || jsonString.trim() === '') {
        return null;
    }
    try {
        return JSON.parse(jsonString);
    } catch (e) {
        console.error('JSON 파싱 오류:', e);
        return null;
    }
}

/**
 * 숫자 포맷팅 (천 단위 구분자)
 */
function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) {
        return '0';
    }
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * CSS 변수에서 색상 가져오기
 */
function getCSSVariable(variableName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(variableName)
        .trim();
}

// 동적 색상 팔레트 (CSS 변수에서 가져옴)
const dynamicColors = [
    getCSSVariable('--color-chart-site-5'),
    getCSSVariable('--color-chart-site-6'),
    getCSSVariable('--color-chart-site-7'),
    getCSSVariable('--color-chart-site-8'),
];

/**
 * 요약 데이터 로드
 */
async function loadSummaryData() {
    if (!summaryDataUrl) {
        console.error('요약 데이터 URL이 설정되지 않았습니다.');
        return;
    }
    
    try {
        const response = await fetch(summaryDataUrl);
        if (!response.ok) {
            throw new Error('데이터를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateSummaryCards(data.data);
        } else {
            console.error('데이터 로드 실패:', data.error);
            alert('데이터를 불러올 수 없습니다: ' + (data.error || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('데이터 로드 오류:', error);
        alert('데이터를 불러오는 중 오류가 발생했습니다.');
    }
}

/**
 * 요약 카드 업데이트
 */
function updateSummaryCards(data) {
    if (!data) return;
    
    // 오늘 매출
    const todayRevenueEl = document.getElementById('aggregated-today-revenue');
    if (todayRevenueEl) {
        const todayRevenue = data.today_revenue || 0;
        todayRevenueEl.innerHTML = '<span class="text-black">' + formatNumber(Math.round(todayRevenue)) + '</span>원';
    }
    
    // 매출 프로그래스바 계산
    const totalRevenue = data.total_revenue || 0;
    const totalTargetRevenue = data.total_target_revenue || 0;
    const totalBreakEvenPoint = data.total_break_even_point || 0;
    
    const revenueBar = document.getElementById('aggregated-revenue-progress-bar');
    const revenueText = document.getElementById('aggregated-total-revenue-text');
    const bepMarker = document.getElementById('aggregated-revenue-bep-marker');
    const bepText = document.getElementById('aggregated-break-even-text');
    const targetRevenueText = document.getElementById('aggregated-target-revenue-text');
    
    // 총 매출 프로그래스바
    if (revenueBar && revenueText) {
        if (totalTargetRevenue > 0) {
            const rate = Math.min(100, (totalRevenue / totalTargetRevenue) * 100);
            revenueBar.style.width = rate + '%';
        } else {
            revenueBar.style.width = '0%';
        }
        revenueText.textContent = formatNumber(Math.round(totalRevenue)) + '원';
    }
    
    // 목표 매출 텍스트
    if (targetRevenueText) {
        if (totalTargetRevenue > 0) {
            targetRevenueText.textContent = formatNumber(Math.round(totalTargetRevenue)) + '원';
        } else {
            targetRevenueText.textContent = '목표 미설정';
        }
    }
    
    // 손익분기점 마커
    if (bepMarker && bepText) {
        if (totalTargetRevenue > 0 && totalBreakEvenPoint > 0) {
            const bepRate = Math.min(100, (totalBreakEvenPoint / totalTargetRevenue) * 100);
            bepMarker.style.left = bepRate + '%';
            bepMarker.classList.remove('hidden');
            bepText.textContent = formatNumber(Math.round(totalBreakEvenPoint)) + '원';
        } else {
            bepMarker.classList.add('hidden');
            bepText.textContent = '-';
        }
    }
    
    // 오늘 판매 매수
    const todayTicketsEl = document.getElementById('aggregated-today-tickets');
    if (todayTicketsEl) {
        const todayTickets = data.today_ticket_count || 0;
        todayTicketsEl.innerHTML = '<span class="text-black">' + formatNumber(todayTickets) + '</span>매';
    }
    
    // 판매 매수 프로그래스바 계산
    const totalTickets = data.total_ticket_count || 0;
    const totalSeats = data.total_seats || 0;
    
    const ticketsBar = document.getElementById('aggregated-tickets-progress-bar');
    const ticketsText = document.getElementById('aggregated-total-tickets-text');
    const seatsText = document.getElementById('aggregated-total-seats-text');
    
    // 총 판매 매수 프로그래스바
    if (ticketsBar && ticketsText) {
        if (totalSeats > 0) {
            const ticketsRate = Math.min(100, (totalTickets / totalSeats) * 100);
            ticketsBar.style.width = ticketsRate + '%';
        } else {
            ticketsBar.style.width = '0%';
        }
        ticketsText.textContent = formatNumber(totalTickets) + '매';
    }
    
    // 총 오픈 판매 매수 텍스트
    if (seatsText) {
        if (totalSeats > 0) {
            seatsText.textContent = formatNumber(totalSeats) + '매';
        } else {
            seatsText.textContent = '-';
        }
    }
    
    // 개별 콘서트 리스트 테이블 렌더링
    renderConcertList(data.concert_list || []);
}

/**
 * 개별 콘서트 리스트 테이블 렌더링
 */
function renderConcertList(concertList) {
    const tbody = document.getElementById('concert-list-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (concertList.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-gray-600">콘서트 데이터가 없습니다</td></tr>';
        return;
    }
    
    concertList.forEach(concert => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const title = concert.title || '-';
        const totalRevenue = concert.total_revenue || 0;
        const targetRevenue = concert.target_revenue || 0;
        const achievementRate = concert.achievement_rate || 0;
        
        // 프로그래스 바 너비 계산
        const progressWidth = targetRevenue > 0 ? Math.min(100, achievementRate) : 0;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${title}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(Math.round(totalRevenue))}원</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${targetRevenue > 0 ? formatNumber(Math.round(targetRevenue)) + '원' : '-'}</span>
            </td>
            <td class="px-6 py-4">
                <div class="flex flex-col gap-1">
                    <div class="text-xs font-semibold text-gray-700">
                        ${targetRevenue > 0 ? achievementRate.toFixed(1) + '%' : '-'}
                    </div>
                    <div class="relative w-full h-3 bg-gray-100 rounded-full overflow-hidden">
                        <div
                            class="h-full bg-primary rounded-full transition-all duration-500"
                            style="width: ${progressWidth}%;"
                        ></div>
                    </div>
                </div>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 기간별 매출 데이터 로드
 */
async function loadPeriodRevenueData() {
    if (!periodRevenueUrl) {
        console.error('기간별 매출 데이터 URL이 설정되지 않았습니다.');
        return;
    }
    
    const periodType = document.querySelector('input[name="period-type"]:checked')?.value || 'monthly';
    const startDate = document.getElementById('period-start-date')?.value;
    const endDate = document.getElementById('period-end-date')?.value;
    
    if (!startDate || !endDate) {
        console.error('시작일 또는 종료일이 설정되지 않았습니다.');
        return;
    }
    
    try {
        const url = `${periodRevenueUrl}?period_type=${periodType}&start_date=${startDate}&end_date=${endDate}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('데이터를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentPeriodData = data.data;
            renderPeriodRevenueChart();
        } else {
            console.error('데이터 로드 실패:', data.error);
            alert('데이터를 불러올 수 없습니다: ' + (data.error || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('데이터 로드 오류:', error);
        alert('데이터를 불러오는 중 오류가 발생했습니다.');
    }
}

/**
 * 기간별 매출 차트 렌더링
 */
function renderPeriodRevenueChart() {
    const ctx = document.getElementById('period-revenue-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (periodRevenueChart) {
        periodRevenueChart.destroy();
    }
    
    if (!currentPeriodData || !currentPeriodData.periods || !currentPeriodData.performances) {
        // 데이터가 없을 때 빈 차트 표시
        periodRevenueChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false,
                    },
                },
            },
        });
        return;
    }
    
    const periods = currentPeriodData.periods;
    const performances = currentPeriodData.performances;
    const data = currentPeriodData.data;
    
    // 기간 레이블 포맷팅
    const periodType = document.querySelector('input[name="period-type"]:checked')?.value || 'monthly';
    const labels = periods.map(period => {
        if (periodType === 'daily') {
            const date = new Date(period + 'T00:00:00');
            return (date.getMonth() + 1) + '/' + date.getDate();
        } else if (periodType === 'weekly') {
            // 주 시작일(월요일)을 기준으로 월과 주차 계산
            const weekStartDate = new Date(period + 'T00:00:00');
            const month = weekStartDate.getMonth() + 1;
            
            // 해당 월의 1일
            const firstDayOfMonth = new Date(weekStartDate.getFullYear(), weekStartDate.getMonth(), 1);
            // 1일이 속한 주의 시작일(월요일) 계산
            const firstDayWeekday = firstDayOfMonth.getDay();
            const daysToMonday = firstDayWeekday === 0 ? 6 : firstDayWeekday - 1;
            const firstWeekStart = new Date(firstDayOfMonth);
            firstWeekStart.setDate(firstDayOfMonth.getDate() - daysToMonday);
            
            // 주 시작일과 1일 주 시작일의 차이를 계산하여 주차 구하기
            const diffTime = weekStartDate.getTime() - firstWeekStart.getTime();
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            const weekNumber = Math.floor(diffDays / 7) + 1;
            
            return month + '월 ' + weekNumber + '주';
        } else { // monthly
            return period;
        }
    });
    
    // 데이터셋 생성 (각 공연별로)
    const datasets = performances.map((performance, index) => {
        const performanceId = performance.id.toString();
        const performanceData = periods.map(period => data[period]?.[performanceId] || 0);
        
        // 색상 할당
        const backgroundColor = dynamicColors[index % dynamicColors.length];
        
        return {
            label: performance.title,
            data: performanceData,
            backgroundColor: backgroundColor,
            borderColor: backgroundColor,
            borderWidth: 1,
        };
    });
    
    periodRevenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return label + ': ' + formatNumber(Math.round(value)) + '원';
                        },
                    },
                },
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false,
                    },
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        },
                    },
                    grid: {
                        display: false,
                    },
                },
            },
        },
    });
}

/**
 * 기간 선택 시 날짜 자동 설정
 */
function setDefaultDatesForPeriod() {
    const periodType = document.querySelector('input[name="period-type"]:checked')?.value || 'monthly';
    const startDateInput = document.getElementById('period-start-date');
    const endDateInput = document.getElementById('period-end-date');
    
    if (!startDateInput || !endDateInput) return;
    
    const today = new Date();
    const endDate = new Date(today);
    let startDate = new Date(today);
    
    if (periodType === 'daily') {
        startDate.setDate(startDate.getDate() - 29); // 최근 30일
    } else if (periodType === 'weekly') {
        // 최근 4주 (월요일 기준)
        const daysUntilMonday = today.getDay() === 0 ? 6 : today.getDay() - 1;
        startDate = new Date(today);
        startDate.setDate(startDate.getDate() - daysUntilMonday - 21); // 3주 전 월요일
    } else { // monthly
        // 최근 3개월
        startDate = new Date(today.getFullYear(), today.getMonth() - 2, 1);
    }
    
    startDateInput.value = startDate.toISOString().split('T')[0];
    endDateInput.value = endDate.toISOString().split('T')[0];
}

/**
 * 테이블용 기간 선택 시 날짜 자동 설정
 */
function setDefaultDatesForTablePeriod() {
    const periodType = document.querySelector('input[name="table-period-type"]:checked')?.value || 'monthly';
    const startDateInput = document.getElementById('table-period-start-date');
    const endDateInput = document.getElementById('table-period-end-date');
    
    if (!startDateInput || !endDateInput) return;
    
    const today = new Date();
    const endDate = new Date(today);
    let startDate = new Date(today);
    
    if (periodType === 'daily') {
        startDate.setDate(startDate.getDate() - 29); // 최근 30일
    } else if (periodType === 'weekly') {
        // 최근 4주 (월요일 기준)
        const daysUntilMonday = today.getDay() === 0 ? 6 : today.getDay() - 1;
        startDate = new Date(today);
        startDate.setDate(startDate.getDate() - daysUntilMonday - 21); // 3주 전 월요일
    } else { // monthly
        // 최근 3개월
        startDate = new Date(today.getFullYear(), today.getMonth() - 2, 1);
    }
    
    startDateInput.value = startDate.toISOString().split('T')[0];
    endDateInput.value = endDate.toISOString().split('T')[0];
}

/**
 * 테이블용 기간별 매출 데이터 로드
 */
async function loadPeriodRevenueTableData() {
    if (!periodRevenueUrl) {
        console.error('기간별 매출 데이터 URL이 설정되지 않았습니다.');
        return;
    }
    
    const periodType = document.querySelector('input[name="table-period-type"]:checked')?.value || 'monthly';
    const startDate = document.getElementById('table-period-start-date')?.value;
    const endDate = document.getElementById('table-period-end-date')?.value;
    
    if (!startDate || !endDate) {
        console.error('시작일 또는 종료일이 설정되지 않았습니다.');
        return;
    }
    
    try {
        const url = `${periodRevenueUrl}?period_type=${periodType}&start_date=${startDate}&end_date=${endDate}`;
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('데이터를 불러올 수 없습니다.');
        }
        
        const data = await response.json();
        
        if (data.success) {
            currentTablePeriodData = data.data;
            renderPeriodRevenueTable();
        } else {
            console.error('데이터 로드 실패:', data.error);
            alert('데이터를 불러올 수 없습니다: ' + (data.error || '알 수 없는 오류'));
        }
    } catch (error) {
        console.error('데이터 로드 오류:', error);
        alert('데이터를 불러오는 중 오류가 발생했습니다.');
    }
}

/**
 * 기간별 매출 테이블 렌더링
 */
function renderPeriodRevenueTable() {
    const thead = document.getElementById('table-header-row');
    const tbody = document.getElementById('table-tbody');
    
    if (!thead || !tbody) return;
    
    // 기존 내용 초기화
    tbody.innerHTML = '';
    
    if (!currentTablePeriodData || !currentTablePeriodData.periods || !currentTablePeriodData.performances) {
        tbody.innerHTML = '<tr><td colspan="100%" class="px-6 py-8 text-center text-gray-600">데이터가 없습니다</td></tr>';
        return;
    }
    
    const periods = currentTablePeriodData.periods;
    const performances = currentTablePeriodData.performances;
    const data = currentTablePeriodData.data;
    
    // 테이블 헤더 생성
    const periodType = document.querySelector('input[name="table-period-type"]:checked')?.value || 'monthly';
    
    // 기존 헤더 셀 제거 (날짜 제외)
    const existingHeaderCells = thead.querySelectorAll('th:not(:first-child)');
    existingHeaderCells.forEach(cell => cell.remove());
    
    // 공연명 헤더 추가
    performances.forEach(performance => {
        const th = document.createElement('th');
        th.className = 'px-6 py-4 text-right text-sm font-semibold text-black';
        th.textContent = performance.title;
        thead.appendChild(th);
    });
    
    // 테이블 본문 생성
    periods.forEach(period => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        // 날짜/기간 레이블 생성
        const dateCell = document.createElement('td');
        dateCell.className = 'px-6 py-4 text-sm font-medium text-black sticky left-0 bg-white z-10';
        
        if (periodType === 'daily') {
            const date = new Date(period + 'T00:00:00');
            dateCell.textContent = (date.getMonth() + 1) + '/' + date.getDate();
        } else if (periodType === 'weekly') {
            // 주 시작일(월요일)을 기준으로 월과 주차 계산
            const weekStartDate = new Date(period + 'T00:00:00');
            const month = weekStartDate.getMonth() + 1;
            
            // 해당 월의 1일
            const firstDayOfMonth = new Date(weekStartDate.getFullYear(), weekStartDate.getMonth(), 1);
            // 1일이 속한 주의 시작일(월요일) 계산
            const firstDayWeekday = firstDayOfMonth.getDay();
            const daysToMonday = firstDayWeekday === 0 ? 6 : firstDayWeekday - 1;
            const firstWeekStart = new Date(firstDayOfMonth);
            firstWeekStart.setDate(firstDayOfMonth.getDate() - daysToMonday);
            
            // 주 시작일과 1일 주 시작일의 차이를 계산하여 주차 구하기
            const diffTime = weekStartDate.getTime() - firstWeekStart.getTime();
            const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
            const weekNumber = Math.floor(diffDays / 7) + 1;
            
            dateCell.textContent = month + '월 ' + weekNumber + '주';
        } else { // monthly
            dateCell.textContent = period;
        }
        
        row.appendChild(dateCell);
        
        // 각 공연별 매출 셀 생성
        performances.forEach(performance => {
            const cell = document.createElement('td');
            cell.className = 'px-6 py-4 text-right text-sm text-black';
            
            const performanceId = performance.id.toString();
            const revenue = data[period]?.[performanceId] || 0;
            
            if (revenue > 0) {
                cell.textContent = formatNumber(Math.round(revenue)) + '원';
            } else {
                cell.textContent = '-';
                cell.className = 'px-6 py-4 text-right text-sm text-secondary';
            }
            
            row.appendChild(cell);
        });
        
        tbody.appendChild(row);
    });
}

/**
 * 초기화
 */
document.addEventListener('DOMContentLoaded', function() {
    // 데이터 URL 로드
    const dataScript = document.getElementById('concert-aggregated-data');
    if (dataScript) {
        const data = parseJsonSafely(dataScript.textContent);
        if (data) {
            summaryDataUrl = data.summaryUrl;
            periodRevenueUrl = data.periodRevenueUrl;
        }
    }
    
    // 초기 요약 데이터 로드
    if (summaryDataUrl) {
        loadSummaryData();
    }
    
    // 기간별 매출 그래프 초기화
    if (periodRevenueUrl) {
        // 기본 날짜 설정
        setDefaultDatesForPeriod();
        
        // 초기 데이터 로드
        loadPeriodRevenueData();
        
        // 기간 선택 변경 이벤트
        document.querySelectorAll('input[name="period-type"]').forEach(radio => {
            radio.addEventListener('change', function() {
                setDefaultDatesForPeriod();
                loadPeriodRevenueData();
            });
        });
        
        // 적용 버튼 클릭 이벤트
        const applyBtn = document.getElementById('period-apply-btn');
        if (applyBtn) {
            applyBtn.addEventListener('click', function() {
                loadPeriodRevenueData();
            });
        }
    }
    
    // 기간별 매출 테이블 초기화
    if (periodRevenueUrl) {
        // 기본 날짜 설정
        setDefaultDatesForTablePeriod();
        
        // 초기 데이터 로드
        loadPeriodRevenueTableData();
        
        // 기간 선택 변경 이벤트
        document.querySelectorAll('input[name="table-period-type"]').forEach(radio => {
            radio.addEventListener('change', function() {
                setDefaultDatesForTablePeriod();
                loadPeriodRevenueTableData();
            });
        });
        
        // 적용 버튼 클릭 이벤트
        const tableApplyBtn = document.getElementById('table-period-apply-btn');
        if (tableApplyBtn) {
            tableApplyBtn.addEventListener('click', function() {
                loadPeriodRevenueTableData();
            });
        }
    }
});


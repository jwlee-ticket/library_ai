// 콘서트 대시보드 상세 페이지 JavaScript
// 데이터는 HTML의 <script type="application/json" id="concert-dashboard-data"> 태그에서 로드됩니다.

// 전역 변수
let performanceId = null;
let dataUrl = null;
let revenueChart = null;
let ticketChart = null;
let ageGenderChart = null;
let salesChannelChart = null;
let regionChart = null;
let gradeChart = null;
let currentData = null;

/**
 * CSS 변수에서 색상 가져오기
 */
function getCSSVariable(variableName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(variableName)
        .trim();
}

// 예매처 색상 매핑 (CSS 변수에서 가져옴)
const bookingSiteColors = {
    '놀티켓': getCSSVariable('--color-chart-nolticket'),
    '예스24': getCSSVariable('--color-chart-yes24'),
    '멜론티켓': getCSSVariable('--color-chart-melonticket'),
    '티켓링크': getCSSVariable('--color-chart-ticketlink'),
};

// 동적 색상 팔레트 (CSS 변수에서 가져옴)
const dynamicColors = [
    getCSSVariable('--color-chart-site-5'),
    getCSSVariable('--color-chart-site-6'),
    getCSSVariable('--color-chart-site-7'),
    getCSSVariable('--color-chart-site-8'),
];

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
 * 예매처 색상 가져오기
 */
function getBookingSiteColor(site, index) {
    if (bookingSiteColors[site]) {
        return bookingSiteColors[site];
    }
    // 동적 색상 할당 (4개 이상일 때)
    return dynamicColors[(index - 4) % dynamicColors.length];
}

/**
 * 숫자 포맷팅 (천 단위 콤마)
 */
function formatNumber(num) {
    if (typeof num === 'undefined' || num === null) {
        return '0';
    }
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * 날짜 포맷팅 (YYYY-MM-DD -> MM/DD)
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${month}/${day}`;
}

/**
 * 데이터 로드
 */
async function loadDashboardData(startDate, endDate) {
    if (!dataUrl) {
        console.error('데이터 URL이 설정되지 않았습니다.');
        return;
    }
    
    const url = `${dataUrl}?start_date=${startDate}&end_date=${endDate}`;
    console.log('데이터 로드 시작:', url);
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        
        if (data.success) {
            currentData = data.data;
            updateSummaryCards();
            updateBookingSiteFilters();
            renderCharts();
            renderGradeSales();
            renderGradeChart();
            renderDiscountSales();
            renderAgeGenderChart();
            renderPaymentMethodSales();
            renderCardSales();
            renderSalesChannelSales();
            renderSalesChannelChart();
            renderRegionSales();
            renderRegionChart();
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
function updateSummaryCards() {
    if (!currentData) return;
    
    const yesterdayRevenueEl = document.getElementById('summary-yesterday-revenue');
    const yesterdayTicketsEl = document.getElementById('summary-yesterday-tickets');
    
    // 매출 프로그래스바 계산
    const targetRevenue = currentData.target_revenue || 0;
    const breakEvenPoint = currentData.break_even_point || 0;
    const totalRevenue = currentData.total_revenue || 0;
    
    const revenueBar = document.getElementById('revenue-progress-bar');
    const revenueText = document.getElementById('summary-total-revenue-text');
    const bepMarker = document.getElementById('revenue-bep-marker');
    const bepText = document.getElementById('summary-break-even-text');
    const targetRevenueText = document.querySelector('.target-revenue-value');
    
    // 목표액 텍스트 업데이트 (천 단위 콤마 적용)
    if (targetRevenueText && targetRevenue > 0) {
        targetRevenueText.textContent = formatNumber(Math.round(targetRevenue));
    }
    
    // 총 매출 프로그래스바
    if (revenueBar && revenueText) {
        if (targetRevenue > 0) {
            const rate = Math.min(100, (totalRevenue / targetRevenue) * 100);
            revenueBar.style.width = rate + '%';
            revenueText.textContent = formatNumber(Math.round(totalRevenue)) + '원';
        } else {
            revenueBar.style.width = '0%';
            revenueText.textContent = '-';
        }
    }
    
    // 손익분기점 마커
    if (bepMarker && bepText) {
        if (targetRevenue > 0 && breakEvenPoint > 0) {
            const bepRate = Math.min(100, (breakEvenPoint / targetRevenue) * 100);
            bepMarker.style.left = bepRate + '%';
            bepMarker.classList.remove('hidden');
            bepText.textContent = formatNumber(Math.round(breakEvenPoint)) + '원';
        } else {
            bepMarker.classList.add('hidden');
            bepText.textContent = '-';
        }
    }
    
    // 어제 날짜 계산
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const yesterdayStr = yesterday.toISOString().split('T')[0];
    
    // 어제 매출 계산
    if (yesterdayRevenueEl && currentData.daily_revenue) {
        let yesterdayRevenue = 0;
        const bookingSites = currentData.booking_sites || [];
        
        if (currentData.daily_revenue[yesterdayStr]) {
            bookingSites.forEach(site => {
                if (currentData.daily_revenue[yesterdayStr][site]) {
                    yesterdayRevenue += (currentData.daily_revenue[yesterdayStr][site].paid || 0);
                    yesterdayRevenue += (currentData.daily_revenue[yesterdayStr][site].unpaid || 0);
                }
            });
        }
        
        if (yesterdayRevenue > 0) {
            yesterdayRevenueEl.innerHTML = '<span class="text-black">' + formatNumber(Math.round(yesterdayRevenue)) + '</span>원';
        } else {
            yesterdayRevenueEl.innerHTML = '<span class="text-gray-400">-</span>';
        }
    }
    
    // 총 판매 매수 계산
    let totalTickets = 0;
    if (currentData.daily_tickets) {
        const dates = currentData.dates;
        const bookingSites = currentData.booking_sites;
        
        dates.forEach(date => {
            bookingSites.forEach(site => {
                if (currentData.daily_tickets[date] && currentData.daily_tickets[date][site]) {
                    totalTickets += (currentData.daily_tickets[date][site].paid || 0);
                    totalTickets += (currentData.daily_tickets[date][site].unpaid || 0);
                }
            });
        });
    }
    
    // 판매 매수 프로그래스바 계산
    const totalSeats = currentData.total_seats || 0;
    const ticketsBar = document.getElementById('tickets-progress-bar');
    const ticketsText = document.getElementById('summary-total-tickets-text');
    const seatsText = document.getElementById('summary-total-seats-text');
    
    if (ticketsBar && ticketsText) {
        if (totalSeats > 0) {
            const ticketsRate = Math.min(100, (totalTickets / totalSeats) * 100);
            ticketsBar.style.width = ticketsRate + '%';
            ticketsText.textContent = formatNumber(totalTickets) + '매';
        } else {
            ticketsBar.style.width = '0%';
            ticketsText.textContent = '-';
        }
    }
    
    if (seatsText) {
        if (totalSeats > 0) {
            seatsText.textContent = formatNumber(totalSeats) + '매';
        } else {
            seatsText.textContent = '-';
        }
    }
    
    // 어제 판매 매수 계산
    if (yesterdayTicketsEl && currentData.daily_tickets) {
        let yesterdayTickets = 0;
        const bookingSites = currentData.booking_sites || [];
        
        if (currentData.daily_tickets[yesterdayStr]) {
            bookingSites.forEach(site => {
                if (currentData.daily_tickets[yesterdayStr][site]) {
                    yesterdayTickets += (currentData.daily_tickets[yesterdayStr][site].paid || 0);
                    yesterdayTickets += (currentData.daily_tickets[yesterdayStr][site].unpaid || 0);
                }
            });
        }
        
        if (yesterdayTickets > 0) {
            yesterdayTicketsEl.innerHTML = '<span class="text-black">' + formatNumber(yesterdayTickets) + '</span>매';
        } else {
            yesterdayTicketsEl.innerHTML = '<span class="text-gray-400">-</span>';
        }
    }
}

/**
 * 예매처 필터 체크박스 생성
 */
function updateBookingSiteFilters() {
    if (!currentData || !currentData.booking_sites) return;
    
    const container = document.getElementById('filter-booking-sites');
    if (!container) return;
    
    container.innerHTML = '';
    
    currentData.booking_sites.forEach((site, index) => {
        const label = document.createElement('label');
        label.className = 'flex items-center gap-2 cursor-pointer';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `filter-site-${index}`;
        checkbox.dataset.site = site;
        checkbox.checked = true;
        checkbox.className = 'w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary-200 focus:ring-2';
        
        const span = document.createElement('span');
        span.className = 'text-sm text-black';
        span.textContent = site;
        
        label.appendChild(checkbox);
        label.appendChild(span);
        container.appendChild(label);
    });
}

/**
 * 차트 렌더링
 */
function renderCharts() {
    if (!currentData) return;
    
    renderRevenueChart();
    renderTicketChart();
}

/**
 * 성별, 연령대별 판매현황 차트 렌더링
 */
function renderAgeGenderChart() {
    const ctx = document.getElementById('age-gender-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (ageGenderChart) {
        ageGenderChart.destroy();
    }
    
    const ageGenderData = currentData?.age_gender_sales || [];
    
    // 연령대별로 정렬
    let sortedData = [];
    if (ageGenderData.length > 0) {
        sortedData = [...ageGenderData].sort((a, b) => {
            const aNum = parseInt(a.age_group.split('~')[0].trim()) || 0;
            const bNum = parseInt(b.age_group.split('~')[0].trim()) || 0;
            return aNum - bNum;
        });
    }
    
    const ageGroups = sortedData.length > 0 ? sortedData.map(item => item.age_group) : [];
    const maleCounts = sortedData.length > 0 ? sortedData.map(item => item.male_count || 0) : [];
    const femaleCounts = sortedData.length > 0 ? sortedData.map(item => item.female_count || 0) : [];
    const unknownCounts = sortedData.length > 0 ? sortedData.map(item => item.unknown_count || 0) : [];
    
    ageGenderChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ageGroups,
            datasets: [
                {
                    label: '남성',
                    data: maleCounts,
                    backgroundColor: '#3b82f6', // 파란색
                    borderColor: '#3b82f6',
                    borderWidth: 1,
                },
                {
                    label: '여성',
                    data: femaleCounts,
                    backgroundColor: '#ec4899', // 핑크색
                    borderColor: '#ec4899',
                    borderWidth: 1,
                },
                {
                    label: '성별모름',
                    data: unknownCounts,
                    backgroundColor: '#78716c', // Secondary 컬러
                    borderColor: '#78716c',
                    borderWidth: 1,
                },
            ],
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
                            return label + ': ' + formatNumber(value) + '명';
                        },
                    },
                },
            },
            scales: {
                y: {
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
                x: {
                    grid: {
                        display: false,
                    },
                },
            },
        },
    });
}

/**
 * 매출 차트 렌더링
 */
function renderRevenueChart() {
    const ctx = document.getElementById('revenue-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (revenueChart) {
        revenueChart.destroy();
    }
    
    const dates = currentData.dates;
    const bookingSites = currentData.booking_sites;
    const dailyRevenue = currentData.daily_revenue;
    
    // 선택된 예매처와 입금 상태 확인
    const selectedSites = getSelectedBookingSites();
    const showPaid = document.getElementById('filter-paid')?.checked || false;
    const showUnpaid = document.getElementById('filter-unpaid')?.checked || false;
    
    // 데이터셋 생성 (예매처별로 그룹화)
    const datasets = [];
    
    selectedSites.forEach((site, siteIndex) => {
        const siteColor = getBookingSiteColor(site, siteIndex);
        
        // 입금 데이터셋 (막대 차트)
        if (showPaid) {
            datasets.push({
                type: 'bar',
                label: `${site} (입금)`,
                data: dates.map(date => dailyRevenue[date]?.[site]?.paid || 0),
                backgroundColor: siteColor,
                borderColor: siteColor,
                borderWidth: 1,
                order: 2, // 막대 차트는 아래에 그리기
            });
        }
        
        // 미입금 데이터셋 (막대 차트)
        if (showUnpaid) {
            datasets.push({
                type: 'bar',
                label: `${site} (미입금)`,
                data: dates.map(date => dailyRevenue[date]?.[site]?.unpaid || 0),
                backgroundColor: siteColor + '99', // 60% 투명도
                borderColor: siteColor + '99',
                borderWidth: 1,
                order: 2, // 막대 차트는 아래에 그리기
            });
        }
    });
    
    revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates.map(formatDate),
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
                y: {
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
                x: {
                    grid: {
                        display: false,
                    },
                },
            },
        },
    });
}

/**
 * 판매 매수 차트 렌더링
 */
function renderTicketChart() {
    const ctx = document.getElementById('ticket-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (ticketChart) {
        ticketChart.destroy();
    }
    
    const dates = currentData.dates;
    const bookingSites = currentData.booking_sites;
    const dailyTickets = currentData.daily_tickets;
    
    // 선택된 예매처와 입금 상태 확인
    const selectedSites = getSelectedBookingSites();
    const showPaid = document.getElementById('filter-paid')?.checked || false;
    const showUnpaid = document.getElementById('filter-unpaid')?.checked || false;
    
    // 데이터셋 생성 (예매처별로 그룹화)
    const datasets = [];
    
    selectedSites.forEach((site, siteIndex) => {
        const siteColor = getBookingSiteColor(site, siteIndex);
        
        // 입금 데이터셋 (막대 차트)
        if (showPaid) {
            datasets.push({
                type: 'bar',
                label: `${site} (입금)`,
                data: dates.map(date => dailyTickets[date]?.[site]?.paid || 0),
                backgroundColor: siteColor,
                borderColor: siteColor,
                borderWidth: 1,
                order: 2, // 막대 차트는 아래에 그리기
            });
        }
        
        // 미입금 데이터셋 (막대 차트)
        if (showUnpaid) {
            datasets.push({
                type: 'bar',
                label: `${site} (미입금)`,
                data: dates.map(date => dailyTickets[date]?.[site]?.unpaid || 0),
                backgroundColor: siteColor + '99', // 60% 투명도
                borderColor: siteColor + '99',
                borderWidth: 1,
                order: 2, // 막대 차트는 아래에 그리기
            });
        }
    });
    
    ticketChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates.map(formatDate),
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
                            return label + ': ' + formatNumber(value) + '매';
                        },
                    },
                },
            },
            scales: {
                y: {
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
                x: {
                    grid: {
                        display: false,
                    },
                },
            },
        },
    });
}

/**
 * 선택된 예매처 목록 가져오기
 */
function getSelectedBookingSites() {
    const checkboxes = document.querySelectorAll('#filter-booking-sites input[type="checkbox"]:checked');
    return Array.from(checkboxes).map(cb => cb.dataset.site);
}

/**
 * 등급별 판매현황 렌더링
 */
function renderGradeSales() {
    if (!currentData || !currentData.grade_sales) return;
    
    const tbody = document.getElementById('grade-sales-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const gradeSales = currentData.grade_sales;
    const grades = Object.keys(gradeSales).sort();
    
    if (grades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-600">등급별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    grades.forEach(grade => {
        const data = gradeSales[grade];
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const paidCount = data.paid_count || 0;
        const freeCount = data.free_count || 0;
        const revenue = data.revenue || 0;
        const paidOccupancyRate = (data.paid_occupancy_rate || 0) * 100;
        const totalOccupancyRate = (data.total_occupancy_rate || 0) * 100;
        const totalCount = data.total_count || 0;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${grade}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(paidCount)}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(freeCount)}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(Math.round(revenue))}원</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${paidOccupancyRate.toFixed(1)}%</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${totalOccupancyRate.toFixed(1)}%</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(totalCount)}</span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 등급별 판매현황 파이 차트 렌더링
 */
function renderGradeChart() {
    const ctx = document.getElementById('grade-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (gradeChart) {
        gradeChart.destroy();
    }
    
    if (!currentData || !currentData.grade_sales) {
        // 데이터가 없을 때 빈 차트 표시
        gradeChart = new Chart(ctx, {
            type: 'pie',
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
                    tooltip: {
                        enabled: false,
                    },
                },
            },
        });
        return;
    }
    
    const gradeSales = currentData.grade_sales;
    const grades = Object.keys(gradeSales).sort();
    
    if (grades.length === 0) {
        // 데이터가 없을 때 빈 차트 표시
        gradeChart = new Chart(ctx, {
            type: 'pie',
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
                    tooltip: {
                        enabled: false,
                    },
                },
            },
        });
        return;
    }
    
    const labels = grades;
    const paidCounts = grades.map(grade => gradeSales[grade].paid_count || 0);
    
    // 총 매수(유료) 계산
    const totalPaidCount = paidCounts.reduce((sum, count) => sum + count, 0);
    
    // 색상 생성 (동적 색상 팔레트 사용)
    const backgroundColors = grades.map((_, index) => {
        return dynamicColors[index % dynamicColors.length];
    });
    
    gradeChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '매수(유료)',
                    data: paidCounts,
                    backgroundColor: backgroundColors,
                    borderColor: '#ffffff',
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                        },
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = totalPaidCount > 0 ? ((value / totalPaidCount) * 100).toFixed(1) : 0;
                            return label + ': ' + formatNumber(value) + '매 (' + percentage + '%)';
                        },
                    },
                },
            },
        },
    });
}

/**
 * 할인권종별 판매현황 렌더링
 */
function renderDiscountSales() {
    if (!currentData || !currentData.discount_sales) return;
    
    const tbody = document.getElementById('discount-sales-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const discountSales = currentData.discount_sales;
    const sites = Object.keys(discountSales).sort();
    
    if (sites.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-gray-600">할인권종별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    sites.forEach(site => {
        const discounts = discountSales[site];
        if (!discounts || discounts.length === 0) return;
        
        discounts.forEach(discount => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            
            const discountType = discount.discount_type || '-';
            const salesCount = discount.sales_count || 0;
            const revenue = discount.revenue || 0;
            
            row.innerHTML = `
                <td class="px-6 py-4">
                    <span class="text-base font-medium text-black">${site}</span>
                </td>
                <td class="px-6 py-4">
                    <span class="text-sm text-black">${discountType}</span>
                </td>
                <td class="px-6 py-4 text-right">
                    <span class="text-sm text-black">${formatNumber(salesCount)}</span>
                </td>
                <td class="px-6 py-4 text-right">
                    <span class="text-sm text-black">${formatNumber(Math.round(revenue))}원</span>
                </td>
            `;
            
            tbody.appendChild(row);
        });
    });
}

/**
 * 결제수단별 판매현황 렌더링
 */
function renderPaymentMethodSales() {
    if (!currentData || !currentData.payment_method_sales) return;
    
    const tbody = document.getElementById('payment-method-sales-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const paymentMethodSales = currentData.payment_method_sales;
    const paymentMethods = Object.keys(paymentMethodSales).sort();
    
    if (paymentMethods.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-600">결제수단별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    paymentMethods.forEach(paymentMethod => {
        const data = paymentMethodSales[paymentMethod];
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const count = data.count || 0;
        const amount = data.amount || 0;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${paymentMethod}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(count)}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(Math.round(amount))}원</span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 카드별 매출집계 렌더링
 */
function renderCardSales() {
    if (!currentData || !currentData.card_sales) return;
    
    const tbody = document.getElementById('card-sales-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const cardSales = currentData.card_sales;
    const cardTypes = Object.keys(cardSales).sort();
    
    if (cardTypes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-600">카드별 매출 데이터가 없습니다</td></tr>';
        return;
    }
    
    cardTypes.forEach(cardType => {
        const data = cardSales[cardType];
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const count = data.count || 0;
        const amount = data.amount || 0;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${cardType}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(count)}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(Math.round(amount))}원</span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 판매경로별 판매현황 테이블 렌더링
 */
function renderSalesChannelSales() {
    if (!currentData || !currentData.sales_channel_sales) return;
    
    const tbody = document.getElementById('sales-channel-sales-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const salesChannelSales = currentData.sales_channel_sales;
    const salesChannels = Object.keys(salesChannelSales).sort();
    
    if (salesChannels.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-600">판매경로별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    salesChannels.forEach(salesChannel => {
        const data = salesChannelSales[salesChannel];
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const count = data.count || 0;
        const amount = data.amount || 0;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${salesChannel}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(count)}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(Math.round(amount))}원</span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 판매경로별 판매현황 차트 렌더링
 */
function renderSalesChannelChart() {
    const ctx = document.getElementById('sales-channel-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (salesChannelChart) {
        salesChannelChart.destroy();
    }
    
    if (!currentData || !currentData.sales_channel_sales) {
        // 데이터가 없을 때 빈 차트 표시
        salesChannelChart = new Chart(ctx, {
            type: 'pie',
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
                    tooltip: {
                        enabled: false,
                    },
                },
            },
        });
        return;
    }
    
    const salesChannelSales = currentData.sales_channel_sales;
    const salesChannels = Object.keys(salesChannelSales).sort();
    
    if (salesChannels.length === 0) {
        // 데이터가 없을 때 빈 차트 표시
        salesChannelChart = new Chart(ctx, {
            type: 'pie',
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
                    tooltip: {
                        enabled: false,
                    },
                },
            },
        });
        return;
    }
    
    const labels = salesChannels;
    const counts = salesChannels.map(channel => salesChannelSales[channel].count || 0);
    
    // 총 판매 매수 계산
    const totalCount = counts.reduce((sum, count) => sum + count, 0);
    
    // 색상 생성 (동적 색상 팔레트 사용)
    const backgroundColors = salesChannels.map((_, index) => {
        return dynamicColors[index % dynamicColors.length];
    });
    
    salesChannelChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '판매 매수',
                    data: counts,
                    backgroundColor: backgroundColors,
                    borderColor: '#ffffff',
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                        },
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = totalCount > 0 ? ((value / totalCount) * 100).toFixed(1) : 0;
                            return label + ': ' + formatNumber(value) + '매 (' + percentage + '%)';
                        },
                    },
                },
            },
        },
    });
}

/**
 * 지역별 판매현황 테이블 렌더링
 */
function renderRegionSales() {
    if (!currentData || !currentData.region_sales) return;
    
    const tbody = document.getElementById('region-sales-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    const regionSales = currentData.region_sales;
    const regions = Object.keys(regionSales).sort();
    
    if (regions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="2" class="px-6 py-8 text-center text-gray-600">지역별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    regions.forEach(region => {
        const data = regionSales[region];
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const count = data.count || 0;
        
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${region}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(count)}</span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 지역별 판매현황 차트 렌더링
 */
function renderRegionChart() {
    const ctx = document.getElementById('region-chart');
    if (!ctx) return;
    
    // 기존 차트 제거
    if (regionChart) {
        regionChart.destroy();
    }
    
    if (!currentData || !currentData.region_sales) {
        // 데이터가 없을 때 빈 차트 표시
        regionChart = new Chart(ctx, {
            type: 'pie',
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
                    tooltip: {
                        enabled: false,
                    },
                },
            },
        });
        return;
    }
    
    const regionSales = currentData.region_sales;
    const regions = Object.keys(regionSales).sort();
    
    if (regions.length === 0) {
        // 데이터가 없을 때 빈 차트 표시
        regionChart = new Chart(ctx, {
            type: 'pie',
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
                    tooltip: {
                        enabled: false,
                    },
                },
            },
        });
        return;
    }
    
    const labels = regions;
    const counts = regions.map(region => regionSales[region].count || 0);
    
    // 총 판매 매수 계산
    const totalCount = counts.reduce((sum, count) => sum + count, 0);
    
    // 색상 생성 (동적 색상 팔레트 사용)
    const backgroundColors = regions.map((_, index) => {
        return dynamicColors[index % dynamicColors.length];
    });
    
    regionChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '판매 매수',
                    data: counts,
                    backgroundColor: backgroundColors,
                    borderColor: '#ffffff',
                    borderWidth: 2,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                        },
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = totalCount > 0 ? ((value / totalCount) * 100).toFixed(1) : 0;
                            return label + ': ' + formatNumber(value) + '매 (' + percentage + '%)';
                        },
                    },
                },
            },
        },
    });
}

/**
 * 초기화
 */
document.addEventListener('DOMContentLoaded', function() {
    // 데이터 로드
    const dataScript = document.getElementById('concert-dashboard-data');
    if (dataScript) {
        const data = parseJsonSafely(dataScript.textContent);
        if (data) {
            performanceId = data.performanceId;
            dataUrl = data.dataUrl;
        }
    }
    
    // 기본 날짜 설정 (최근 7일)
    const endDate = new Date();
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - 6);
    
    const startDateInput = document.getElementById('filter-start-date');
    const endDateInput = document.getElementById('filter-end-date');
    
    if (startDateInput) {
        startDateInput.value = startDate.toISOString().split('T')[0];
    }
    if (endDateInput) {
        endDateInput.value = endDate.toISOString().split('T')[0];
    }
    
    // 초기 데이터 로드
    if (startDateInput && endDateInput) {
        loadDashboardData(startDateInput.value, endDateInput.value);
    }
    
    // 필터 적용 버튼
    const applyBtn = document.getElementById('filter-apply-btn');
    if (applyBtn) {
        applyBtn.addEventListener('click', function() {
            if (startDateInput && endDateInput) {
                loadDashboardData(startDateInput.value, endDateInput.value);
            }
        });
    }
    
    // 예매처 필터 변경
    document.addEventListener('change', function(e) {
        if (e.target.matches('#filter-booking-sites input[type="checkbox"]')) {
            renderCharts();
        }
    });
    
    // 입금/미입금 필터 변경
    const paidFilter = document.getElementById('filter-paid');
    const unpaidFilter = document.getElementById('filter-unpaid');
    
    if (paidFilter) {
        paidFilter.addEventListener('change', renderCharts);
    }
    if (unpaidFilter) {
        unpaidFilter.addEventListener('change', renderCharts);
    }
});


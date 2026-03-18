// 콘서트 대시보드 상세 페이지 JavaScript
// 데이터는 HTML의 <script type="application/json" id="concert-dashboard-data"> 태그에서 로드됩니다.

// 전역 변수
let performanceId = null;
let dataUrl = null;
let memosUrl = null;
let dailyChart = null;
let ageGenderChart = null;
let salesChannelChart = null;
let regionChart = null;
let gradeChart = null;
let currentData = null;
let chartData = null;
let marketingMemos = {};
const chartYAxisWidth = 84;

/**
 * CSS 변수에서 색상 가져오기
 */
function getCSSVariable(variableName) {
    return getComputedStyle(document.documentElement)
        .getPropertyValue(variableName)
        .trim();
}

// 예매처 색상 매핑 (브랜드 지정 + CSS 변수)
const bookingSiteColors = {
    '라이브러리컴퍼니': '#F65938',
    'Library Company': '#F65938',
    'NOL 티켓': '#4154FF',
    'NOL티켓': '#4154FF',
    '놀티켓': '#4154FF',
    '롯데콘서트홀': '#DB291C',
    '예스24': getCSSVariable('--color-chart-yes24') || '#2A3038',
    '멜론티켓': getCSSVariable('--color-chart-melonticket') || '#16A34A',
    '티켓링크': getCSSVariable('--color-chart-ticketlink') || '#78716C',
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

function toggleVisibilityById(id, visible) {
    const el = document.getElementById(id);
    if (!el) return;
    if (visible) {
        el.classList.remove('hidden');
    } else {
        el.classList.add('hidden');
    }
}

function updateFinalReportSectionsVisibility() {
    if (!currentData) return;
    const visibility = currentData.final_report_visibility || {};

    const hasDiscount = !!visibility.has_discount_sales;
    const hasAgeGender = !!visibility.has_age_gender_sales;
    const hasPayment = !!visibility.has_payment_method_sales;
    const hasCard = !!visibility.has_card_sales;
    const hasSalesChannel = !!visibility.has_sales_channel_sales;
    const hasRegion = !!visibility.has_region_sales;

    toggleVisibilityById('section-discount-sales', hasDiscount);
    toggleVisibilityById('section-age-gender-sales', hasAgeGender);
    toggleVisibilityById('section-sales-channel-sales', hasSalesChannel);
    toggleVisibilityById('section-region-sales', hasRegion);
    toggleVisibilityById('section-payment-method-sales', hasPayment);
    toggleVisibilityById('section-card-sales', hasCard);
    toggleVisibilityById('section-payment-card-grid', hasPayment || hasCard);
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
    
    const query = startDate && endDate ? `?start_date=${startDate}&end_date=${endDate}` : '';
    const url = `${dataUrl}${query}`;
    console.log('데이터 로드 시작:', url);
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        
        if (data.success) {
            const isFiltered = !!(startDate && endDate);
            if (!isFiltered || !currentData) {
                currentData = data.data;
            }
            chartData = data.data;
            if (chartData?.applied_start_date && chartData?.applied_end_date) {
                const startDateInput = document.getElementById('filter-start-date');
                const endDateInput = document.getElementById('filter-end-date');
                if (startDateInput && endDateInput) {
                    startDateInput.value = chartData.applied_start_date;
                    endDateInput.value = chartData.applied_end_date;
                }
            }
            if (!isFiltered) {
                updateSummaryCards();
                updateBookingSiteFilters();
                updateFinalReportSectionsVisibility();
                renderCharts();
                renderBookingSiteSummary();
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
                renderCharts();
            }
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
 * 마케팅 메모 로드
 */
async function loadMarketingMemos() {
    if (!memosUrl) return;
    try {
        const response = await fetch(memosUrl);
        if (!response.ok) return;
        const result = await response.json();
        if (result.success) {
            marketingMemos = result.data?.memos || {};
            if (dailyChart) {
                dailyChart.options.plugins.annotation.annotations = buildMemoAnnotations();
                dailyChart.update();
            }
        }
    } catch (e) {
        console.error('마케팅 메모 로드 실패:', e);
    }
}

/**
 * 마케팅 메모 annotation 객체 생성
 */
function buildMemoAnnotations() {
    const data = chartData || currentData;
    if (!data) return {};
    const annotations = {};
    (data.dates || []).forEach((date) => {
        const memos = marketingMemos[date];
        if (!memos || !memos.length) return;
        const first = memos[0].content;
        const truncated = first.length > 12 ? first.slice(0, 12) + '…' : first;
        const label = memos.length > 1 ? `${truncated} 외 ${memos.length - 1}개` : truncated;
        const formattedDate = formatDate(date);
        annotations[`memo_${date.replace(/-/g, '_')}`] = {
            type: 'line',
            xMin: formattedDate,
            xMax: formattedDate,
            borderColor: 'rgba(220, 38, 38, 0.75)',
            borderWidth: 2,
            borderDash: [4, 4],
            label: {
                display: true,
                content: label,
                position: 'start',
                yAdjust: -8,
                color: '#dc2626',
                backgroundColor: 'rgba(255,255,255,0.9)',
                font: { size: 11, weight: 'normal' },
                padding: { x: 5, y: 3 },
                borderRadius: 3,
            },
            click: function() {
                openMemoModal(date);
            },
        };
    });
    return annotations;
}

/**
 * 요약 카드 업데이트
 */
function updateSummaryCards() {
    if (!currentData) return;
    
    const todayRevenueEl = document.getElementById('summary-today-revenue');
    const todayTicketsEl = document.getElementById('summary-today-tickets');
    const totalRevenueEl = document.getElementById('summary-total-revenue');
    const totalTicketsEl = document.getElementById('summary-total-tickets');
    
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
        } else {
            revenueBar.style.width = '0%';
        }
        revenueText.textContent = formatNumber(Math.round(totalRevenue)) + '원';
    }
    
    if (totalRevenueEl) {
        totalRevenueEl.textContent = formatNumber(Math.round(totalRevenue));
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
    
    const todayStr = new Date().toISOString().split('T')[0];
    
    // 최근 날짜 매출 계산
    if (todayRevenueEl && currentData.daily_revenue) {
        let todayRevenue = 0;
        const bookingSites = currentData.booking_sites || [];
        if (currentData.daily_revenue[todayStr]) {
            bookingSites.forEach(site => {
                if (currentData.daily_revenue[todayStr][site]) {
                    todayRevenue += (currentData.daily_revenue[todayStr][site].paid || 0);
                    todayRevenue += (currentData.daily_revenue[todayStr][site].unpaid || 0);
                }
            });
        }
        if (todayRevenue > 0) {
            todayRevenueEl.innerHTML = '<span class="text-black">' + formatNumber(Math.round(todayRevenue)) + '</span>원';
        } else {
            todayRevenueEl.innerHTML = '<span class="text-secondary">-</span>';
        }
    }
    
    // 총 판매 매수 계산
    let totalTickets = currentData.total_ticket_count || 0;
    if (!totalTickets && currentData.daily_tickets) {
        const dates = currentData.dates || [];
        const bookingSites = currentData.booking_sites || [];
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
        } else {
            ticketsBar.style.width = '0%';
        }
        const openSeatsText = totalSeats > 0 ? formatNumber(totalSeats) + '매' : '-';
        ticketsText.textContent = formatNumber(totalTickets) + '매/' + openSeatsText;
    }
    
    if (totalTicketsEl) {
        totalTicketsEl.textContent = formatNumber(totalTickets);
    }
    
    if (seatsText) {
        if (totalSeats > 0) {
            seatsText.textContent = formatNumber(totalSeats) + '매';
        } else {
            seatsText.textContent = '-';
        }
    }
    
    // 최근 날짜 판매 매수 계산
    if (todayTicketsEl && currentData.daily_tickets) {
        let todayTickets = 0;
        const bookingSites = currentData.booking_sites || [];
        if (currentData.daily_tickets[todayStr]) {
            bookingSites.forEach(site => {
                if (currentData.daily_tickets[todayStr][site]) {
                    todayTickets += (currentData.daily_tickets[todayStr][site].paid || 0);
                    todayTickets += (currentData.daily_tickets[todayStr][site].unpaid || 0);
                }
            });
        }
        if (todayTickets > 0) {
            todayTicketsEl.innerHTML = '<span class="text-black">' + formatNumber(todayTickets) + '</span>매';
        } else {
            todayTicketsEl.innerHTML = '<span class="text-secondary">-</span>';
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
        label.className = 'flex items-center gap-2 cursor-pointer hover:text-primary transition-colors duration-200';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `filter-site-${index}`;
        checkbox.dataset.site = site;
        checkbox.checked = true;
        checkbox.className = 'checkbox checkbox-primary checkbox-sm';
        
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
    if (!chartData) return;

    renderDailyChart();
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
                    afterFit: function(scale) {
                        scale.width = chartYAxisWidth;
                    },
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
function renderDailyChart() {
    const ctx = document.getElementById('daily-chart');
    if (!ctx) return;

    if (dailyChart) {
        dailyChart.destroy();
    }

    const data = chartData || currentData;
    if (!data) return;
    const dates = data.dates;
    const dailyRevenue = data.daily_revenue;
    const dailyTickets = data.daily_tickets;
    const selectedSites = getSelectedBookingSites();
    const paidCheckbox = document.getElementById('filter-paid');
    const showPaid = paidCheckbox ? paidCheckbox.checked : true;

    const revenueTotals = dates.map(date => {
        let total = 0;
        selectedSites.forEach(site => {
            total += dailyRevenue[date]?.[site]?.paid || 0;
            if (!showPaid) {
                total += dailyRevenue[date]?.[site]?.unpaid || 0;
            }
        });
        return total;
    });

    const ticketTotals = dates.map(date => {
        let total = 0;
        selectedSites.forEach(site => {
            total += dailyTickets[date]?.[site]?.paid || 0;
            if (!showPaid) {
                total += dailyTickets[date]?.[site]?.unpaid || 0;
            }
        });
        return total;
    });
    const revenueMax = Math.max(1, ...revenueTotals);
    const ticketMax = Math.max(1, ...ticketTotals);

    dailyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: dates.map(formatDate),
            datasets: [
                {
                    type: 'bar',
                    label: '매출',
                    data: revenueTotals,
                    yAxisID: 'yRevenue',
                    backgroundColor: '#6366f1',
                    borderColor: '#4f46e5',
                    borderWidth: 1,
                    borderRadius: 4,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: false,
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const revenue = context.parsed.y || 0;
                            const idx = context.dataIndex;
                            const tickets = ticketTotals[idx] || 0;
                            const date = dates[idx];
                            const memos = marketingMemos[date] || [];
                            const lines = [
                                '매출: ' + formatNumber(Math.round(revenue)) + '원',
                                '판매 매수: ' + formatNumber(Math.round(tickets)) + '매',
                            ];
                            if (memos.length) {
                                lines.push('');
                                memos.forEach(m => lines.push('📌 ' + m.content));
                            }
                            return lines;
                        },
                    },
                },
                annotation: {
                    annotations: buildMemoAnnotations(),
                },
            },
            scales: {
                yRevenue: {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    suggestedMax: revenueMax,
                    afterFit: function(scale) {
                        scale.width = chartYAxisWidth;
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(Math.round(value));
                        },
                    },
                    grid: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: '매출 (원)',
                    },
                },
                yTickets: {
                    type: 'linear',
                    position: 'right',
                    display: true,
                    beginAtZero: true,
                    suggestedMax: ticketMax,
                    afterFit: function(scale) {
                        scale.width = chartYAxisWidth;
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(Math.round(value));
                        },
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    title: {
                        display: true,
                        text: '판매 매수',
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
    if (!checkboxes.length) {
        return currentData?.booking_sites || [];
    }
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
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-600">등급별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    grades.forEach(grade => {
        const data = gradeSales[grade];
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const paidCount = data.paid_count || 0;
        const freeCount = data.free_count || 0;
        const paidOccupancyRate = (data.paid_occupancy_rate || 0) * 100;
        const totalOccupancyRate = (data.total_occupancy_rate || 0) * 100;
        const totalCount = data.total_count || 0;
        const seatCount = data.seat_count || 0;
        const openSeatText = seatCount > 0 ? formatNumber(seatCount) : '-';
        
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
                <span class="text-sm text-black">${paidOccupancyRate.toFixed(1)}%</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${totalOccupancyRate.toFixed(1)}%</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(totalCount)}/${openSeatText}</span>
            </td>
        `;
        
        tbody.appendChild(row);
    });
}

/**
 * 예매처별 요약 테이블 렌더링
 */
function renderBookingSiteSummary() {
    const tbody = document.getElementById('booking-site-tbody');
    if (!tbody || !currentData) return;

    const summaryRows = currentData.booking_site_summary_all_time || [];
    if (summaryRows.length === 0) {
        // Fallback for older API responses
        const fallbackSummary = {};
        const dates = currentData.dates || [];
        const bookingSites = currentData.booking_sites || [];
        const dailyRevenue = currentData.daily_revenue || {};
        const dailyTickets = currentData.daily_tickets || {};
        bookingSites.forEach(site => {
            fallbackSummary[site] = { revenue: 0, tickets: 0 };
            dates.forEach(date => {
                const revenueBySite = dailyRevenue[date]?.[site];
                const ticketsBySite = dailyTickets[date]?.[site];
                if (revenueBySite) {
                    fallbackSummary[site].revenue += revenueBySite.paid || 0;
                }
                if (ticketsBySite) {
                    fallbackSummary[site].tickets += ticketsBySite.paid || 0;
                }
            });
        });
        const fallbackSites = Object.keys(fallbackSummary).sort();
        if (!fallbackSites.length) {
            tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-600">예매처별 데이터가 없습니다</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        fallbackSites.forEach(site => {
            const row = document.createElement('tr');
            row.className = 'hover:bg-gray-50 transition-colors';
            row.innerHTML = `
                <td class="px-6 py-4">
                    <span class="text-base font-medium text-black">${site}</span>
                </td>
                <td class="px-6 py-4 text-right">
                    <span class="text-sm text-black">${formatNumber(Math.round(fallbackSummary[site].revenue))}원</span>
                </td>
                <td class="px-6 py-4 text-right">
                    <span class="text-sm text-black">${formatNumber(fallbackSummary[site].tickets)}매</span>
                </td>
            `;
            tbody.appendChild(row);
        });
        return;
    }

    if (!summaryRows.length) {
        tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-600">예매처별 데이터가 없습니다</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    summaryRows.forEach(item => {
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        const site = item.site || '-';
        const revenue = item.revenue || 0;
        const tickets = item.tickets || 0;
        row.innerHTML = `
            <td class="px-6 py-4">
                <span class="text-base font-medium text-black">${site}</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(Math.round(revenue))}원</span>
            </td>
            <td class="px-6 py-4 text-right">
                <span class="text-sm text-black">${formatNumber(tickets)}매</span>
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
    const salesChannelRows = Array.isArray(salesChannelSales)
        ? salesChannelSales
        : Object.keys(salesChannelSales || {}).sort().map(channel => ({
            sales_channel: channel,
            count: salesChannelSales[channel]?.count || 0,
            amount: salesChannelSales[channel]?.amount || 0
        }));
    
    if (salesChannelRows.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="px-6 py-8 text-center text-gray-600">판매경로별 판매 데이터가 없습니다</td></tr>';
        return;
    }
    
    salesChannelRows.forEach(item => {
        const salesChannel = item.sales_channel || '-';
        const row = document.createElement('tr');
        row.className = 'hover:bg-gray-50 transition-colors';
        
        const count = item.count || 0;
        const amount = item.amount || 0;
        
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
    const salesChannelRows = Array.isArray(salesChannelSales)
        ? salesChannelSales
        : Object.keys(salesChannelSales || {}).sort().map(channel => ({
            sales_channel: channel,
            count: salesChannelSales[channel]?.count || 0,
            amount: salesChannelSales[channel]?.amount || 0
        }));
    
    if (salesChannelRows.length === 0) {
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
    
    const labels = salesChannelRows.map(item => item.sales_channel || '-');
    const counts = salesChannelRows.map(item => item.count || 0);
    
    // 총 판매 매수 계산
    const totalCount = counts.reduce((sum, count) => sum + count, 0);
    
    // 색상 생성 (동적 색상 팔레트 사용)
    const backgroundColors = salesChannelRows.map((_, index) => {
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
    if (!currentData || !currentData.region_sales_groups) return;

    const container = document.getElementById('region-sales-container');
    if (!container) return;

    container.innerHTML = '';

    const regionGroups = currentData.region_sales_groups || [];
    if (!regionGroups.length) {
        const empty = document.createElement('div');
        empty.className = 'rounded-lg border border-gray-100 bg-gray-50 p-6 text-sm text-gray-600';
        empty.textContent = '지역별 판매 데이터가 없습니다';
        container.appendChild(empty);
        return;
    }

    regionGroups.forEach((group, index) => {
        const title = group.title || '지역별';
        const rows = group.rows || [];
        const card = document.createElement('div');
        card.className = 'rounded-xl border border-gray-200 shadow-sm bg-white p-4';
        card.innerHTML = `
            <div class="text-sm font-semibold text-black mb-3">${title}</div>
            <div class="relative mb-4" style="height: 240px;">
                <canvas id="region-chart-${index}"></canvas>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead class="bg-surface border-b border-gray-200">
                        <tr>
                            <th class="px-4 py-2 text-left text-sm font-semibold text-black">지역</th>
                            <th class="px-4 py-2 text-right text-sm font-semibold text-black">판매 매수</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-100"></tbody>
                </table>
            </div>
        `;

        const tbody = card.querySelector('tbody');
        if (!rows.length) {
            const row = document.createElement('tr');
            row.innerHTML = '<td colspan="2" class="px-4 py-4 text-center text-sm text-gray-600">데이터가 없습니다</td>';
            tbody.appendChild(row);
        } else {
            rows.forEach(item => {
                const row = document.createElement('tr');
                row.className = 'hover:bg-gray-50 transition-colors';
                const count = item.count || 0;
                row.innerHTML = `
                    <td class="px-4 py-2">
                        <span class="text-sm text-black">${item.region || '-'}</span>
                    </td>
                    <td class="px-4 py-2 text-right">
                        <span class="text-sm text-black">${formatNumber(count)}</span>
                    </td>
                `;
                tbody.appendChild(row);
            });
        }

        container.appendChild(card);

        const canvas = card.querySelector(`#region-chart-${index}`);
        if (canvas) {
            const labels = rows.map(item => item.region || '-');
            const counts = rows.map(item => item.count || 0);
            const totalCount = counts.reduce((sum, count) => sum + count, 0);
            const backgroundColors = labels.map((_, idx) => dynamicColors[idx % dynamicColors.length]);

            new Chart(canvas, {
                type: 'pie',
                data: {
                    labels,
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
                                padding: 10,
                                font: {
                                    size: 11,
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
    });
}

/**
 * 지역별 판매현황 차트 렌더링
 */
function renderRegionChart() {
    return;
}

/**
 * 마케팅 메모 모달 열기/닫기
 */
function openMemoModal(date) {
    const modal = document.getElementById('memo-modal');
    const backdrop = document.getElementById('memo-backdrop');
    if (!modal) return;
    const dateInput = document.getElementById('memo-date-input');
    if (dateInput) dateInput.value = date || '';
    renderMemoList(date);
    modal.classList.remove('hidden');
    if (backdrop) backdrop.classList.remove('hidden');
}

function closeMemoModal() {
    const modal = document.getElementById('memo-modal');
    const backdrop = document.getElementById('memo-backdrop');
    if (modal) modal.classList.add('hidden');
    if (backdrop) backdrop.classList.add('hidden');
}

/**
 * 특정 날짜의 메모 목록을 모달 내에 렌더링
 */
function renderMemoList(date) {
    const wrapper = document.getElementById('memo-list-wrapper');
    const container = document.getElementById('memo-list-container');
    if (!container || !wrapper) return;
    const rawMemos = (date && marketingMemos[date]) ? marketingMemos[date] : [];
    if (!rawMemos.length) {
        wrapper.style.display = 'none';
        container.innerHTML = '';
        return;
    }
    wrapper.style.display = '';

    // 최신순 정렬 (created_at 내림차순)
    const memos = [...rawMemos].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    container.innerHTML = '';
    memos.forEach(m => {
        const row = document.createElement('div');
        row.className = 'py-3 border-b border-gray-100';
        row.dataset.memoId = m.id;

        // 보기 영역
        const viewArea = document.createElement('div');
        viewArea.className = 'flex items-start justify-between gap-2';

        const textEl = document.createElement('p');
        textEl.className = 'text-sm text-black break-words flex-1';
        textEl.textContent = m.content;

        const btnGroup = document.createElement('div');
        btnGroup.className = 'flex gap-1 flex-shrink-0';

        const editBtn = document.createElement('button');
        editBtn.type = 'button';
        editBtn.title = '수정';
        editBtn.className = 'p-1 text-gray-400 hover:text-black transition-colors';
        editBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>`;

        const deleteBtn = document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.title = '삭제';
        deleteBtn.className = 'p-1 text-gray-400 hover:text-red-500 transition-colors';
        deleteBtn.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>`;

        btnGroup.appendChild(editBtn);
        btnGroup.appendChild(deleteBtn);
        viewArea.appendChild(textEl);
        viewArea.appendChild(btnGroup);

        // 편집 영역
        const editArea = document.createElement('div');
        editArea.style.display = 'none';
        editArea.className = 'mt-2';

        const textarea = document.createElement('textarea');
        textarea.className = 'w-full border border-gray-300 rounded-lg p-2 text-sm resize-none focus:outline-none focus:border-gray-500';
        textarea.rows = 2;
        textarea.value = m.content;

        const editBtnRow = document.createElement('div');
        editBtnRow.className = 'flex justify-end gap-2 mt-2';

        const cancelBtn = document.createElement('button');
        cancelBtn.type = 'button';
        cancelBtn.textContent = '취소';
        cancelBtn.className = 'px-3 py-1 text-sm text-gray-600 hover:text-black transition-colors';

        const saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.textContent = '저장';
        saveBtn.className = 'px-3 py-1 text-sm bg-primary text-white rounded-lg hover:opacity-90 transition-opacity';

        editBtnRow.appendChild(cancelBtn);
        editBtnRow.appendChild(saveBtn);
        editArea.appendChild(textarea);
        editArea.appendChild(editBtnRow);

        // 작성일
        const metaEl = document.createElement('p');
        metaEl.className = 'text-xs text-gray-400 mt-1';
        metaEl.textContent = m.created_at;

        row.appendChild(viewArea);
        row.appendChild(editArea);
        row.appendChild(metaEl);
        container.appendChild(row);

        // 이벤트
        editBtn.addEventListener('click', () => {
            viewArea.style.display = 'none';
            editArea.style.display = '';
            textarea.focus();
            textarea.setSelectionRange(textarea.value.length, textarea.value.length);
        });

        cancelBtn.addEventListener('click', () => {
            textarea.value = m.content;
            editArea.style.display = 'none';
            viewArea.style.display = '';
        });

        saveBtn.addEventListener('click', async () => {
            const newContent = textarea.value.trim();
            await updateMemo(m.id, newContent, date);
        });

        deleteBtn.addEventListener('click', async () => {
            await deleteMemo(m.id, date);
        });
    });
}

function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

/**
 * 메모 저장
 */
async function saveMemo() {
    if (!memosUrl) return;
    const dateInput = document.getElementById('memo-date-input');
    const contentInput = document.getElementById('memo-content-input');
    const date = dateInput ? dateInput.value.trim() : '';
    const content = contentInput ? contentInput.value.trim() : '';

    if (!date || !content) {
        alert('날짜와 내용을 모두 입력해주세요.');
        return;
    }

    try {
        const response = await fetch(memosUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ date, content }),
        });
        const result = await response.json();
        if (result.success) {
            if (!marketingMemos[date]) marketingMemos[date] = [];
            marketingMemos[date].push(result.data);
            if (contentInput) contentInput.value = '';
            renderMemoList(date);
            if (dailyChart) {
                dailyChart.options.plugins.annotation.annotations = buildMemoAnnotations();
                dailyChart.update();
            }
        } else {
            alert(result.error || '저장 중 오류가 발생했습니다.');
        }
    } catch (e) {
        console.error('메모 저장 오류:', e);
        alert('저장 중 오류가 발생했습니다.');
    }
}

/**
 * 메모 수정
 */
async function updateMemo(memoId, newContent, date) {
    if (!memosUrl || !newContent) {
        alert('내용을 입력해주세요.');
        return;
    }
    try {
        const response = await fetch(`${memosUrl}${memoId}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify({ content: newContent }),
        });
        const result = await response.json();
        if (result.success) {
            if (marketingMemos[date]) {
                const idx = marketingMemos[date].findIndex(m => String(m.id) === String(memoId));
                if (idx !== -1) marketingMemos[date][idx].content = result.data.content;
            }
            renderMemoList(date);
            if (dailyChart) {
                dailyChart.options.plugins.annotation.annotations = buildMemoAnnotations();
                dailyChart.update();
            }
        } else {
            alert(result.error || '수정 중 오류가 발생했습니다.');
        }
    } catch (e) {
        console.error('메모 수정 오류:', e);
        alert('수정 중 오류가 발생했습니다.');
    }
}

/**
 * 메모 삭제
 */
async function deleteMemo(memoId, date) {
    if (!memosUrl) return;
    if (!confirm('이 메모를 삭제하시겠습니까?')) return;
    try {
        const response = await fetch(`${memosUrl}${memoId}/`, {
            method: 'DELETE',
            headers: { 'X-CSRFToken': getCsrfToken() },
        });
        const result = await response.json();
        if (result.success) {
            if (marketingMemos[date]) {
                marketingMemos[date] = marketingMemos[date].filter(m => String(m.id) !== String(memoId));
                if (!marketingMemos[date].length) delete marketingMemos[date];
            }
            renderMemoList(date);
            if (dailyChart) {
                dailyChart.options.plugins.annotation.annotations = buildMemoAnnotations();
                dailyChart.update();
            }
        } else {
            alert(result.error || '삭제 중 오류가 발생했습니다.');
        }
    } catch (e) {
        console.error('메모 삭제 오류:', e);
        alert('삭제 중 오류가 발생했습니다.');
    }
}

function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.trim().split('=')[1] : '';
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
            memosUrl = data.memosUrl || null;
        }
    }

    loadMarketingMemos();

    const startDateInput = document.getElementById('filter-start-date');
    const endDateInput = document.getElementById('filter-end-date');

    if (startDateInput && endDateInput) {
        loadDashboardData();
    } else {
        loadDashboardData();
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
    if (paidFilter) {
        paidFilter.addEventListener('change', renderCharts);
    }

    // 메모 추가 버튼 (차트 영역 위)
    const addMemoBtn = document.getElementById('add-memo-btn');
    if (addMemoBtn) {
        addMemoBtn.addEventListener('click', function() {
            openMemoModal('');
        });
    }

    // 모달 닫기 버튼
    const memoCloseBtn = document.getElementById('memo-close-btn');
    if (memoCloseBtn) memoCloseBtn.addEventListener('click', closeMemoModal);

    // backdrop 클릭 시 닫기
    const memoBackdrop = document.getElementById('memo-backdrop');
    if (memoBackdrop) memoBackdrop.addEventListener('click', closeMemoModal);

    // 모달 날짜 변경 시 메모 목록 갱신
    const memoDateInput = document.getElementById('memo-date-input');
    if (memoDateInput) {
        memoDateInput.addEventListener('change', function() {
            renderMemoList(this.value);
        });
    }

    // 메모 저장 버튼
    const saveMemoBtn = document.getElementById('save-memo-btn');
    if (saveMemoBtn) {
        saveMemoBtn.addEventListener('click', saveMemo);
    }
});


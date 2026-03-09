let performanceId = null;
let dataUrl = null;
let currentData = null;
let chartData = null;
let dailyChart = null;
let gradeChart = null;
const chartYAxisWidth = 84;
const NOL_TICKET_COLOR = '#4154FF';
const TICKET_LINE_COLOR = '#16a34a';  /* success - 판매 매수 라인 */
const dynamicColors = ['#3b82f6', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#f97316', '#14b8a6'];

/** 합계(입금) %에 따른 행 배경색 (design-system 기준) */
function getTotalPaidRateCellStyle(rate) {
    if (rate == null || Number.isNaN(Number(rate))) return '';
    const r = Number(rate);
    if (r >= 1) return 'background-color: #dbeafe;';   /* 100% 이상: 파란 계열 */
    if (r >= 0.5) return 'background-color: #ffedd5;';  /* 50% 이상 100% 미만: 주황 계열 */
    return 'background-color: #fee2e2;';               /* 50% 미만: 빨간 계열 */
}

function parseJsonSafely(jsonString) {
    if (!jsonString || jsonString.trim() === '') return null;
    try {
        return JSON.parse(jsonString);
    } catch (e) {
        console.error('JSON parse error:', e);
        return null;
    }
}

function formatNumber(num) {
    if (typeof num === 'undefined' || num === null) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatRate(rate) {
    if (rate === null || typeof rate === 'undefined' || Number.isNaN(Number(rate))) return '-';
    return `${(Number(rate) * 100).toFixed(2)}%`;
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const day = date.getDate().toString().padStart(2, '0');
    return `${month}/${day}`;
}

function formatEpisodeDate(showDate, showDay) {
    if (!showDate) return '-';
    if (!showDay) return showDate;
    return `${showDate}(${showDay})`;
}

async function loadDashboardData(startDate, endDate) {
    if (!dataUrl) return;
    const query = startDate && endDate ? `?start_date=${startDate}&end_date=${endDate}` : '';
    const url = `${dataUrl}${query}`;
    try {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (!data.success) {
            alert('데이터를 불러올 수 없습니다.');
            return;
        }

        const isFiltered = !!(startDate && endDate);
        if (!isFiltered || !currentData) currentData = data.data;
        chartData = data.data;

        const startDateInput = document.getElementById('filter-start-date');
        const endDateInput = document.getElementById('filter-end-date');
        if (startDateInput && endDateInput && chartData) {
            startDateInput.value = chartData.applied_start_date || '';
            endDateInput.value = chartData.applied_end_date || '';
        }

        if (!isFiltered) {
            updateSummaryCards();
            renderGradeSales();
            renderEpisodeTable();
        }
        renderCharts();
    } catch (error) {
        console.error(error);
        alert('데이터를 불러오는 중 오류가 발생했습니다.');
    }
}

function updateSummaryCards() {
    if (!currentData) return;

    const targetRevenue = currentData.target_revenue || 0;
    const breakEvenPoint = currentData.break_even_point || 0;
    const totalRevenue = currentData.total_revenue || 0;
    const totalTickets = currentData.total_ticket_count || 0;
    const totalSeats = currentData.total_seats || 0;

    const revenueBar = document.getElementById('revenue-progress-bar');
    const revenueText = document.getElementById('summary-total-revenue-text');
    const bepMarker = document.getElementById('revenue-bep-marker');
    const bepText = document.getElementById('summary-break-even-text');
    const totalTicketsText = document.getElementById('summary-total-tickets-text');
    const totalSeatsText = document.getElementById('summary-total-seats-text');
    const targetRevenueText = document.querySelector('.target-revenue-value');

    if (targetRevenueText && targetRevenue > 0) {
        targetRevenueText.textContent = formatNumber(Math.round(targetRevenue));
    }

    if (revenueBar && revenueText) {
        const rate = targetRevenue > 0 ? Math.min(100, (totalRevenue / targetRevenue) * 100) : 0;
        revenueBar.style.width = `${rate}%`;
        revenueText.textContent = `${formatNumber(Math.round(totalRevenue))}원`;
    }

    if (bepMarker && bepText) {
        if (targetRevenue > 0 && breakEvenPoint > 0) {
            const bepRate = Math.min(100, (breakEvenPoint / targetRevenue) * 100);
            bepMarker.style.left = `${bepRate}%`;
            bepMarker.classList.remove('hidden');
            bepText.textContent = `${formatNumber(Math.round(breakEvenPoint))}원`;
        } else {
            bepMarker.classList.add('hidden');
            bepText.textContent = '-';
        }
    }

    if (totalTicketsText) {
        const openSeatsText = totalSeats > 0 ? `${formatNumber(totalSeats)}매` : '-';
        totalTicketsText.textContent = `${formatNumber(totalTickets)}매/${openSeatsText}`;
    }
    if (totalSeatsText) {
        totalSeatsText.textContent = totalSeats > 0 ? `${formatNumber(totalSeats)}매` : '-';
    }

    const ticketsBar = document.getElementById('tickets-progress-bar');
    if (ticketsBar) {
        const ticketRate = totalSeats > 0 ? Math.min(100, (totalTickets / totalSeats) * 100) : 0;
        ticketsBar.style.width = `${ticketRate}%`;
    }
}

function getSeries(dataMap, dates) {
    return dates.map((date) => {
        const dateObj = dataMap[date] || {};
        const musical = dateObj['뮤지컬'] || {};
        return musical.paid || 0;
    });
}

function renderDailyChart() {
    if (!chartData) return;
    const dates = chartData.dates || [];
    const labels = dates.map(formatDate);
    const revenueValues = getSeries(chartData.daily_revenue || {}, dates);
    const ticketValues = getSeries(chartData.daily_tickets || {}, dates);

    const canvas = document.getElementById('daily-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const revenueMax = Math.max(1, ...revenueValues);
    const ticketMax = Math.max(1, ...ticketValues);

    if (dailyChart) dailyChart.destroy();
    dailyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: '매출',
                    data: revenueValues,
                    backgroundColor: NOL_TICKET_COLOR,
                    borderRadius: 4,
                    yAxisID: 'y',
                }
            ]
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
                        title: (items) => items[0] ? labels[items[0].dataIndex] : '',
                        label: (context) => {
                            const i = context.dataIndex;
                            return `매출: ${formatNumber(Math.round(revenueValues[i]))}원  |  판매 매수: ${formatNumber(ticketValues[i])}매`;
                        },
                    },
                },
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    beginAtZero: true,
                    suggestedMax: revenueMax,
                    afterFit: (scale) => { scale.width = chartYAxisWidth; },
                    ticks: {
                        callback: (value) => formatNumber(Math.round(value)),
                    },
                    grid: {
                        display: false,
                    },
                    title: {
                        display: true,
                        text: '매출 (원)',
                    },
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    beginAtZero: true,
                    suggestedMax: ticketMax,
                    afterFit: (scale) => { scale.width = chartYAxisWidth; },
                    ticks: {
                        callback: (value) => formatNumber(Math.round(value)),
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

function renderCharts() {
    renderDailyChart();
    renderGradeChart();
}

function renderGradeSales() {
    if (!currentData || !currentData.grade_sales) return;
    const tbody = document.getElementById('grade-sales-tbody');
    if (!tbody) return;

    const gradeSales = currentData.grade_sales;
    const grades = Object.keys(gradeSales).sort();
    if (grades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-600">등급별 판매 데이터가 없습니다</td></tr>';
        return;
    }

    tbody.innerHTML = '';
    grades.forEach((grade) => {
        const data = gradeSales[grade];
        const paidCount = data.paid_count || 0;
        const freeCount = data.free_count || 0;
        const totalCount = data.total_count || 0;
        const seatCount = data.seat_count || 0;
        const paidOccupancyRate = (data.paid_occupancy_rate || 0) * 100;
        const totalOccupancyRate = (data.total_occupancy_rate || 0) * 100;
        const openSeatText = seatCount > 0 ? formatNumber(seatCount) : '-';

        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';
        tr.innerHTML = `
            <td class="px-6 py-4"><span class="text-base font-medium text-black">${grade}</span></td>
            <td class="px-6 py-4 text-right"><span class="text-sm text-black">${formatNumber(paidCount)}</span></td>
            <td class="px-6 py-4 text-right"><span class="text-sm text-black">${formatNumber(freeCount)}</span></td>
            <td class="px-6 py-4 text-right"><span class="text-sm text-black">${paidOccupancyRate.toFixed(1)}%</span></td>
            <td class="px-6 py-4 text-right"><span class="text-sm text-black">${totalOccupancyRate.toFixed(1)}%</span></td>
            <td class="px-6 py-4 text-right"><span class="text-sm text-black">${formatNumber(totalCount)}/${openSeatText}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function renderGradeChart() {
    const canvas = document.getElementById('grade-chart');
    if (!canvas) return;
    if (gradeChart) {
        gradeChart.destroy();
    }
    if (!currentData || !currentData.grade_sales) return;

    const gradeSales = currentData.grade_sales;
    const grades = Object.keys(gradeSales).sort();
    if (!grades.length) return;

    const paidCounts = grades.map((grade) => gradeSales[grade].paid_count || 0);
    const totalPaid = paidCounts.reduce((acc, value) => acc + value, 0);
    gradeChart = new Chart(canvas, {
        type: 'pie',
        data: {
            labels: grades,
            datasets: [
                {
                    label: '매수(유료)',
                    data: paidCounts,
                    backgroundColor: grades.map((_, idx) => dynamicColors[idx % dynamicColors.length]),
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
                        font: { size: 12 },
                        usePointStyle: true,
                    },
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = totalPaid > 0 ? ((value / totalPaid) * 100).toFixed(1) : '0.0';
                            return `${label}: ${formatNumber(value)}매 (${percentage}%)`;
                        }
                    }
                },
            },
        },
    });
}

function renderEpisodeTable() {
    if (!currentData) return;
    const tbody = document.getElementById('musical-episode-tbody');
    if (!tbody) return;
    const rows = currentData.episode_rows || [];
    if (!rows.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="px-6 py-6 text-center text-sm text-secondary">데이터가 없습니다.</td></tr>';
        return;
    }
    tbody.innerHTML = '';
    rows.forEach((row) => {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50 transition-colors';
        const rowBgStyle = getTotalPaidRateCellStyle(row.total_paid?.rate);
        if (rowBgStyle) tr.setAttribute('style', rowBgStyle);
        tr.innerHTML = `
            <td class="px-6 py-4 text-sm text-black whitespace-nowrap">${formatEpisodeDate(row.show_date, row.show_day)}</td>
            <td class="px-6 py-4 text-sm text-black whitespace-nowrap">${row.show_time || '-'}</td>
            <td class="px-6 py-4 text-sm text-black whitespace-nowrap">${row.cast || '-'}</td>
            <td class="px-6 py-4 text-sm text-black text-right whitespace-nowrap">${formatNumber(row.paid?.count || 0)}매 / ${formatRate(row.paid?.rate)} / ${formatNumber(Math.round(row.paid?.revenue || 0))}원</td>
            <td class="px-6 py-4 text-sm text-black text-right whitespace-nowrap">${formatNumber(row.unpaid?.count || 0)}매 / ${formatRate(row.unpaid?.rate)} / ${formatNumber(Math.round(row.unpaid?.revenue || 0))}원</td>
            <td class="px-6 py-4 text-sm text-black text-right whitespace-nowrap">${formatNumber(row.invited?.count || 0)}매 / ${formatRate(row.invited?.rate)}</td>
            <td class="px-6 py-4 text-sm text-black text-right whitespace-nowrap">${formatNumber(row.total_paid?.count || 0)}매 / ${formatRate(row.total_paid?.rate)}</td>
            <td class="px-6 py-4 text-sm text-black whitespace-nowrap">${row.remark || '-'}</td>
        `;
        tbody.appendChild(tr);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const dataScript = document.getElementById('concert-dashboard-data');
    if (dataScript) {
        const data = parseJsonSafely(dataScript.textContent);
        if (data) {
            performanceId = data.performanceId;
            dataUrl = data.dataUrl;
        }
    }

    loadDashboardData();

    const applyBtn = document.getElementById('filter-apply-btn');
    const startDateInput = document.getElementById('filter-start-date');
    const endDateInput = document.getElementById('filter-end-date');
    if (applyBtn && startDateInput && endDateInput) {
        applyBtn.addEventListener('click', function() {
            loadDashboardData(startDateInput.value, endDateInput.value);
        });
    }

    const legendTrigger = document.getElementById('episode-legend-trigger');
    const legendTooltip = document.getElementById('episode-legend-tooltip');
    const legendWrap = document.getElementById('episode-legend-wrap');
    if (legendTrigger && legendTooltip) {
        legendTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            const isHidden = legendTooltip.classList.contains('hidden');
            legendTooltip.classList.toggle('hidden', !isHidden);
            legendTooltip.classList.toggle('block', isHidden);
        });
        document.addEventListener('click', function(e) {
            if (legendWrap && !legendWrap.contains(e.target)) {
                legendTooltip.classList.add('hidden');
                legendTooltip.classList.remove('block');
            }
        });
    }
});

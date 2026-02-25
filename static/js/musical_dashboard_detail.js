let performanceId = null;
let dataUrl = null;
let currentData = null;
let chartData = null;
let revenueChart = null;
let ticketChart = null;
const chartYAxisWidth = 84;
const NOL_TICKET_COLOR = '#4154FF';

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
        totalTicketsText.textContent = `${formatNumber(totalTickets)}매`;
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

function renderRevenueChart() {
    if (!chartData) return;
    const dates = chartData.dates || [];
    const labels = dates.map(formatDate);
    const values = getSeries(chartData.daily_revenue || {}, dates);

    const canvas = document.getElementById('revenue-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (revenueChart) revenueChart.destroy();
    revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: '매출',
                data: values,
                backgroundColor: NOL_TICKET_COLOR,
                borderRadius: 4,
            }]
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
                        label: (context) => {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${formatNumber(Math.round(value))}원`;
                        },
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    afterFit: (scale) => { scale.width = chartYAxisWidth; },
                    ticks: {
                        callback: (value) => formatNumber(Math.round(value)),
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

function renderTicketChart() {
    if (!chartData) return;
    const dates = chartData.dates || [];
    const labels = dates.map(formatDate);
    const values = getSeries(chartData.daily_tickets || {}, dates);

    const canvas = document.getElementById('ticket-chart');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (ticketChart) ticketChart.destroy();
    ticketChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: '판매 매수',
                data: values,
                backgroundColor: NOL_TICKET_COLOR,
                borderRadius: 4,
            }]
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
                        label: (context) => {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y;
                            return `${label}: ${formatNumber(value)}매`;
                        },
                    },
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    afterFit: (scale) => { scale.width = chartYAxisWidth; },
                    ticks: {
                        callback: (value) => formatNumber(Math.round(value)),
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

function renderCharts() {
    renderRevenueChart();
    renderTicketChart();
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
});

// 전체 대시보드 (콘서트·뮤지컬·연극)
let summaryUrl = null;
let periodRevenueUrl = null;
let genreChart = null;
let periodChart = null;

function parseJsonSafely(str) {
    if (!str || !str.trim()) return null;
    try {
        return JSON.parse(str);
    } catch (e) {
        console.error('JSON 파싱 오류:', e);
        return null;
    }
}

function formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '0';
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatRevenue(num) {
    return formatNumber(Math.round(num)) + '원';
}

async function loadSummary() {
    if (!summaryUrl) return;
    try {
        const res = await fetch(summaryUrl);
        if (!res.ok) throw new Error('데이터를 불러올 수 없습니다.');
        const json = await res.json();
        if (!json.success) {
            console.error('요약 로드 실패:', json.error);
            return;
        }
        updateOverview(json.data);
    } catch (e) {
        console.error('요약 로드 오류:', e);
    }
}

function updateGoalSection(data) {
    const totalRev = data.total_revenue ?? 0;
    const target = data.total_target_revenue ?? 0;
    const bep = data.total_break_even_point ?? 0;

    const elRev = document.getElementById('overview-goal-revenue-text');
    const elBar = document.getElementById('overview-goal-progress-bar');
    const elBep = document.getElementById('overview-goal-bep-marker');
    const elTarget = document.getElementById('overview-target-revenue-text');
    const elBepText = document.getElementById('overview-bep-text');
    const elRate = document.getElementById('overview-achievement-rate');

    if (elRev) elRev.textContent = formatRevenue(totalRev) + ' / ' + (target > 0 ? formatRevenue(target) : '-');
    if (elTarget) elTarget.textContent = target > 0 ? formatRevenue(target) : '목표 미설정';
    if (elBepText) elBepText.textContent = bep > 0 ? formatRevenue(bep) : '-';

    if (target > 0 && elBar) {
        const rate = Math.min(100, (totalRev / target) * 100);
        elBar.style.width = rate + '%';
    } else if (elBar) {
        elBar.style.width = '0%';
    }
    if (target > 0 && bep > 0 && elBep) {
        const bepRate = Math.min(100, (bep / target) * 100);
        elBep.style.left = bepRate + '%';
        elBep.classList.remove('hidden');
    } else if (elBep) {
        elBep.classList.add('hidden');
    }
    if (elRate) {
        if (target > 0) {
            const rate = (totalRev / target) * 100;
            elRate.textContent = rate.toFixed(1) + '%';
        } else {
            elRate.textContent = '-';
        }
    }
}

function renderGenreChart(genres) {
    const canvas = document.getElementById('overview-genre-chart');
    const legendEl = document.getElementById('overview-genre-legend');
    if (!canvas) return;

    const concert = (genres.concert && genres.concert.total_revenue) ? genres.concert.total_revenue : 0;
    const musical = (genres.musical && genres.musical.total_revenue) ? genres.musical.total_revenue : 0;
    const theater = (genres.theater && genres.theater.total_revenue) ? genres.theater.total_revenue : 0;
    const total = concert + musical + theater;

    if (genreChart) {
        genreChart.destroy();
        genreChart = null;
    }

    if (total === 0) {
        if (legendEl) legendEl.innerHTML = '<span class="text-gray-500">매출 데이터가 없어요</span>';
        genreChart = new Chart(canvas, {
            type: 'doughnut',
            data: { labels: ['콘서트', '뮤지컬', '연극'], datasets: [{ data: [1], backgroundColor: ['#e5e7eb'], borderWidth: 0 }] },
            options: { responsive: true, maintainAspectRatio: true, plugins: { legend: { display: false } } },
        });
        return;
    }

    const colors = ['#3b82f6', '#10b981', '#78716c'];
    const labels = ['콘서트', '뮤지컬', '연극'];
    const values = [concert, musical, theater];
    const filtered = values.map((v, i) => ({ label: labels[i], value: v, color: colors[i] })).filter(x => x.value > 0);

    if (legendEl) {
        legendEl.innerHTML = filtered
            .map(
                (x) =>
                    '<div class="flex items-center gap-2 mb-2">' +
                    '<span class="w-3 h-3 rounded-full flex-shrink-0" style="background:' + x.color + '"></span>' +
                    '<span class="text-sm text-gray-700">' + x.label + ' ' + ((x.value / total) * 100).toFixed(1) + '%</span>' +
                    '</div>'
            )
            .join('');
    }

    genreChart = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: filtered.map((x) => x.label),
            datasets: [
                {
                    data: filtered.map((x) => x.value),
                    backgroundColor: filtered.map((x) => x.color),
                    borderWidth: 0,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const v = ctx.raw;
                            const p = total ? ((v / total) * 100).toFixed(1) : 0;
                            return ctx.label + ': ' + formatRevenue(v) + ' (' + p + '%)';
                        },
                    },
                },
            },
        },
    });
}

function setDefaultPeriodDates() {
    const startEl = document.getElementById('overview-period-start');
    const endEl = document.getElementById('overview-period-end');
    if (!startEl || !endEl) return;
    const periodType = document.querySelector('input[name="overview-period-type"]:checked')?.value || 'monthly';
    const today = new Date();
    let start = new Date(today);
    if (periodType === 'daily') {
        start.setDate(start.getDate() - 29);
    } else if (periodType === 'weekly') {
        const day = today.getDay();
        const toMonday = day === 0 ? 6 : day - 1;
        start.setDate(today.getDate() - toMonday - 21);
    } else {
        start.setMonth(today.getMonth() - 2, 1);
    }
    startEl.value = start.toISOString().split('T')[0];
    endEl.value = today.toISOString().split('T')[0];
}

async function loadPeriodRevenue() {
    if (!periodRevenueUrl) return;
    const periodType = document.querySelector('input[name="overview-period-type"]:checked')?.value || 'monthly';
    const start = document.getElementById('overview-period-start')?.value;
    const end = document.getElementById('overview-period-end')?.value;
    if (!start || !end) return;
    try {
        const url = periodRevenueUrl + '?period_type=' + periodType + '&start_date=' + start + '&end_date=' + end;
        const res = await fetch(url);
        if (!res.ok) throw new Error('기간별 데이터를 불러올 수 없습니다.');
        const json = await res.json();
        if (!json.success) {
            console.error('기간별 로드 실패:', json.error);
            return;
        }
        renderPeriodChart(json.data.periods || [], json.data.data || {});
    } catch (e) {
        console.error('기간별 로드 오류:', e);
    }
}

function renderPeriodChart(periods, data) {
    const canvas = document.getElementById('overview-period-chart');
    if (!canvas) return;
    const periodType = document.querySelector('input[name="overview-period-type"]:checked')?.value || 'monthly';
    const labels = periods.map((p) => {
        if (periodType === 'daily') {
            const d = new Date(p + 'T00:00:00');
            return (d.getMonth() + 1) + '/' + d.getDate();
        }
        if (periodType === 'weekly') {
            const d = new Date(p + 'T00:00:00');
            return (d.getMonth() + 1) + '월 ' + Math.ceil(d.getDate() / 7) + '주';
        }
        return p;
    });
    const values = periods.map((p) => data[p] || 0);

    if (periodChart) {
        periodChart.destroy();
        periodChart = null;
    }
    periodChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: '전체 매출',
                    data: values,
                    backgroundColor: 'rgba(42, 48, 56, 0.8)',
                    borderColor: '#2a3038',
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            return formatRevenue(ctx.raw);
                        },
                    },
                },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { maxRotation: 45 },
                },
                y: {
                    grid: { display: false },
                    ticks: {
                        callback: function (v) {
                            return formatNumber(v);
                        },
                    },
                },
            },
        },
    });
}

function updateOverview(data) {
    if (!data) return;

    const totalRev = data.total_revenue ?? 0;
    const totalTkt = data.total_ticket_count ?? 0;
    const todayRev = data.today_revenue ?? 0;
    const todayTkt = data.today_ticket_count ?? 0;

    const elTotalRev = document.getElementById('overview-total-revenue');
    const elTotalTkt = document.getElementById('overview-total-tickets');
    const elTodayRev = document.getElementById('overview-today-revenue');
    const elTodayTkt = document.getElementById('overview-today-tickets');
    if (elTotalRev) elTotalRev.textContent = formatRevenue(totalRev);
    if (elTotalTkt) elTotalTkt.textContent = formatNumber(totalTkt) + '매';
    if (elTodayRev) elTodayRev.textContent = formatRevenue(todayRev);
    if (elTodayTkt) elTodayTkt.textContent = formatNumber(todayTkt) + '매';

    updateGoalSection(data);

    const g = data.genres || {};
    const concert = g.concert || {};
    const musical = g.musical || {};
    const theater = g.theater || {};

    const elCr = document.getElementById('genre-concert-revenue');
    const elCt = document.getElementById('genre-concert-tickets');
    const elCc = document.getElementById('genre-concert-count');
    if (elCr) elCr.textContent = formatRevenue(concert.total_revenue ?? 0);
    if (elCt) elCt.textContent = formatNumber(concert.total_ticket_count ?? 0) + '매';
    if (elCc) elCc.textContent = (concert.performance_count ?? 0) + '건';

    const elMr = document.getElementById('genre-musical-revenue');
    const elMt = document.getElementById('genre-musical-tickets');
    const elMc = document.getElementById('genre-musical-count');
    if (elMr) elMr.textContent = formatRevenue(musical.total_revenue ?? 0);
    if (elMt) elMt.textContent = formatNumber(musical.total_ticket_count ?? 0) + '매';
    if (elMc) elMc.textContent = (musical.performance_count ?? 0) + '건';

    const elTc = document.getElementById('genre-theater-count');
    if (elTc) elTc.textContent = (theater.performance_count ?? 0) + '건';

    renderGenreChart(g);

    const startEl = document.getElementById('overview-period-start');
    const endEl = document.getElementById('overview-period-end');
    if (data.data_start_date && data.data_end_date && startEl && endEl) {
        startEl.value = data.data_start_date;
        endEl.value = data.data_end_date;
    } else {
        setDefaultPeriodDates();
    }
    loadPeriodRevenue();
}

document.addEventListener('DOMContentLoaded', function () {
    const script = document.getElementById('overview-data');
    if (script) {
        const config = parseJsonSafely(script.textContent);
        if (config) {
            if (config.summaryUrl) summaryUrl = config.summaryUrl;
            if (config.periodRevenueUrl) periodRevenueUrl = config.periodRevenueUrl;
        }
    }
    if (summaryUrl) loadSummary();

    document.querySelectorAll('input[name="overview-period-type"]').forEach(function (radio) {
        radio.addEventListener('change', function () {
            setDefaultPeriodDates();
            loadPeriodRevenue();
        });
    });
    const applyBtn = document.getElementById('overview-period-apply');
    if (applyBtn) applyBtn.addEventListener('click', loadPeriodRevenue);
});

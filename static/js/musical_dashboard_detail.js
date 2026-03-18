let performanceId = null;
let dataUrl = null;
let memosUrl = null;
let currentData = null;
let chartData = null;
let dailyChart = null;
let marketingMemos = {};
const chartYAxisWidth = 84;
const NOL_TICKET_COLOR = '#4154FF';
const TICKET_LINE_COLOR = '#16a34a';  /* success - 판매 매수 라인 */

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
                            const date = dates[i];
                            const memos = marketingMemos[date] || [];
                            const lines = [`매출: ${formatNumber(Math.round(revenueValues[i]))}원  |  판매 매수: ${formatNumber(ticketValues[i])}매`];
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

        const metaEl = document.createElement('p');
        metaEl.className = 'text-xs text-gray-400 mt-1';
        metaEl.textContent = m.created_at;

        row.appendChild(viewArea);
        row.appendChild(editArea);
        row.appendChild(metaEl);
        container.appendChild(row);

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

async function saveMemo() {
    if (!memosUrl) return;
    const dateInput = document.getElementById('memo-date-input');
    const contentInput = document.getElementById('memo-content-input');
    const date = dateInput ? dateInput.value.trim() : '';
    const content = contentInput ? contentInput.value.trim() : '';
    if (!date || !content) { alert('날짜와 내용을 모두 입력해주세요.'); return; }
    try {
        const response = await fetch(memosUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
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
        } else { alert(result.error || '저장 중 오류가 발생했습니다.'); }
    } catch (e) { console.error('메모 저장 오류:', e); alert('저장 중 오류가 발생했습니다.'); }
}

async function updateMemo(memoId, newContent, date) {
    if (!memosUrl || !newContent) { alert('내용을 입력해주세요.'); return; }
    try {
        const response = await fetch(`${memosUrl}${memoId}/`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
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
        } else { alert(result.error || '수정 중 오류가 발생했습니다.'); }
    } catch (e) { console.error('메모 수정 오류:', e); alert('수정 중 오류가 발생했습니다.'); }
}

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
        } else { alert(result.error || '삭제 중 오류가 발생했습니다.'); }
    } catch (e) { console.error('메모 삭제 오류:', e); alert('삭제 중 오류가 발생했습니다.'); }
}

function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.trim().split('=')[1] : '';
}

function renderCharts() {
    renderDailyChart();
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
            memosUrl = data.memosUrl || null;
        }
    }

    loadMarketingMemos();
    loadDashboardData();

    const addMemoBtn = document.getElementById('add-memo-btn');
    if (addMemoBtn) {
        addMemoBtn.addEventListener('click', function() { openMemoModal(''); });
    }

    const memoCloseBtn = document.getElementById('memo-close-btn');
    const memoCancelBtn = document.getElementById('memo-cancel-btn');
    if (memoCloseBtn) memoCloseBtn.addEventListener('click', closeMemoModal);
    if (memoCancelBtn) memoCancelBtn.addEventListener('click', closeMemoModal);

    const memoBackdrop = document.getElementById('memo-backdrop');
    if (memoBackdrop) memoBackdrop.addEventListener('click', closeMemoModal);

    const memoDateInput = document.getElementById('memo-date-input');
    if (memoDateInput) {
        memoDateInput.addEventListener('change', function() { renderMemoList(this.value); });
    }

    const saveMemoBtn = document.getElementById('save-memo-btn');
    if (saveMemoBtn) {
        saveMemoBtn.addEventListener('click', saveMemo);
    }

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

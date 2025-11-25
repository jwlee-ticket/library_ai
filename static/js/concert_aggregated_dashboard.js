// 콘서트 통합 대시보드 JavaScript
// 데이터는 HTML의 <script type="application/json" id="concert-aggregated-data"> 태그에서 로드됩니다.

// 전역 변수
let summaryDataUrl = null;

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
        if (todayRevenue > 0) {
            todayRevenueEl.innerHTML = '<span class="text-black">' + formatNumber(Math.round(todayRevenue)) + '</span>원';
        } else {
            todayRevenueEl.innerHTML = '<span class="text-secondary">-</span>';
        }
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
            revenueText.textContent = formatNumber(Math.round(totalRevenue)) + '원';
        } else {
            revenueBar.style.width = '0%';
            revenueText.textContent = '-';
        }
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
        if (todayTickets > 0) {
            todayTicketsEl.innerHTML = '<span class="text-black">' + formatNumber(todayTickets) + '</span>매';
        } else {
            todayTicketsEl.innerHTML = '<span class="text-secondary">-</span>';
        }
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
            ticketsText.textContent = formatNumber(totalTickets) + '매';
        } else {
            ticketsBar.style.width = '0%';
            ticketsText.textContent = '-';
        }
    }
    
    // 총 오픈 판매 매수 텍스트
    if (seatsText) {
        if (totalSeats > 0) {
            seatsText.textContent = formatNumber(totalSeats) + '매';
        } else {
            seatsText.textContent = '-';
        }
    }
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
        }
    }
    
    // 초기 데이터 로드
    if (summaryDataUrl) {
        loadSummaryData();
    }
});


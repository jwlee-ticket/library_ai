// 콘서트 매출 상세 페이지 JavaScript

// 전역 변수 (script 태그의 JSON 데이터에서 초기화)
let performanceId = null;
let bookingSites = [];
let seatGrades = [];
let salesDateList = [];
let savedDateList = [];
let ageGroups = [];
let regions = [];
let seoulRegions = [];
let gyeonggiRegions = [];
let saveDailySalesUrl = '';
let getDailySalesUrl = '';
let csrfToken = '';

// 오늘 날짜 정보
const today = new Date();
const currentYear = today.getFullYear();
const currentMonth = today.getMonth();
const currentDate = today.getDate();

// 캘린더 표시 월 (오늘 날짜 기준)
let displayYear = currentYear;
let displayMonth = currentMonth;

// 날짜별 상태 저장 (입력 전: null, 완료: 'completed')
const dateStatuses = {};

// 현재 선택된 날짜
let selectedDate = null;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // script 태그에서 JSON 데이터 읽기
    const dataScript = document.getElementById('concert-sales-data');
    if (!dataScript) {
        console.error('concert-sales-data script 태그를 찾을 수 없습니다.');
        return;
    }
    
    try {
        // JSON 파싱
        const data = JSON.parse(dataScript.textContent);
        
        // 전역 변수에 할당
        performanceId = data.performanceId || null;
        bookingSites = Array.isArray(data.bookingSites) ? data.bookingSites : [];
        seatGrades = Array.isArray(data.seatGrades) ? data.seatGrades : [];
        salesDateList = Array.isArray(data.salesDateList) ? data.salesDateList : [];
        savedDateList = Array.isArray(data.savedDateList) ? data.savedDateList : [];
        ageGroups = Array.isArray(data.ageGroups) ? data.ageGroups : [];
        regions = Array.isArray(data.regions) ? data.regions : [];
        seoulRegions = Array.isArray(data.seoulRegions) ? data.seoulRegions : [];
        gyeonggiRegions = Array.isArray(data.gyeonggiRegions) ? data.gyeonggiRegions : [];
        saveDailySalesUrl = data.saveDailySalesUrl || '';
        getDailySalesUrl = data.getDailySalesUrl || '';
        csrfToken = data.csrfToken || '';
        
        console.log('데이터 로드 완료:', {
            performanceId,
            bookingSites,
            bookingSitesLength: bookingSites.length,
            seatGrades,
            seatGradesLength: seatGrades.length,
            savedDateList,
            saveDailySalesUrl,
            csrfToken: csrfToken ? '있음' : '없음'
        });
        
        // bookingSites가 비어있으면 경고
        if (!bookingSites || bookingSites.length === 0) {
            console.warn('⚠️ 예매처 데이터가 비어있습니다.');
        }
    } catch (error) {
        console.error('데이터 초기화 오류:', error);
        console.error('에러 스택:', error.stack);
        console.error('원본 데이터:', dataScript.textContent);
        return;
    }
    
    // 캘린더 초기화
    initCalendar();
    
    // 실제 저장된 매출 데이터가 있는 날짜만 'completed' 상태로 설정
    if (savedDateList && savedDateList.length > 0) {
        savedDateList.forEach(dateStr => {
            dateStatuses[dateStr] = 'completed';
        });
    }
});

// 캘린더 초기화
function initCalendar() {
    renderCalendar();
}

// 캘린더 렌더링
function renderCalendar() {
    const container = document.getElementById('calendar-container');
    if (!container) return;
    
    // 월의 첫 번째 날과 마지막 날
    const firstDay = new Date(displayYear, displayMonth, 1);
    const lastDay = new Date(displayYear, displayMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay(); // 0=일요일
    
    // 월 이름
    const monthNames = ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월', '11월', '12월'];
    const monthName = monthNames[displayMonth];
    
    let html = `
        <div class="mb-6">
            <div class="flex justify-between items-center mb-4">
                <button onclick="changeMonth(-1)" class="p-2 hover:bg-gray-100 hover:shadow-sm rounded-lg transition-all duration-200 flex items-center justify-center">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                    </svg>
                </button>
                <h3 class="text-xl font-semibold text-black">${displayYear}년 ${monthName}</h3>
                <button onclick="changeMonth(1)" class="p-2 hover:bg-gray-100 hover:shadow-sm rounded-lg transition-all duration-200 flex items-center justify-center">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                </button>
            </div>
            
            <!-- 요일 헤더 -->
            <div class="grid grid-cols-7 gap-1 mb-2">
                <div class="text-center text-sm font-semibold text-secondary py-2">일</div>
                <div class="text-center text-sm font-semibold text-secondary py-2">월</div>
                <div class="text-center text-sm font-semibold text-secondary py-2">화</div>
                <div class="text-center text-sm font-semibold text-secondary py-2">수</div>
                <div class="text-center text-sm font-semibold text-secondary py-2">목</div>
                <div class="text-center text-sm font-semibold text-secondary py-2">금</div>
                <div class="text-center text-sm font-semibold text-secondary py-2">토</div>
            </div>
            
            <!-- 날짜 그리드 -->
            <div id="calendar-grid" class="grid grid-cols-7 gap-0 border border-gray-100 rounded-lg overflow-hidden">
    `;
    
    // 총 셀 개수 계산 (빈 칸 + 날짜)
    const totalCells = startingDayOfWeek + daysInMonth;
    const totalRows = Math.ceil(totalCells / 7);
    
    // 빈 칸 (이전 달의 마지막 날들)
    for (let i = 0; i < startingDayOfWeek; i++) {
        const rowIndex = Math.floor(i / 7);
        const colIndex = i % 7;
        const isLastRow = rowIndex === totalRows - 1;
        const isLastCol = colIndex === 6;
        let emptyCellClass = 'h-14 border-r border-b border-gray-100 bg-gray-50 w-full';
        if (isLastCol) {
            emptyCellClass = emptyCellClass.replace('border-r', '');
        }
        if (isLastRow) {
            emptyCellClass = emptyCellClass.replace('border-b', '');
        }
        html += `<div class="${emptyCellClass}"></div>`;
    }
    
    // 날짜 셀들
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${displayYear}-${String(displayMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const cellIndex = startingDayOfWeek + day - 1;
        const rowIndex = Math.floor(cellIndex / 7);
        const colIndex = cellIndex % 7;
        const isLastRow = rowIndex === totalRows - 1;
        const isLastCol = colIndex === 6;
        html += createDateCell(displayYear, displayMonth, day, dateStr, isLastRow, isLastCol);
    }
    
    // 마지막 행의 빈 칸들 (다음 달의 첫 날들)
    const remainingCells = totalCells % 7;
    if (remainingCells !== 0) {
        const emptyCellsAfter = 7 - remainingCells;
        for (let i = 0; i < emptyCellsAfter; i++) {
            const colIndex = remainingCells + i;
            const isLastCol = colIndex === 6;
            let emptyCellClass = 'h-14 border-r border-b border-gray-100 bg-gray-50 w-full';
            if (isLastCol) {
                emptyCellClass = emptyCellClass.replace('border-r', '');
            }
            // 마지막 행이므로 아래 테두리 제거
            emptyCellClass = emptyCellClass.replace('border-b', '');
            html += `<div class="${emptyCellClass}"></div>`;
        }
    }
    
    html += `
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// 날짜 셀 생성
function createDateCell(year, month, day, dateStr, isLastRow, isLastCol) {
    const isToday = year === currentYear && month === currentMonth && day === currentDate;
    const status = getDateStatus(dateStr);
    
    let cellClass = 'h-14 cursor-pointer flex items-center justify-center transition-all duration-200 text-sm font-medium relative border-r border-b border-gray-100 w-full';
    
    // 마지막 열이면 오른쪽 테두리 제거
    if (isLastCol) {
        cellClass = cellClass.replace('border-r', '');
    }
    // 마지막 행이면 아래 테두리 제거
    if (isLastRow) {
        cellClass = cellClass.replace('border-b', '');
    }
    
    if (isToday) {
        // 오늘 날짜: 브랜드 컬러
        cellClass += ' bg-brand text-white font-semibold shadow-sm hover:bg-brand-900';
    } else {
        // 상태별 스타일
        switch(status) {
            case 'completed':
                cellClass += ' bg-success/10 text-success hover:bg-success/20 hover:shadow-sm';
                break;
            default:
                cellClass += ' bg-white text-gray-700 hover:bg-gray-50 hover:shadow-sm';
        }
    }
    
    return `<div class="${cellClass}" onclick="openDateModal('${dateStr}')" data-date="${dateStr}">${day}</div>`;
}

// 날짜 상태 확인
function getDateStatus(dateStr) {
    return dateStatuses[dateStr] || null;
}

// 날짜 상태 업데이트
function updateDateStatus(dateStr, status) {
    dateStatuses[dateStr] = status;
    // savedDateList에도 추가 (중복 방지)
    if (status === 'completed' && savedDateList.indexOf(dateStr) === -1) {
        savedDateList.push(dateStr);
    }
    renderCalendar(); // 캘린더 다시 렌더링
}

// 월 변경
function changeMonth(direction) {
    displayMonth += direction;
    if (displayMonth < 0) {
        displayMonth = 11;
        displayYear--;
    } else if (displayMonth > 11) {
        displayMonth = 0;
        displayYear++;
    }
    renderCalendar();
}

// 모달 열기
function openDateModal(dateStr) {
    selectedDate = dateStr;
    const overlay = document.getElementById('date-modal-overlay');
    const modal = document.getElementById('date-modal');
    
    if (!overlay || !modal) {
        console.error('모달 요소를 찾을 수 없습니다.');
        return;
    }
    
    // bookingSites 확인 (디버깅 정보 포함)
    console.log('모달 열기 시점의 bookingSites:', {
        bookingSites,
        type: typeof bookingSites,
        isArray: Array.isArray(bookingSites),
        length: bookingSites ? bookingSites.length : 0
    });
    
    if (!bookingSites || !Array.isArray(bookingSites) || bookingSites.length === 0) {
        console.error('예매처 데이터가 없습니다:', {
            bookingSites,
            type: typeof bookingSites,
            isArray: Array.isArray(bookingSites)
        });
        alert('예매처 정보를 불러올 수 없습니다. 페이지를 새로고침해주세요.');
        return;
    }
    
    // 모달 내용 생성
    const dateObj = new Date(dateStr);
    const dateFormatted = dateObj.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' });
    
    // 예매처별 폼 생성
    let bookingSiteForms = '';
    try {
        bookingSiteForms = bookingSites.map(site => createBookingSiteForm(dateStr, site)).join('');
    } catch (error) {
        console.error('예매처 폼 생성 오류:', error);
        bookingSiteForms = '<div class="text-red-500">예매처 폼을 생성하는 중 오류가 발생했습니다.</div>';
    }
    
    // 초대 섹션 생성
    let inviteSection = '';
    if (seatGrades && seatGrades.length > 0) {
        try {
            inviteSection = createInviteSection(dateStr);
        } catch (error) {
            console.error('초대 섹션 생성 오류:', error);
            inviteSection = '';
        }
    }
    
    modal.innerHTML = `
        <div class="p-8">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-xl font-semibold text-black">${dateFormatted}</h3>
                <button onclick="closeDateModal()" class="p-2 hover:bg-gray-100 hover:shadow-sm rounded-lg transition-all duration-200">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="space-y-6">
                <!-- 예매처별 입금/미입금 -->
                <div class="space-y-4">
                    ${bookingSiteForms}
                </div>
                
                <!-- 초대 영역 (별도) -->
                ${inviteSection}
            </div>
            <div class="mt-6 flex justify-end gap-3">
                <button 
                    type="button"
                    onclick="closeDateModal()"
                    class="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 hover:shadow-sm transition-all duration-200"
                >
                    취소
                </button>
                <button 
                    type="button"
                    onclick="saveDateSales('${dateStr}')"
                    class="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary-900 active:bg-primary-800 hover:shadow-sm transition-all duration-200 shadow-sm"
                >
                    저장
                </button>
            </div>
        </div>
    `;
    
    // 모달에 tabindex 추가하여 포커스 받을 수 있게 하기
    modal.setAttribute('tabindex', '-1');
    
    // 모달 애니메이션 효과
    overlay.classList.remove('hidden');
    setTimeout(() => {
        overlay.classList.add('opacity-100');
        modal.classList.add('scale-100', 'opacity-100');
        // 모달에 포커스 주기
        modal.focus();
        
        // 모달 DOM이 완전히 렌더링된 후 기존 저장된 데이터 불러오기
        setTimeout(() => {
            loadExistingSalesData(dateStr);
        }, 50);
    }, 10);
}

// 기존 저장된 매출 데이터 불러오기
function loadExistingSalesData(dateStr) {
    if (!getDailySalesUrl) {
        console.warn('조회 URL이 설정되지 않았습니다.');
        return;
    }
    
    const url = `${getDailySalesUrl}?date=${dateStr}`;
    console.log('기존 데이터 조회 시작:', url);
    
    fetch(url, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        console.log('조회 응답 상태:', response.status);
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || `HTTP ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('조회된 데이터:', data);
        if (data.success && data.data) {
            // 각 예매처별로 데이터 채우기
            bookingSites.forEach(site => {
                if (data.data[site]) {
                    const siteData = data.data[site];
                    const siteId = `${dateStr}_${site}`;
                    
                    // 기본 필드 채우기
                    const paidRevenueInput = document.getElementById(`${siteId}_paid_revenue`);
                    const paidTicketCountInput = document.getElementById(`${siteId}_paid_ticket_count`);
                    const unpaidRevenueInput = document.getElementById(`${siteId}_unpaid_revenue`);
                    const unpaidTicketCountInput = document.getElementById(`${siteId}_unpaid_ticket_count`);
                    
                    if (paidRevenueInput) paidRevenueInput.value = siteData.paid_revenue || 0;
                    if (paidTicketCountInput) paidTicketCountInput.value = siteData.paid_ticket_count || 0;
                    if (unpaidRevenueInput) unpaidRevenueInput.value = siteData.unpaid_revenue || 0;
                    if (unpaidTicketCountInput) unpaidTicketCountInput.value = siteData.unpaid_ticket_count || 0;
                    
                    // 등급별 매수 채우기
                    if (siteData.paid_by_grade && seatGrades) {
                        seatGrades.forEach(grade => {
                            const gradeInput = document.getElementById(`${siteId}_paid_grade_${grade}`);
                            if (gradeInput && siteData.paid_by_grade[grade]) {
                                gradeInput.value = siteData.paid_by_grade[grade];
                            }
                        });
                        // 입금 등급별 매수 합계 업데이트
                        updateTicketCount(siteId, 'paid');
                    }
                    
                    if (siteData.unpaid_by_grade && seatGrades) {
                        seatGrades.forEach(grade => {
                            const gradeInput = document.getElementById(`${siteId}_unpaid_grade_${grade}`);
                            if (gradeInput && siteData.unpaid_by_grade[grade]) {
                                gradeInput.value = siteData.unpaid_by_grade[grade];
                            }
                        });
                        // 미입금 등급별 매수 합계 업데이트
                        updateTicketCount(siteId, 'unpaid');
                    }
                    
                    // 초대 등급별 매수 채우기 (첫 번째 예매처의 값 사용)
                    if (siteData.free_by_grade && seatGrades && site === bookingSites[0]) {
                        seatGrades.forEach(grade => {
                            const firstSiteId = `${dateStr}_${bookingSites[0]}`;
                            const freeInput = document.getElementById(`${firstSiteId}_free_grade_${grade}`);
                            if (freeInput && siteData.free_by_grade[grade]) {
                                freeInput.value = siteData.free_by_grade[grade];
                                // 다른 예매처에도 동기화
                                syncInviteInputs(dateStr, grade);
                            }
                        });
                    }
                }
            });
            console.log('기존 데이터 로드 완료');
        }
    })
    .catch(error => {
        console.error('기존 데이터 조회 오류:', error);
        // 조회 실패해도 모달은 계속 사용 가능하도록 함
    });
}

// 모달 닫기
function closeDateModal() {
    const overlay = document.getElementById('date-modal-overlay');
    const modal = document.getElementById('date-modal');
    
    if (overlay && modal) {
        // 애니메이션 효과
        overlay.classList.remove('opacity-100');
        modal.classList.remove('scale-100', 'opacity-100');
        modal.classList.add('scale-95', 'opacity-0');
        
        setTimeout(() => {
            overlay.classList.add('hidden');
            selectedDate = null;
        }, 200);
    }
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', function(event) {
    const overlay = document.getElementById('date-modal-overlay');
    const modal = document.getElementById('date-modal');
    
    if (overlay && modal && event.target === overlay) {
        closeDateModal();
    }
});

// ESC 키로 모달 닫기 (전역 이벤트 리스너)
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' || event.keyCode === 27) {
        const overlay = document.getElementById('date-modal-overlay');
        // 모달이 열려있는지 확인 (hidden 클래스가 없고 selectedDate가 있으면 열려있음)
        if (overlay && selectedDate && !overlay.classList.contains('hidden')) {
            event.preventDefault();
            event.stopPropagation();
            closeDateModal();
        }
    }
}, true); // capture phase에서 처리하여 입력 필드에서도 작동하도록

function createBookingSiteForm(dateStr, bookingSite) {
    const siteId = `${dateStr}_${bookingSite}`;
    
    return `
        <div class="border-2 border-gray-100 rounded-lg p-4">
            <h4 class="text-base font-semibold text-black mb-4">${bookingSite}</h4>
            <!-- 입금과 미입금을 가로로 5:5 배치 -->
            <div class="grid grid-cols-2 gap-6">
                <!-- 입금 -->
                <div class="pr-6 border-r border-gray-200">
                    <label class="block text-sm font-medium text-gray-700 mb-2">입금</label>
                    <div class="grid grid-cols-2 gap-4 mb-3">
                        <div>
                            <label class="block text-xs text-gray-600 mb-1">판매액 (원)</label>
                            <input type="number" id="${siteId}_paid_revenue" name="${bookingSite}_paid_revenue" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-600 mb-1">판매 매수</label>
                            <input type="number" id="${siteId}_paid_ticket_count" name="${bookingSite}_paid_ticket_count" min="0" placeholder="0" ${seatGrades.length > 0 ? 'readonly class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg bg-gray-100 cursor-not-allowed"' : 'class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200"'}">
                        </div>
                    </div>
                    ${seatGrades.length > 0 ? `
                        <div class="mb-2">
                            <label class="block text-xs text-gray-600 mb-2">등급별 매수 (입금)</label>
                            <div class="grid grid-cols-2 gap-2">
                                ${seatGrades.map(grade => `
                                    <div class="relative">
                                        <label class="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 pointer-events-none">${grade} :</label>
                                        <input type="number" id="${siteId}_paid_grade_${grade}" name="${bookingSite}_paid_grade_${grade}" min="0" placeholder="0" oninput="updateTicketCount('${siteId}', 'paid')" class="w-full pl-12 pr-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200">
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
                
                <!-- 미입금 -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">미입금</label>
                    <div class="grid grid-cols-2 gap-4 mb-3">
                        <div>
                            <label class="block text-xs text-gray-600 mb-1">판매액 (원)</label>
                            <input type="number" id="${siteId}_unpaid_revenue" name="${bookingSite}_unpaid_revenue" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200">
                        </div>
                        <div>
                            <label class="block text-xs text-gray-600 mb-1">판매 매수</label>
                            <input type="number" id="${siteId}_unpaid_ticket_count" name="${bookingSite}_unpaid_ticket_count" min="0" placeholder="0" ${seatGrades.length > 0 ? 'readonly class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg bg-gray-100 cursor-not-allowed"' : 'class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200"'}">
                        </div>
                    </div>
                    ${seatGrades.length > 0 ? `
                        <div class="mb-2">
                            <label class="block text-xs text-gray-600 mb-2">등급별 매수 (미입금)</label>
                            <div class="grid grid-cols-2 gap-2">
                                ${seatGrades.map(grade => `
                                    <div class="relative">
                                        <label class="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 pointer-events-none">${grade} :</label>
                                        <input type="number" id="${siteId}_unpaid_grade_${grade}" name="${bookingSite}_unpaid_grade_${grade}" min="0" placeholder="0" oninput="updateTicketCount('${siteId}', 'unpaid')" class="w-full pl-12 pr-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200">
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        </div>
    `;
}

function createInviteSection(dateStr) {
    // 예매처별로 입력하되, UI에서는 예매처를 구분하지 않고 등급별로만 표시
    // 저장 시에는 각 예매처에 동일한 값이 저장되도록 처리
    return `
        <div class="border-2 border-gray-100 rounded-lg p-4">
            <h4 class="text-base font-semibold text-black mb-4">초대</h4>
            <div class="grid grid-cols-2 gap-2">
                ${seatGrades.map(grade => {
                    // 첫 번째 예매처의 입력 필드만 표시 (나머지는 hidden으로 저장)
                    const firstSiteId = `${dateStr}_${bookingSites[0]}`;
                    const hiddenInputs = bookingSites.slice(1).map(bookingSite => {
                        const siteId = `${dateStr}_${bookingSite}`;
                        return `<input type="hidden" id="${siteId}_free_grade_${grade}" name="${bookingSite}_free_grade_${grade}" value="0">`;
                    }).join('');
                    return `
                        <div class="relative">
                            <label class="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-gray-500 pointer-events-none">${grade} :</label>
                            <input type="number" id="${firstSiteId}_free_grade_${grade}" name="${bookingSites[0]}_free_grade_${grade}" min="0" placeholder="0" oninput="syncInviteInputs('${dateStr}', '${grade}')" class="w-full pl-12 pr-3 py-2 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary focus:ring-2 focus:ring-primary-200 transition-all duration-200">
                            ${hiddenInputs}
                        </div>
                    `;
                }).join('')}
            </div>
        </div>
    `;
}

function syncInviteInputs(dateStr, grade) {
    // 첫 번째 예매처의 값을 다른 예매처들에도 동일하게 적용
    const firstInput = document.getElementById(`${dateStr}_${bookingSites[0]}_free_grade_${grade}`);
    if (firstInput) {
        const value = firstInput.value || 0;
        bookingSites.slice(1).forEach(bookingSite => {
            const hiddenInput = document.getElementById(`${dateStr}_${bookingSite}_free_grade_${grade}`);
            if (hiddenInput) {
                hiddenInput.value = value;
            }
        });
    }
}

function updateTicketCount(siteId, type) {
    if (!seatGrades || seatGrades.length === 0) return;
    
    let total = 0;
    seatGrades.forEach(grade => {
        const input = document.getElementById(`${siteId}_${type}_grade_${grade}`);
        if (input) {
            const value = parseInt(input.value) || 0;
            total += value;
        }
    });
    
    const ticketCountInput = document.getElementById(`${siteId}_${type}_ticket_count`);
    if (ticketCountInput) {
        ticketCountInput.value = total;
    }
}

function saveDateSales(dateStr) {
    // URL 확인
    if (!saveDailySalesUrl) {
        console.error('저장 URL이 설정되지 않았습니다.');
        alert('저장 URL이 설정되지 않았습니다.');
        return;
    }
    
    console.log('매출 저장 시작:', {
        dateStr,
        saveDailySalesUrl,
        bookingSites,
        seatGrades
    });
    
    const formData = new FormData();
    formData.append('date', dateStr);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    // 해당 날짜의 모든 입력 필드 수집
    bookingSites.forEach(site => {
        const siteId = `${dateStr}_${site}`;
        const paidRevenue = document.getElementById(`${siteId}_paid_revenue`)?.value || '0';
        const paidTicketCount = document.getElementById(`${siteId}_paid_ticket_count`)?.value || '0';
        const unpaidRevenue = document.getElementById(`${siteId}_unpaid_revenue`)?.value || '0';
        const unpaidTicketCount = document.getElementById(`${siteId}_unpaid_ticket_count`)?.value || '0';
        
        formData.append(`${site}_paid_revenue`, paidRevenue);
        formData.append(`${site}_paid_ticket_count`, paidTicketCount);
        formData.append(`${site}_unpaid_revenue`, unpaidRevenue);
        formData.append(`${site}_unpaid_ticket_count`, unpaidTicketCount);
        
        seatGrades.forEach(grade => {
            const paidGrade = document.getElementById(`${siteId}_paid_grade_${grade}`)?.value || '0';
            const unpaidGrade = document.getElementById(`${siteId}_unpaid_grade_${grade}`)?.value || '0';
            // 초대는 첫 번째 예매처의 값을 모든 예매처에 동일하게 적용
            const firstSiteId = `${dateStr}_${bookingSites[0]}`;
            const freeValue = document.getElementById(`${firstSiteId}_free_grade_${grade}`)?.value || '0';
            
            formData.append(`${site}_paid_grade_${grade}`, paidGrade);
            formData.append(`${site}_unpaid_grade_${grade}`, unpaidGrade);
            formData.append(`${site}_free_grade_${grade}`, freeValue);
        });
    });
    
    // FormData 내용 확인 (디버깅용)
    console.log('전송할 데이터:', {
        date: dateStr,
        csrfToken: csrfToken ? '있음' : '없음'
    });
    
    fetch(saveDailySalesUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => {
        console.log('응답 상태:', response.status, response.statusText);
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || `HTTP ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('저장 응답:', data);
        if (data.success) {
            // savedDateList에 날짜 추가 (중복 방지)
            if (savedDateList.indexOf(dateStr) === -1) {
                savedDateList.push(dateStr);
            }
            // 날짜 상태 업데이트 및 캘린더 다시 렌더링
            updateDateStatus(dateStr, 'completed');
            closeDateModal(); // 모달 닫기
        } else {
            console.error('저장 실패:', data);
            alert('저장 실패: ' + (data.error || '알 수 없는 오류'));
        }
    })
    .catch(error => {
        console.error('저장 중 오류:', error);
        alert('저장 중 오류가 발생했어요: ' + error.message);
    });
}

function updateDateStatus(dateStr, status) {
    const statusEl = document.getElementById(`status-${dateStr}`);
    if (statusEl) {
        statusEl.textContent = status;
        if (status === '입력 완료') {
            statusEl.className = 'px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700';
        } else if (status === '입력 중') {
            statusEl.className = 'px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700';
        } else {
            statusEl.className = 'px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600';
        }
    }
}

// 등급별 판매현황은 템플릿에서 자동 생성됨 (모든 등급에 대해)

// 할인권종 판매현황은 템플릿에서 자동 생성됨 (공연 모델의 discount_types 기반)

// 연령대별 성별 판매현황은 템플릿에서 자동 생성됨 (AGE_GROUPS의 모든 항목에 대해)

// 4-1. 결제수단별 판매현황 항목 추가
function addPaymentMethodSalesItem() {
    const container = document.getElementById('final_payment_method_sales');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = 'flex gap-4 items-end';
    div.innerHTML = `
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">결제수단</label>
            <input type="text" placeholder="예: 신용카드" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="payment_method">
        </div>
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">매수</label>
            <input type="number" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="count">
        </div>
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">금액</label>
            <input type="number" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="amount">
        </div>
        <button type="button" onclick="removePaymentMethodSalesItem(this)" class="p-2 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
        </button>
    `;
    container.appendChild(div);
}

function removePaymentMethodSalesItem(button) {
    button.closest('div').remove();
}

// 4-2. 카드별 매출집계 항목 추가
function addCardSalesItem() {
    const container = document.getElementById('final_card_sales_summary');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = 'flex gap-4 items-end';
    div.innerHTML = `
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">카드종류</label>
            <input type="text" placeholder="예: 삼성카드" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="card_type">
        </div>
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">매수</label>
            <input type="number" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="count">
        </div>
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">금액</label>
            <input type="number" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="amount">
        </div>
        <button type="button" onclick="removeCardSalesItem(this)" class="p-2 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
        </button>
    `;
    container.appendChild(div);
}

function removeCardSalesItem(button) {
    button.closest('div').remove();
}

// 6. 판매경로별 판매현황 항목 추가
function addSalesChannelSalesItem() {
    const container = document.getElementById('final_sales_channel_sales');
    if (!container) return;
    
    const div = document.createElement('div');
    div.className = 'flex gap-4 items-end';
    div.innerHTML = `
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">판매경로</label>
            <input type="text" placeholder="예: 온라인" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="sales_channel">
        </div>
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">매수</label>
            <input type="number" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="count">
        </div>
        <div class="flex-1">
            <label class="block text-xs text-gray-600 mb-1">금액</label>
            <input type="number" min="0" placeholder="0" class="w-full px-3 py-2 border-2 border-gray-200 rounded-lg" data-field="amount">
        </div>
        <button type="button" onclick="removeSalesChannelSalesItem(this)" class="p-2 text-red-500 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
            </svg>
        </button>
    `;
    container.appendChild(div);
}

function removeSalesChannelSalesItem(button) {
    button.closest('div').remove();
}

// 지역별 판매현황은 템플릿에서 자동 생성됨 (REGIONS, SEOUL_REGIONS, GYEONGGI_REGIONS의 모든 항목에 대해)

// 최종 매출 저장
function saveFinalSales() {
    // TODO: AJAX로 저장 요청
    alert('최종 매출 저장 기능은 아직 구현 중입니다.');
}

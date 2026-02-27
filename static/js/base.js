// 드롭다운 토글 함수들

/**
 * 장르별 대시보드 드롭다운 토글
 */
function toggleGenreDropdown() {
    const dropdown = document.getElementById('genre-dropdown');
    const arrow = document.getElementById('genre-arrow');
    if (!dropdown || !arrow) return;
    dropdown.classList.toggle('hidden');
    arrow.classList.toggle('rotate-180');
}

/**
 * 데이터 관리 드롭다운 토글
 */
function toggleDataDropdown() {
    const dropdown = document.getElementById('data-dropdown');
    const arrow = document.getElementById('data-arrow');
    if (!dropdown || !arrow) return;
    dropdown.classList.toggle('hidden');
    arrow.classList.toggle('rotate-180');
}

/**
 * 사용자 드롭다운 토글
 */
function toggleUserDropdown() {
    const dropdown = document.getElementById('user-dropdown');
    if (!dropdown) return;
    dropdown.classList.toggle('hidden');
}

// 외부 클릭 시 사용자 드롭다운 닫기
document.addEventListener('click', function(event) {
    const userButton = document.querySelector('button[onclick="toggleUserDropdown()"]');
    const userDropdown = document.getElementById('user-dropdown');
    if (userButton && userDropdown && !userButton.contains(event.target) && !userDropdown.contains(event.target)) {
        if (!userDropdown.classList.contains('hidden')) {
            userDropdown.classList.add('hidden');
        }
    }
});

// 숫자 포맷팅 유틸리티 함수들

/**
 * 숫자에 세 자리마다 콤마 추가
 * @param {string|number} value - 포맷팅할 숫자
 * @returns {string} 콤마가 추가된 문자열
 */
function formatNumber(value) {
    if (value === '' || value === null || value === undefined) return '';
    // 콤마 제거 후 숫자만 추출
    const numStr = String(value).replace(/,/g, '');
    // 숫자가 아닌 경우 빈 문자열 반환
    if (numStr === '' || isNaN(numStr)) return '';
    // 세 자리마다 콤마 추가
    return parseInt(numStr, 10).toLocaleString('ko-KR');
}

/**
 * 콤마가 포함된 문자열에서 숫자만 추출
 * @param {string} value - 콤마가 포함된 문자열
 * @returns {string} 숫자만 포함된 문자열
 */
function removeCommas(value) {
    if (!value) return '';
    return String(value).replace(/,/g, '');
}

/**
 * 입력 필드에 숫자 포맷팅 적용
 * @param {HTMLInputElement} input - 포맷팅을 적용할 입력 필드
 */
function applyNumberFormatting(input) {
    if (!input) return;
    
    // 입력 이벤트: 입력 시 자동 포맷팅
    input.addEventListener('input', function(e) {
        const cursorPosition = this.selectionStart;
        const oldValue = this.value;
        const formattedValue = formatNumber(this.value);
        
        // 포맷팅된 값이 변경된 경우에만 업데이트
        if (oldValue !== formattedValue) {
            this.value = formattedValue;
            // 커서 위치 조정 (콤마 추가로 인한 위치 변화 보정)
            const newCursorPosition = cursorPosition + (formattedValue.length - oldValue.length);
            this.setSelectionRange(newCursorPosition, newCursorPosition);
        }
    });
    
    // 포커스 아웃 시 포맷팅 확정
    input.addEventListener('blur', function() {
        if (this.value) {
            this.value = formatNumber(this.value);
        }
    });
    
    // 포커스 인 시 콤마 제거 (편집 편의)
    input.addEventListener('focus', function() {
        const numValue = removeCommas(this.value);
        if (numValue && numValue !== this.value) {
            const cursorPosition = this.selectionStart;
            this.value = numValue;
            // 커서 위치 유지
            this.setSelectionRange(cursorPosition, cursorPosition);
        }
    });
}

/**
 * 클래스나 셀렉터로 여러 입력 필드에 포맷팅 적용
 * @param {string} selector - CSS 셀렉터 또는 클래스명
 */
function applyNumberFormattingToSelector(selector) {
    document.querySelectorAll(selector).forEach(input => {
        if (input.tagName === 'INPUT' && (input.type === 'number' || input.type === 'text')) {
            applyNumberFormatting(input);
        }
    });
}


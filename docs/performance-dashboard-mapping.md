# 공연별 대시보드 데이터 매핑

공연별 대시보드 화면에서 사용하는 데이터 항목을
엑셀 업로드로 적재된 DB 기준으로 매핑한 문서입니다.

## 1) 데이터 소스
- 엑셀 업로드 파서: `회차별판매` 시트 기반
- 저장 모델
  - `data_management.PerformanceDailySales`
  - `data_management.PerformanceDailySalesGrade`
  - `performance.Performance`

## 2) 화면 섹션별 매핑

### A. KPI 요약 카드
| 화면 항목 | 계산/출처 | DB 필드 |
| --- | --- | --- |
| 총 매출 | `SUM(paid_revenue + unpaid_revenue)` | `PerformanceDailySales.paid_revenue`, `PerformanceDailySales.unpaid_revenue` |
| 총 판매 매수 | `SUM(paid_ticket_count + unpaid_ticket_count)` | `PerformanceDailySales.paid_ticket_count`, `PerformanceDailySales.unpaid_ticket_count` |
| 기간 | 공연 기간 표시 | `Performance.performance_start`, `Performance.performance_end` |

### B. 일별 추이
| 화면 항목 | 계산/출처 | DB 필드 |
| --- | --- | --- |
| 일별 매출 | 날짜별 `SUM(paid_revenue + unpaid_revenue)` | `PerformanceDailySales` (group by `date`) |
| 일별 판매 매수 | 날짜별 `SUM(paid_ticket_count + unpaid_ticket_count)` | `PerformanceDailySales` (group by `date`) |

### C. 등급별 판매 현황
| 화면 항목 | 계산/출처 | DB 필드 |
| --- | --- | --- |
| 등급별 유료 매수 | `SUM(paid_count)` | `PerformanceDailySalesGrade.paid_count` |
| 등급별 미입금 매수 | `SUM(unpaid_count)` | `PerformanceDailySalesGrade.unpaid_count` |
| 등급별 무료 매수 | `SUM(free_count)` | `PerformanceDailySalesGrade.free_count` |
| 등급별 총 매수 | `paid + unpaid + free` | `PerformanceDailySalesGrade` 합산 |
| 등급별 비중 | `등급별 총 매수 / 전체 총 매수` | 계산값 |

### D. 예매처별 비중
| 화면 항목 | 계산/출처 | DB 필드 |
| --- | --- | --- |
| 예매처별 매출 | 예매처별 `SUM(paid_revenue + unpaid_revenue)` | `PerformanceDailySales.booking_site` 기준 합계 |
| 예매처별 매수 | 예매처별 `SUM(paid_ticket_count + unpaid_ticket_count)` | `PerformanceDailySales.booking_site` 기준 합계 |
| 예매처 비중 | `예매처 합계 / 전체 합계` | 계산값 |

### E. 메타 정보(선택)
| 화면 항목 | 계산/출처 | DB 필드 |
| --- | --- | --- |
| 데이터 업데이트 일자 | 최근 업로드 날짜 | `PerformanceDailySales.date` 최대값 |
| 커버리지 | 업로드된 날짜 범위 | `PerformanceDailySales.date` 최소/최대 |

## 3) 필터 기준
- 공연 선택: `performance_id`
- 기간 필터: `date` 범위
- 예매처 필터(선택): `booking_site`

## 4) 엑셀 → DB 요약 매핑
| 엑셀(회차별판매) | DB |
| --- | --- |
| 공연일(Date) | `PerformanceDailySales.date` |
| 예매처 그룹 | `PerformanceDailySales.booking_site` |
| 입금 TOT/금액 | `paid_ticket_count`, `paid_revenue` |
| 입금+미입금 TOT/금액 | `paid + unpaid` 합계 |
| 초대 등급별 매수 | `PerformanceDailySalesGrade.free_count` |


# 엑셀 → DB 매핑표 (공연 매출)

## 대상 모델
- `data_management.models.PerformanceDailySales`
- `data_management.models.PerformanceDailySalesGrade`

## 기본 전제
- 엑셀의 `회차별판매` 시트를 기준으로 매핑한다.
- 업로드 시 사용자가 선택한 공연(`performance`)을 기준으로 저장한다.
- 예매처/등급은 엑셀 컬럼을 정규화한 이름으로 매칭한다.

## PerformanceDailySales 매핑
| 엑셀 컬럼(회차별판매) | 설명 | 모델 필드 |
| --- | --- | --- |
| `Date` / `공연일` | 공연 날짜 | `date` |
| 예매처 그룹명 | `인터파크`, `코스타티켓`, `국립극장`, `라이브러리컴퍼니` 등 | `booking_site` |
| 예매처-`입금` 블록의 `TOT` | 예매처 입금 매수 | `paid_ticket_count` |
| 예매처-`입금` 블록의 `금액` | 예매처 입금 금액 | `paid_revenue` |
| 예매처-`입금+미입금` 블록의 `TOT` | 예매처 총 매수 | `paid_ticket_count + unpaid_ticket_count` |
| `입금+미입금 TOT - 입금 TOT` | 미입금 매수 계산 | `unpaid_ticket_count` |
| `입금+미입금 금액 - 입금 금액` | 미입금 금액 계산 | `unpaid_revenue` |
| `No.` / `Time` / 캐스트 | 회차 메타 정보 | `notes` (JSON 저장) |
| `점유율`, `잔여석`, `객단가` 등 | 분석용 보조 데이터 | `notes` (JSON 저장, 선택) |

### 예시 (notes JSON)
```
{
  "round_no": 12,
  "time": "19:30",
  "cast": {"순희": "박지연", "유령": "송원근"},
  "occupancy_rate": 0.132
}
```

## PerformanceDailySalesGrade 매핑
| 엑셀 컬럼(회차별판매) | 설명 | 모델 필드 |
| --- | --- | --- |
| 예매처-`입금` 블록의 등급별 매수 | `R`, `S`, `A`, `휠체어석`, `비지정석` | `paid_count` |
| 예매처-`입금+미입금` 블록의 등급별 매수 | 총 매수 | `paid_count + unpaid_count` |
| `입금+미입금 등급 매수 - 입금 등급 매수` | 미입금 매수 | `unpaid_count` |
| `초대` 블록의 등급별 매수 | 무료(초대) 매수 | `free_count` |
| 등급명 | 좌석 등급 | `seat_grade` |

### 좌석 등급 매칭 규칙
- 엑셀 등급명을 그대로 `SeatGrade.name`에 매칭
- 미존재 시 `SeatGrade` 신규 생성(공연에 연결)

## 매핑 예외 규칙
- `입금+미입금` 블록이 없으면 `unpaid_*`는 0
- `초대` 블록이 없으면 `free_count`는 0
- 음수 결과는 0으로 보정
- `TOTAL`, `계`, `합계` 행은 스킵

## 참고: PerformanceFinalSales
현재 기본 파서는 `PerformanceFinalSales`에 저장하지 않는다.
향후 `판매상세` 또는 `Daily` 시트에서 집계 데이터가 필요할 경우
`grade_sales_summary`나 `payment_method_sales` 같은 JSON 필드에 저장한다.

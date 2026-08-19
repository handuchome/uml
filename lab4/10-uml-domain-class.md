# 10. UML Domain & Class Diagram

## 1. Domain Model
```mermaid
classDiagram
  class RawFeeRecord {
    +String Ngay
    +String AppCode
    +String MaKhachHang
    +Decimal SoTienGoc
    +Validate()
  }
  class ProcessedFeeTask {
    +String TaskId
    +String LoaiPhi
    +Decimal SoTienPhi
    +Int RetryCount
    +String Status
    +Date NgayPhaiThu
    +IncrementRetry()
    +MarkSuccess()
  }
  class CalendarConstraint {
    +Date DateCheck
    +Boolean IsHoliday
    +Boolean IsLunarFirst
    +CheckEligibility()
  }
  class FeeReport {
    +String AppCode
    +String Branch
    +Date ReportDate
    +String StatusFilter
    +GenerateDetailed()
    +GenerateSummary()
    +GenerateInsufficientFunds()
  }

  RawFeeRecord "1" --> "1" ProcessedFeeTask : Ingest & Apply Params
  ProcessedFeeTask "*" --> "1" CalendarConstraint : Validate BEFORE Core
  FeeReport ..> ProcessedFeeTask : Read from Replica
```

## 2. Attribute Details
- `ProcessedFeeTask`: Entity cốt lõi lưu trữ trạng thái xử lý trung gian, số lần retry, loại phí và ngày phải thu (có thể thay đổi khi dời lịch).
- `CalendarConstraint`: Object đảm bảo quy tắc nghiệp vụ giới hạn lịch trình thời gian thu phí.

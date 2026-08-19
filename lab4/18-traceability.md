# 18. Traceability Matrix

Ma trận truy vết từ Yêu cầu (US) -> Kiến trúc (Container) -> Business Rules -> Kịch bản Kiểm thử (Test Cases).

| User Story | Thành phần Kiến trúc | Business Rule (BR) | Lớp Unit Test tương ứng |
|---|---|---|---|
| **US-01:** Nhận ds & lọc phí | Ingestion Service | BR-01 (Lọc phí > 0) | `testBR01_ShouldOnlyProcessFeeGreaterThanZero()` |
| **US-02:** Kiểm tra lịch âm/lễ | Calendar Gate | BR-02 (Không chạy Lễ) | `testBR02_ShouldHaltExecutionOnLunarFirstOrHoliday()` |
| **US-03:** Trích nợ Core | Execution Engine | N/A | (Tích hợp luồng xử lý chính) |
| **US-04:** AutoRetry 10 lần | Retry Scheduler | BR-03 (Retry <= 10) | `testBR03_ShouldIncrementRetryAndHaltAt10()` |
| **US-05:** Gửi SMS | Execution Engine | BR-04 (Gửi SMS ngay) | `testBR04_ShouldSendSmsImmediatelyOnSuccess()` |
| **US-06:** Tra cứu UI | Web/App UI Portal | BR-05 (Read Replica) | (Tích hợp QA/UI Testing) |

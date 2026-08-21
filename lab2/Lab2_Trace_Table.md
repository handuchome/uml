# Lab 2: Trace Table

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 2

*Rule: Requirement ID -> Process Step -> CON.* -> Named object/state.*

| Requirement ID | Process Step (I-5) | CON.* (I-10) | Named Object / State (I-6) |
|---|---|---|---|
| REQ-01 | 1 & 2 (Tiếp nhận & Tính toán) | CON.1 (Phí > 0) | `ProcessedFeeTask` / `Created` |
| REQ-02 | 3 (Kiểm tra lịch qua Calendar Gate) | CON.2 (Chặn lịch) | `ProcessedFeeTask` / `Pending_Calendar` -> `Rescheduled` |
| REQ-03 | 4 (Gửi lệnh trích nợ Core Banking) | N/A | `ProcessedFeeTask` / `Pending_Execution` -> `Completed` |
| REQ-04 | 4 (Loop / Xử lý lỗi từ Core Banking) | CON.3 (AutoRetry Max 10) | `ProcessedFeeTask` / `Retrying` -> `Failed_Permanently` |
| REQ-05 | 5 (Kích hoạt Notification Service) | CON.4 (Bắt buộc gửi SMS) | `ProcessedFeeTask` / `Completed` |
| REQ-06 | 5 (Đồng bộ Report Database để tra cứu) | CON.5 (Read/Write Split) | `FeeReport` / N/A |

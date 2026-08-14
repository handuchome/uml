# Quality gates — Design

Reviewer checklist for a **logical / solution design** pack for the Bank Service Fee Collection System.

**Source of truth.** [Domain.md](Domain.md), [Requirements.md](Requirements.md), [Analysis.md](Analysis.md).

## Required contents

| # | Section / artifact | Must show |
|---|---|---|
| D1 | Scope | Pointers to Domain, in-scope US-01…US-06. Đề cập rõ Digibank, Thẻ, IB TC. |
| D2 | Domain / class design | Bổ sung `CalendarConstraint` / bảng cấu hình ngày lễ. Thêm trường `LoaiPhi` vào `ProcessedFeeTask`. |
| D3 | Sequence — Calendar Check | Sequence bắt buộc có bước gọi API/DB kiểm tra ngày (IsLunarFirst, IsHoliday) TRƯỚC khi gọi Core. Nếu True -> Halt/Reschedule. |
| D4 | Sequence — Execution | US-03/05: Engine đọc Task → Gửi Core → OK → Kích hoạt SMS. |
| D5 | Sequence — AutoRetry | Core fail (Insufficient funds) → Tăng `RetryCount` +1 → Kiểm tra `< 10`. |
| D6 | UI Wireframe / Flow | Cần có bản phác thảo hoặc luồng luân chuyển của 1 màn hình tra cứu chứa 3 loại báo cáo (US-06). |
| D7 | BR evidence table | Khớp BR-01 đến BR-05 (Đặc biệt BR-02 chặn ngày). |

## Automatic Fail (anti-patterns)

- Sequence Diagram thiếu cụm kiểm tra Lịch (Holiday/Lunar 1st check).
- Màn hình tra cứu (UI) truy vấn trực tiếp vào Core Banking thay vì DB nội bộ của hệ thống thu phí.

## BR evidence table

| BR | Rule (short) | Evidence (diagram / section name) |
|---|---|---|
| BR-01 | Kiểm tra Params, chỉ thu nếu > 0 | Sequence - Ingestion |
| BR-02 | Chặn mùng 1 Âm lịch / Lễ | Sequence - Calendar Check |
| BR-03 | Lỗi số dư kích hoạt Retry | Sequence - AutoRetry |
| BR-04 | Thu thành công gửi SMS | Sequence - Execution |
| BR-05 | Có màn hình tra cứu | UI Diagram / Sequence - Report Query |

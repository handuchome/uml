# Quality gates — Design

Reviewer checklist for a **logical / solution design** pack for the Bank Service Fee Collection System.

**Source of truth.** [Domain.md](Domain.md), [Requirements.md](Requirements.md), [Analysis.md](Analysis.md).

## Required contents

| # | Section / artifact | Must show |
|---|---|---|
| D1 | Scope | Pointers to [Domain.md](Domain.md) - In/Out Scope. In-scope US-01…US-06. Đề cập rõ Digibank, Thẻ, IB TC. |
| D2 | Domain / class design | `RawFeeRecord`, `ProcessedFeeTask` (+ `LoaiPhi`, `RetryCount`), `CalendarConstraint`, `FeeReport`. |
| D3 | Sequence — Ingestion | US-01: Nhận danh sách → Kiểm tra `SoTienPhi > 0` (BR-01) → Tạo `ProcessedFeeTask`. |
| D4 | Sequence — Calendar Check | US-02: Kiểm tra `IsLunarFirst` hoặc `IsHoliday` từ API/DB TRƯỚC khi gọi Core (BR-02 TUYỆT ĐỐI). Nếu Yes -> Halt/Reschedule sang ngày làm việc tiếp. |
| D5 | Sequence — Execution | US-03/05: Engine đọc Task → Gửi Core → Thành công → Kích hoạt SMS ngay (BR-04). |
| D6 | Sequence — AutoRetry | US-04: Core fail (Insufficient funds) → Tăng `RetryCount` +1 → Kiểm tra `RetryCount < 10` (BR-03). |
| D7 | UI Wireframe / Flow | US-06: Màn hình tra cứu với 3 loại báo cáo (Chi tiết, Tổng hợp, Không đủ số dư). Bộ lọc: AppCode, Chi nhánh, Ngày, Trạng thái. |
| D8 | BR evidence table | Khớp BR-01 đến BR-05 với diagram tương ứng. |

## Automatic Fail (anti-patterns)

- Sequence Diagram thiếu cụm kiểm tra Lịch (Holiday/Lunar 1st check) TRƯỚC Core Banking call (Vi phạm BR-02, US-02).
- Màn hình tra cứu (UI) truy vấn trực tiếp vào Core Banking thay vì DB nội bộ của hệ thống thu phí (Vi phạm A5 - Read/Write Split).
- AutoRetry không có giới hạn ≤ 10 lần hoặc không kiểm tra `RetryCount` (Vi phạm BR-03).
- SMS không được gửi ngay khi thu thành công (Vi phạm BR-04, US-05).
- Thiếu field `LoaiPhi` trong `ProcessedFeeTask` class design (Vi phạm D2).
- Xử lý hoàn phí (Refund) hoặc hạch toán trong design (Vi phạm Out of Scope).

## BR evidence table

| BR | Rule (short) | Evidence (diagram / section name) | Priority |
|---|---|---|---|
| BR-01 | Kiểm tra Params, chỉ thu nếu > 0 | Sequence - Ingestion (US-01) | Must |
| BR-02 | Chặn mùng 1 Âm lịch / Lễ (TUYỆT ĐỐI) | Sequence - Calendar Check (US-02) | **Critical** |
| BR-03 | Lỗi số dư kích hoạt Retry ≤ 10 | Sequence - AutoRetry (US-04) | Must |
| BR-04 | Thu thành công gửi SMS ngay | Sequence - Execution (US-05) | Must |
| BR-05 | Có màn hình tra cứu 3 báo cáo | UI Diagram / Sequence - Report (US-06) | Must |

---

## Out of Scope (Không xử lý trong design)

Như định nghĩa trong [Domain.md](Domain.md#2-out-of-scope):
- Hạch toán kế toán tổng hợp
- Thu phí tiền mặt tại quầy
- Hoàn phí (Refund)
- Tạo/Quản lý tham số miễn giảm
- Phân quyền user phức tạp

# Quality gates — Architecture

Reviewer checklist for an **architecture** pack for the Bank Service Fee Collection System.

**Source of truth.** [Domain.md](Domain.md), [Requirements.md](Requirements.md), [Analysis.md](Analysis.md).

## Required contents

| # | Section / artifact | Must show |
|---|---|---|
| A1 | System context (C4 L1) | Thêm 3 nguồn dữ liệu: Digibank, Thẻ, IB TC. Thêm hệ thống/API Calendar (Lịch Âm/Lễ). **Out of scope**: Hạch toán, thu tiền mặt, tạo Params. |
| A2 | Container view (C4 L2) | **Bắt buộc** có Container cho Web/App UI (Màn hình tra cứu 3 báo cáo - US-06). |
| A3 | Calendar Gate | Logic check mùng 1 Âm lịch và nghỉ lễ phải là một Component/Gate đứng TRƯỚC Fee Execution Engine (BR-02 TUYỆT ĐỐI KHÔNG). |
| A4 | Scheduler / Batch | Có cơ chế lập lịch rõ ràng cho AutoRetry (Max 10 lần - BR-03) và xử lý dời lịch (Reschedule) từ ngày lễ. |
| A5 | Read/Write Split | UI Server query từ Read Store (Báo cáo), độc lập với luồng trích nợ Core Banking. |
| A6 | SMS Gateway | Component gửi SMS ngay khi thu thành công (BR-04 - US-05). |
| A7 | Open assumptions | Bổ sung OA-01 (Out of scope), OA-05 (cơ chế dời lịch) và OA-06 (nguồn Calendar). |

## Automatic Fail (anti-patterns)

- **Hardcode** logic tính ngày Âm lịch / Nghỉ lễ trực tiếp trong mã nguồn thay vì dùng DB/Cấu hình hoặc API chuẩn (Vi phạm BR-02).
- Gửi lệnh sang Core Banking rồi mới nhờ Core check xem hôm nay có phải ngày lễ không (Vi phạm Domain: Hệ thống này phải tự chặn).
- Không có container UI cho Bank Staff (Vi phạm US-06).
- AutoRetry logic không giới hạn ≤ 10 lần (Vi phạm BR-03).
- Khách hàng thu thành công nhưng không gửi SMS (Vi phạm BR-04).
- Xử lý hoàn phí, hạch toán kế toán, hay tạo tham số miễn giảm trong scope (Vi phạm Out of Scope).

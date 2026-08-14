# Quality gates — Architecture

Reviewer checklist for an **architecture** pack for the Bank Service Fee Collection System.

**Source of truth.** [Domain.md](Domain.md), [Requirements.md](Requirements.md), [Analysis.md](Analysis.md).

## Required contents

| # | Section / artifact | Must show |
|---|---|---|
| A1 | System context (C4 L1) | Thêm nguồn dữ liệu Thẻ, IB TC, Digibank. Thêm hệ thống/API cung cấp Lịch (Calendar). |
| A2 | Container view (C4 L2) | **Bắt buộc** có Container cho Web/App UI (Màn hình tra cứu). |
| A3 | Calendar Gate | Logic check mùng 1 Âm lịch và nghỉ lễ phải là một Component/Gate đứng TRƯỚC Fee Execution Engine. |
| A4 | Scheduler / Batch | Có cơ chế lập lịch rõ ràng cho AutoRetry và xử lý dời lịch (Reschedule) từ ngày lễ. |
| A5 | Read/Write Split | UI Server query từ Read Store (Báo cáo), độc lập với luồng trích nợ Core. |
| A6 | Open assumptions | Bổ sung OA-05 (cơ chế dời lịch) và OA-06 (nguồn Calendar). |

## Automatic Fail (anti-patterns)

- **Hardcode** logic tính ngày Âm lịch / Nghỉ lễ trực tiếp trong mã nguồn thay vì dùng DB/Cấu hình hoặc API chuẩn.
- Gửi lệnh sang Core Banking rồi mới nhờ Core check xem hôm nay có phải ngày lễ không (Vi phạm Domain: Hệ thống này phải tự chặn).
- Không có container UI cho Bank Staff.

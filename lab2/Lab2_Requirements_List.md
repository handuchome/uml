# Lab 2: Requirements List

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 2

*Note: Each requirement traces to Goal, a CON.*, a process step, or a state.*

| Req ID | Requirement Description (from User Stories) | Trace: Goal / Outcome | Trace: Process Step | Trace: CON.* | Trace: State |
|---|---|---|---|---|---|
| REQ-01 | Hệ thống tiếp nhận danh sách thu phí từ Source System Digibank, Source System Card, và Source System IB TC. Tính toán và chỉ tạo task khi phí > 0. (US-01) | Goal: Centralize and automate fee collection | Step 1 & Step 2 | CON.1 (Phí > 0) | Created |
| REQ-02 | Hệ thống phải kiểm tra lịch thu phí trước khi gọi Core Banking. Nếu rơi vào mùng 1 Âm lịch hoặc Nghỉ lễ, lô thu phí phải bị chặn và dời lịch. (US-02) | Outcome: 100% compliance with holiday/lunar constraints | Step 3 | CON.2 (Chặn lịch) | Pending_Calendar, Rescheduled |
| REQ-03 | Thực thi trích nợ thông qua Core Banking đối với các khoản phí đã vượt qua bài kiểm tra lịch. (US-03) | Goal: Centralize and automate fee collection | Step 4 | N/A | Pending_Execution, Completed |
| REQ-04 | Tự động thử lại (AutoRetry) tối đa 10 lần đối với các giao dịch trích nợ thất bại do lỗi không đủ số dư. (US-04) | Outcome: Zero manual retry effort for insufficient funds | Step 4 (Loop) | CON.3 (AutoRetry Max 10) | Retrying, Failed_Permanently |
| REQ-05 | Kích hoạt gửi SMS cho khách hàng ngay lập tức khi nhận được kết quả thu phí thành công từ Core Banking. (US-05) | Goal: Centralize and automate fee collection | Step 5 | CON.4 (Bắt buộc gửi SMS) | Completed |
| REQ-06 | Cung cấp màn hình UI (Fee Inquiry Web App) cho Bank Staff tra cứu 3 loại báo cáo (Chi tiết, Tổng hợp, Lỗi số dư). (US-06) | Baseline -> Target: CQRS reporting | Step 5 (Sync) | CON.5 (Read/Write Split) | N/A (Read operations) |

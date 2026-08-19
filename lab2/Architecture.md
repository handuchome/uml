# Architecture Design - Bank Service Fee Collection System

**Source of truth:** [Domain.md](Domain.md), [Requirements.md](Requirements.md), [Analysis.md](Analysis.md)

## A1. System Context (C4 Level 1)
Scope: Thu thập danh sách phí từ Digibank, Thẻ, IB TC. Tích hợp Calendar API để chặn lịch Âm/Lễ. 
*Out of scope: Hạch toán kế toán, thu tiền mặt, tạo tham số miễn giảm, hoàn phí (Refund).*

```mermaid
C4Context
  title System Context - Bank Service Fee Collection System

  Person(staff, "Bank Staff", "Sử dụng hệ thống để tra cứu báo cáo (US-06)")
  System(feeSys, "Fee Collection System", "Hệ thống trung tâm xử lý thu phí dịch vụ tự động")

  System_Ext(digibank, "Digibank", "Nguồn dữ liệu (AppCode: DIGIBANK)")
  System_Ext(card, "Hệ thống Thẻ", "Nguồn dữ liệu (AppCode: CARD)")
  System_Ext(ibtc, "IB TC", "Nguồn dữ liệu (AppCode: IBTC)")
  System_Ext(params, "Hệ thống Params", "Cấu hình miễn giảm phí gốc")
  System_Ext(calendar, "Calendar API", "Cung cấp thông tin lịch Âm / Nghỉ lễ quốc gia")
  System_Ext(core, "Core Banking", "Quản lý tài khoản & Thực thi trích nợ")
  System_Ext(sms, "SMS Gateway", "Hệ thống gửi tin nhắn cho khách hàng")

  Rel(digibank, feeSys, "Gửi danh sách thu (US-01)")
  Rel(card, feeSys, "Gửi danh sách thu (US-01)")
  Rel(ibtc, feeSys, "Gửi danh sách thu (US-01)")

  Rel(feeSys, params, "Đồng bộ/Kiểm tra Params miễn giảm")
  Rel(feeSys, calendar, "Tra cứu mùng 1 Âm & Ngày lễ (BR-02)")
  Rel(feeSys, core, "Gửi lệnh trích nợ tài khoản (US-03)")
  Rel(feeSys, sms, "Gửi SMS ngay khi thu thành công (BR-04)")

  Rel(staff, feeSys, "Truy cập màn hình tra cứu")
```

## A2 & A5. Container View (C4 Level 2) & Read/Write Split
Kiến trúc áp dụng **Read/Write Split (CQRS pattern)**: Màn hình UI của Bank Staff tuyệt đối không query trực tiếp vào Core Banking hay Primary DB (tránh lock DB khi hệ thống đang cày batch trích nợ), mà đọc từ Report Read DB riêng biệt.

```mermaid
C4Container
  title Container View - Fee Collection System

  Person(staff, "Bank Staff", "Bank Staff")
  System_Ext(sources, "Digibank, Thẻ, IB TC", "Các hệ thống nguồn")
  System_Ext(core, "Core Banking", "Hệ thống Core")
  System_Ext(calendar, "Calendar API", "Dịch vụ Lịch")
  System_Ext(sms, "SMS Gateway", "Dịch vụ SMS")

  Boundary(system, "Fee Collection System") {
    Container(api, "Ingestion Service", "Java/Spring Boot", "Tiếp nhận & Lọc phí > 0 (BR-01)")
    Container(gate, "Calendar Gate", "Component", "Kiểm tra Mùng 1 Âm/Lễ TRƯỚC KHI trích nợ (BR-02)")
    Container(engine, "Execution Engine", "Java/Go", "Xử lý trích nợ, gọi Core & SMS")
    Container(retry, "Scheduler / Batch", "Quartz/Cron", "Quản lý AutoRetry <=10 & Reschedule")
    Container(ui, "Web/App UI Portal", "React/Angular", "Màn hình tra cứu 3 báo cáo (US-06)")
    
    ContainerDb(db_write, "Primary DB", "PostgreSQL", "Lưu trữ Task và Trạng thái (Write-heavy)")
    ContainerDb(db_read, "Report DB", "PostgreSQL/Elastic", "Read Replica phục vụ UI (Read-heavy)")
  }

  Rel(sources, api, "Đẩy file/API danh sách")
  Rel(api, db_write, "Lưu Raw/Processed Task")
  
  Rel(engine, gate, "Validate ngày trước khi chạy")
  Rel(gate, calendar, "Query Lịch qua API")
  
  Rel(engine, core, "Trích nợ Core")
  Rel(engine, sms, "Trigger SMS ngay lập tức")
  Rel(engine, db_write, "Cập nhật Status/Retry")
  
  Rel(retry, db_write, "Quét lỗi số dư (RetryCount < 10)")
  Rel(retry, engine, "Requeue/Push tasks")
  
  Rel(db_write, db_read, "Data Sync (CDC / Async)")
  Rel(ui, db_read, "Tra cứu dữ liệu (Chi tiết, Tổng hợp, Lỗi)")
  Rel(staff, ui, "Tương tác bộ lọc")
```

## A3. Calendar Gate
- **Vai trò:** Hoạt động như một chốt chặn (Circuit Breaker logic) đặt **TRƯỚC** Fee Execution Engine.
- **Quy tắc tuyệt đối (BR-02):** Engine phải đi qua Calendar Gate. Gate sẽ kiểm tra xem ngày hệ thống hiện tại có phải là mùng 1 Âm lịch hoặc nghỉ lễ không bằng cách gọi `Calendar API`.
- **Nếu YES:** Ngăn chặn ngay lập tức, đổi trạng thái lô thu sang `Rescheduled` sang ngày làm việc tiếp theo. Core Banking tuyệt đối không nhận được request nào trong ngày này.
- **Chống Anti-pattern:** Logic Âm lịch KHÔNG bị hardcode mà phụ thuộc vào Master Data hoặc External Calendar API.

## A4. Scheduler / Batch (AutoRetry)
- **Cơ chế (BR-03 & US-04):** Job Scheduler định kỳ quét các `ProcessedFeeTask` có trạng thái `INSUFFICIENT_FUNDS`.
- Nếu `RetryCount < 10`, Batch sẽ đẩy task trở lại Queue cho Execution Engine xử lý.
- Nếu `RetryCount >= 10`, Task bị đánh dấu là `PERMANENT_FAIL` và bỏ qua (chỉ hiển thị lên UI báo cáo).
- Lập lịch dời ngày (Reschedule): Nếu Calendar Gate báo lỗi Lễ, Scheduler tự động đẩy `NgayPhaiThu` sang `NgayPhaiThu + 1 working day`.

## A6. SMS Gateway Integration
- **Cơ chế (BR-04 & US-05):** Execution Engine được liên kết trực tiếp (Synchronous hoặc High-priority Asynchronous) với SMS Gateway.
- Ngay khi Core Banking trả về `Success` (Đã trừ tiền), Engine gọi ngay hàm `SendSMS()` rồi mới đóng Task. Đảm bảo trải nghiệm tức thời cho khách hàng.

## A7. Open Assumptions
| ID | Topic | Quyết định trong Kiến trúc này |
|---|---|---|
| **OA-01** | Phạm vi (Scope Out) | Không có module Hạch toán, Không tích hợp hệ thống Thu tiền mặt, Không có module Hoàn phí (Refund UI). |
| **OA-05** | Cơ chế dời lịch (Reschedule) | Thiết kế `Scheduler / Batch` xử lý dời sang **ngày làm việc tiếp theo** thay vì cộng dồn vào tháng sau. |
| **OA-06** | Nguồn dữ liệu Lịch | Dùng **Calendar API** nội bộ hiện có của ngân hàng làm System External (Không tự build bảng mapping ngày Âm lịch để tránh sai lệch rủi ro). |

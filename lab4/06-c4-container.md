# 06. C4 Container Diagram

## 1. Diagram
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
    
    ContainerDb(db_write, "Primary DB", "PostgreSQL", "Lưu trữ Task và Trạng thái")
    ContainerDb(db_read, "Report DB", "PostgreSQL/Elastic", "Read Replica phục vụ UI")
  }

  Rel(sources, api, "Đẩy file/API danh sách")
  Rel(api, db_write, "Lưu Raw/Processed Task")
  
  Rel(engine, gate, "Validate ngày trước khi chạy")
  Rel(gate, calendar, "Query Lịch qua API")
  
  Rel(engine, core, "Trích nợ Core")
  Rel(engine, sms, "Trigger SMS ngay lập tức")
  Rel(engine, db_write, "Cập nhật Status/Retry")
  
  Rel(retry, db_write, "Quét lỗi số dư")
  Rel(retry, engine, "Requeue/Push tasks")
  
  Rel(db_write, db_read, "Data Sync (CDC / Async)")
  Rel(ui, db_read, "Tra cứu dữ liệu")
  Rel(staff, ui, "Tương tác bộ lọc")
```

## 2. Component Highlights
Áp dụng **Read/Write Split (CQRS pattern)**: Web/App UI Portal query từ Report Read DB riêng biệt, đảm bảo không khóa bảng khi luồng trích nợ đang cày batch.

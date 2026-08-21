# Lab 2: Analysis

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 2

## 1. As-is vs To-be

| Aspect | As-is (Baseline) | To-be (Target) |
|---|---|---|
| **Data Ingestion** | Phân mảnh, xử lý thủ công từng mảng riêng biệt (Digibank, Thẻ, IB TC). | Tập trung qua Fee Ingestion Service (Centralize fee collection). |
| **Calendar Check** | Thiếu cơ chế kiểm tra lịch tập trung, rủi ro vi phạm quy định (thu nhầm ngày lễ). | Tự động hóa 100% (100% compliance) qua Calendar Gate, tích hợp Calendar Service. |
| **Exception Handling** | Xử lý lỗi số dư thủ công, tốn nguồn lực vận hành (Manual retry effort). | Zero manual retry effort, tự động chạy lại qua Retry Scheduler (Max 10 lần). |
| **Reporting / Inquiry** | Truy vấn trực tiếp vào Database chính, gây nghẽn cổ chai luồng giao dịch. | Tách biệt luồng Đọc/Ghi (Read/Write Split - CQRS), tối ưu hiệu năng cho Fee Inquiry Web App. |

## 2. Capabilities implied by the goal

Dựa trên Goal *"Centralize and automate fee collection across multiple banking channels with strict calendar constraints and retry mechanisms"*, hệ thống yêu cầu các năng lực cốt lõi sau:
- **Năng lực tích hợp đa kênh (Multi-channel Integration):** Chuẩn hóa dữ liệu đầu vào từ nhiều Source System khác nhau.
- **Năng lực kiểm soát quy tắc nghiệp vụ (Rule Engine / Filtering):** Loại trừ các khoản phí <= 0 và kiểm tra theo danh sách từ Params System.
- **Năng lực nhận diện thời gian thực (Time-awareness / Calendar Gate):** Đánh giá động ngày hiện tại với Lịch Âm/Nghỉ lễ.
- **Năng lực lập lịch linh hoạt (Scheduler):** Tạm dừng, dời lịch (Reschedule) và lặp lại giao dịch (AutoRetry) một cách độc lập và tự động.
- **Năng lực đồng bộ bất đồng bộ (Asynchronous Syncing):** Cập nhật dữ liệu từ Fee Database sang Report Database và kích hoạt Notification Service mà không block luồng chính.

## 3. Exception paths named

- **Path 1: Fee Discard** (Phí không hợp lệ) 
  - Trigger: Kết quả lọc `SoTienPhi <= 0`. 
  - Action: Bỏ qua (Discard), không tạo `ProcessedFeeTask`.
- **Path 2: Calendar Block** (Vi phạm lịch) 
  - Trigger: Rơi vào Mùng 1 Âm lịch hoặc Nghỉ lễ. 
  - Action: Task `ProcessedFeeTask` chuyển trạng thái từ `Pending_Calendar` sang `Rescheduled`. Chờ đến ngày làm việc tiếp theo.
- **Path 3: Insufficient Funds** (Không đủ số dư) 
  - Trigger: Lỗi trả về từ Core Banking. 
  - Action: Task chuyển từ `Pending_Execution` sang `Retrying`. Retry Scheduler sẽ pick up và thử lại.
- **Path 4: Max Retries Exceeded** (Vượt quá giới hạn Retry) 
  - Trigger: Lỗi không đủ số dư lặp lại và `RetryCount` đạt mốc 10. 
  - Action: Task chuyển sang `Failed_Permanently` (Trạng thái Terminal).

# Bank Service Fee Collection System (Fee Collection Hub)

## 📌 Giới thiệu dự án
Đây là dự án Capstone thiết kế và phát triển **Hệ thống thu phí dịch vụ ngân hàng (Fee Collection Hub)**. Hệ thống được xây dựng dựa trên nguyên tắc Domain-Driven Design (DDD), phân rã kiến trúc L3, áp dụng CQRS, và mô phỏng các tương tác với hệ thống Core Banking.

Mặc dù kiến trúc thực tế là các Microservices phân tán, dự án này đã áp dụng chiến thuật "Collapse Architecture" (gộp hệ thống) thành một tiến trình FastAPI duy nhất (In-process) kết hợp cùng In-memory Message Broker và Database ảo để tối ưu hóa việc chạy giả lập và kiểm thử tự động.

## 👥 Nhóm phát triển (Team 1)
- **Nguyễn Nhật Trường (TN)**
- **Hà Ngọc Bắc (SA - Kỹ sư trưởng):** Phụ trách kiến trúc hệ thống, kiểm duyệt và chốt ký (Sign-off).
- **Dương Đỗ Minh (Dev):** Phụ trách lập trình, phát triển mã nguồn và đảm bảo tiêu chuẩn Code Quality.
- **Hàn Ngọc Đức (Test):** Phụ trách kiểm thử tự động, đảm bảo Test Coverage.

## 🏗️ Kiến trúc & Thiết kế
- **Cấu trúc Collapse:** Chạy toàn bộ trên 1 process FastAPI.
- **Xử lý nghiệp vụ:** 
  - `Fee Ingestion Service`: Tiếp nhận yêu cầu thu phí.
  - `Calendar Gate`: Cổng chặn ngày nghỉ/lễ (Không thực hiện giao dịch vào ngày lễ).
  - `Execution Engine`: Xử lý giao dịch, tương tác với Core Banking và gửi SMS.
  - `Retry Scheduler`: Tự động thử lại các giao dịch thất bại do không đủ số dư (tối đa 10 lần).
- **CQRS:** Phân tách luồng Đọc/Ghi qua `FeeReportAPI` và `ReportProjector`.
- **Mocks:** Tích hợp các hệ thống giả lập `MockCoreBanking`, `MockCalendarService`, `MockSMSGateway`.

## 🏆 Kết quả đạt được
- **Bảo vệ thành công Hard Rules:** Vượt qua toàn bộ các ràng buộc ngặt nghèo của hệ thống giám khảo (I-5, I-9).
- **100% Test Pass:** 10/10 kịch bản kiểm thử tự động đều Pass thành công.
- **Điểm số Capstone:** Hoàn thành xuất sắc với số điểm **9.0 / 10** từ hệ thống chấm điểm tự động. Lịch sử Git chuẩn mực, tách bạch rõ vai trò của Dev và SA.

## 🚀 Cách chạy dự án
```bash
# Cài đặt thư viện
pip install -r capstone/requirements.txt

# Chạy kiểm thử tự động
pytest capstone/test_capstone.py -v
```

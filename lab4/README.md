# Bank Service Fee Collection System

## 1. System Overview
Hệ thống xử lý tập trung việc thu các loại phí dịch vụ từ tài khoản khách hàng. Hệ thống nhận dữ liệu gốc từ nhiều nguồn, đối chiếu với các chính sách miễn giảm, kiểm tra lịch thu phí (loại trừ mùng 1 Âm lịch và nghỉ lễ), thực hiện trích nợ tự động qua Core Banking, gửi thông báo và cung cấp màn hình tra cứu đối soát.

## 2. In Scope
- Tiếp nhận danh sách từ 3 mảng (Digibank, Thẻ, IB TC)
- Lọc danh sách miễn giảm (chỉ thu nếu Số tiền > 0)
- Kiểm tra lịch thu phí tự động
- Trích nợ Core Banking
- Cơ chế AutoRetry (tối đa 10 lần)
- Thông báo SMS
- Màn hình tra cứu (UI)

## 3. Out of Scope
- Hạch toán kế toán tổng hợp
- Thu phí tiền mặt tại quầy
- Hoàn phí (Refund)
- Tạo/Quản lý tham số miễn giảm
- Phân quyền user phức tạp

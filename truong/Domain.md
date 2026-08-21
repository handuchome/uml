# Domain:
Hệ thống Thu các loại phí dịch vụ cho Ngân hàng (Bank Service Fee Collection System)

## Hệ thống Thu các loại phí dịch vụ
**Mô tả.** Hệ thống xử lý tập trung việc thu các loại phí dịch vụ từ tài khoản khách hàng. Hệ thống nhận dữ liệu gốc từ nhiều nguồn (AppCode), đối chiếu với các chính sách miễn giảm, thực hiện trích nợ tự động qua Core Banking, gửi thông báo và cung cấp các báo cáo đối soát.

**Ranh giới hệ thống (In / out boundary).** In: Tiếp nhận danh sách cần thu phí, xử lý logic miễn giảm, thực thi trích nợ tự động (bao gồm cơ chế AutoRetry), gửi tin nhắn thông báo, xuất báo cáo. Out: Quá trình hạch toán kế toán tổng hợp, thu phí tiền mặt tại quầy, quy trình hoàn phí (refund), tạo và quản lý tham số miễn giảm trên hệ thống Params gốc (hệ thống này chỉ đọc Params).

**Tác nhân và hệ thống.** Hệ thống nguồn (cung cấp danh sách phí); Hệ thống Params (cung cấp danh sách miễn giảm); Core Banking (thực hiện trích nợ); SMS Gateway (gửi tin nhắn); Người dùng nội bộ (tra cứu báo cáo).

**Luồng cơ bản (Happy path).** Hệ thống nguồn gửi danh sách → Lọc danh sách được miễn giảm → Tạo danh sách phải thu (số tiền > 0) → Gửi lệnh trích nợ vào Core Banking → Thành công → Gửi SMS cho khách hàng → Cập nhật báo cáo tra cứu chi tiết và tổng hợp.

**Ngoại lệ (Edge cases).** Khách hàng không đủ số dư → Chuyển trạng thái sang AutoRetry (tối đa 10 lần) → Lên danh sách Báo cáo không đủ số dư trả nợ phí.

# Scope:
- Quản lý danh sách đầu vào và miễn giảm
- Thực thi thu phí và AutoRetry
- Thông báo và Báo cáo

## Quản lý danh sách đầu vào và miễn giảm
**Mô tả.** Quá trình tổng hợp dữ liệu thô từ các hệ thống dịch vụ (AppCode) và tính toán số tiền phí thực tế phải thu sau khi áp dụng chính sách miễn giảm.

**In / out boundary.** In: Danh sách thô (Ngày, AppCode, Mã KH, SĐT, STK, Số tiền), tham số miễn giảm, logic loại trừ để ra danh sách số tiền > 0. Out: Giao diện cấu hình chính sách miễn giảm.

**Tại sao quan trọng đối với mô hình.** Phải tách biệt rõ dữ liệu `Danh sách cần thu` (raw) và `Danh sách phải thu` (processed). Logic này phải chạy trước khi bất kỳ giao dịch trích nợ nào được gửi tới Core Banking.

## Thực thi thu phí và AutoRetry
**Mô tả.** Giao tiếp với Core Banking để trích tiền từ số tài khoản (STK) của khách hàng và cơ chế tự động thử lại khi tài khoản không đủ tiền.

**In / out boundary.** In: Danh sách phải thu, gọi API Core Banking, bắt lỗi số dư, đếm số lần Retry (tối đa 10 lần). Out: Xử lý khóa tài khoản, xử lý nợ quá hạn phức tạp ngoài phạm vi thu phí dịch vụ.

**Ngoại lệ.** Tài khoản đóng, tài khoản bị phong tỏa: Dừng thu phí ngay lập tức (không đưa vào vòng lặp Retry nếu lỗi không phải do số dư). Lỗi số dư: Chạy AutoRetry.

## Thông báo và Báo cáo
**Mô tả.** Giao tiếp khách hàng (SMS) và cung cấp góc nhìn (Read Model) cho người dùng nội bộ để đối soát.

**In / out boundary.** In: Kích hoạt SMS khi giao dịch thành công. Báo cáo Chi tiết, Tổng hợp, và Báo cáo không đủ số dư. Out: Các kênh thông báo khác (Email, OTT) nếu chưa được chỉ định, báo cáo kế toán GL.

# Architecture implications:
- Tách biệt luồng Xử lý lô (Batch processing) cho việc nhập dữ liệu và Retry khỏi luồng truy vấn (Query) của báo cáo.
- Cần có cơ chế định tuyến và lập lịch (Scheduler) rõ ràng cho luồng AutoRetry 10 lần.
- Dữ liệu `Chi nhánh` cần được làm rõ nguồn gốc (mapping từ Core Banking hoặc Hệ thống nguồn) vì không có trong input thô nhưng xuất hiện trong output.

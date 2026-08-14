# Domain:
Hệ thống Thu các loại phí dịch vụ cho Ngân hàng (Bank Service Fee Collection System)

## Hệ thống Thu các loại phí dịch vụ
**Mô tả.** Hệ thống xử lý tập trung việc thu các loại phí dịch vụ từ tài khoản khách hàng. Hệ thống nhận dữ liệu gốc từ nhiều nguồn, đối chiếu với các chính sách miễn giảm, kiểm tra lịch thu phí (loại trừ mùng 1 Âm lịch và nghỉ lễ), thực hiện trích nợ tự động qua Core Banking, gửi thông báo và cung cấp màn hình tra cứu đối soát.

**Ranh giới hệ thống (In / out boundary).** In: Tiếp nhận danh sách cần thu phí của 3 mảng (Digibank+SMS, Thẻ, Internet Banking Tổ chức), xử lý logic miễn giảm, kiểm tra lịch quốc gia/âm lịch, thực thi trích nợ tự động (bao gồm AutoRetry), gửi SMS, và màn hình UI tra cứu. Out: Quá trình hạch toán kế toán tổng hợp, thu phí tiền mặt tại quầy, hoàn phí (refund), tạo và quản lý tham số miễn giảm trên hệ thống Params gốc.

**Tác nhân và hệ thống.** Hệ thống nguồn (Digibank, Thẻ, IB TC); Hệ thống Params; Dịch vụ Lịch (Calendar Service - Âm lịch/Nghỉ lễ); Core Banking; SMS Gateway; Người dùng nội bộ (thao tác trên màn hình tra cứu).

**Luồng cơ bản (Happy path).** Nhận danh sách → Lọc danh sách miễn giảm → Tính phí > 0 → **Kiểm tra lịch (pass)** → Gửi lệnh trích nợ vào Core Banking → Thành công → Gửi SMS → Cập nhật báo cáo tra cứu.

**Ngoại lệ (Edge cases).** 
- Rơi vào mùng 1 Âm lịch hoặc Nghỉ lễ → Tạm dừng thu, dời lịch theo quy định.
- Khách hàng không đủ số dư → Chuyển trạng thái sang AutoRetry (tối đa 10 lần).

# Scope:

## 1. In Scope (Nằm trong phạm vi)

| # | Thành phần | Chi tiết |
|---|---|---|
| **1** | Tiếp nhận danh sách từ 3 mảng | Digibank+SMS, Thẻ, IB TC (Internet Banking Tổ chức) |
| **2** | Lọc danh sách miễn giảm | Xử lý logic phí thực tế (chỉ thu nếu Số tiền > 0) |
| **3** | Kiểm tra lịch thu phí tự động | Không thu vào mùng 1 Âm lịch và ngày nghỉ lễ (rule bắt buộc) |
| **4** | Trích nợ Core Banking | Gửi lệnh rút tiền qua Core Banking |
| **5** | Cơ chế AutoRetry | Tự động thử lại tối đa 10 lần (khi lỗi không đủ số dư) |
| **6** | Thông báo SMS | Gửi tin nhắn SMS sau khi thu thành công |
| **7** | Màn hình tra cứu | Build 1 UI dành cho Bank Staff với 3 loại báo cáo: Chi tiết, Tổng hợp, Không đủ số dư |

## 2. Out of Scope (Nằm ngoài phạm vi)

| # | Thành phần | Lý do |
|---|---|---|
| **1** | Hạch toán kế toán tổng hợp | Do kế toán xử lý riêng |
| **2** | Thu phí tiền mặt tại quầy | Nằm ngoài kênh tự động |
| **3** | Hoàn phí (Refund) | Không trong phạm vi hiện tại |
| **4** | Tạo/Quản lý tham số miễn giảm | Quản lý trên hệ thống Params gốc |
| **5** | Phân quyền user phức tạp | Chỉ tập trung vào chức năng tra cứu (quyền cơ bản) |

## 3. Quản lý lịch thu tự động (Calendar constraint)
**Mô tả.** Hệ thống tự động chặn các giao dịch trích nợ tự động nếu thời điểm thực thi rơi vào mùng 1 Âm lịch hoặc các ngày nghỉ lễ theo quy định.
**In / out boundary.** In: Lấy dữ liệu ngày hiện tại, đối chiếu API/Database lịch Âm và lịch nghỉ lễ. Out: Cấu hình ngày nghỉ lễ thủ công (giả định dùng chung nguồn của toàn ngân hàng).

## 4. Màn hình chức năng tra cứu
**Mô tả.** Giao diện UI (Web/App nội bộ) dành cho Bank Staff để tra cứu kết quả thu phí.
**In / out boundary.** In: Màn hình tra cứu với các bộ lọc (AppCode, Chi nhánh, Ngày, Trạng thái), xuất 03 loại báo cáo (Chi tiết, Tổng hợp, Không đủ số dư). Out: Phân quyền user phức tạp (chỉ tập trung vào chức năng tra cứu).

---

## 5. Business Rules (Quy tắc kinh doanh)

| ID | Rule | Chi tiết |
|---|---|---|
| **BR-01** | Khoản thu hợp lệ để xử lý | Chỉ xử lý nếu `Số tiền > 0` sau miễn giảm (US-01) |
| **BR-02** | Ràng buộc lịch (BẮTBUỘC) | **TUYỆT ĐỐI KHÔNG** phát sinh giao dịch vào mùng 1 Âm lịch và ngày Nghỉ lễ (US-02) |
| **BR-03** | AutoRetry cho lỗi số dư | Lỗi "Không đủ số dư" kích hoạt vòng lặp Retry, tối đa 10 lần (US-04) |
| **BR-04** | Thông báo bắt buộc | Thu thành công phải trigger SMS ngay lập tức (US-05) |
| **BR-05** | Tính toàn vẹn dữ liệu | Dữ liệu phải được hiển thị trực quan qua 1 màn hình tra cứu (US-06) |

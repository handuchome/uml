# Requirements

Source of truth: [Domain.md](Domain.md). 

**Domain.** Hệ thống Thu các loại phí dịch vụ cho Ngân hàng.

**In scope.**
| # | Thành phần | Chi tiết |
|---|---|---|
| 1 | Tiếp nhận danh sách từ 3 mảng | Digibank+SMS, Thẻ, IB TC (Internet Banking Tổ chức) |
| 2 | Lọc danh sách miễn giảm | Xử lý logic phí thực tế (chỉ thu nếu Số tiền > 0) |
| 3 | Kiểm tra lịch thu phí tự động | Không thu vào mùng 1 Âm lịch và ngày nghỉ lễ (rule bắt buộc) |
| 4 | Trích nợ Core Banking | Gửi lệnh rút tiền qua Core Banking |
| 5 | Cơ chế AutoRetry | Tự động thử lại tối đa 10 lần (khi lỗi không đủ số dư) |
| 6 | Thông báo SMS | Gửi tin nhắn SMS sau khi thu thành công |
| 7 | Màn hình tra cứu | Build 1 UI dành cho Bank Staff với 3 loại báo cáo: Chi tiết, Tổng hợp, Không đủ số dư |

**Out of scope.**
| # | Thành phần | Lý do |
|---|---|---|
| 1 | Hạch toán kế toán tổng hợp | Do kế toán xử lý riêng |
| 2 | Thu phí tiền mặt tại quầy | Nằm ngoài kênh tự động |
| 3 | Hoàn phí (Refund) | Không trong phạm vi hiện tại |
| 4 | Tạo/Quản lý tham số miễn giảm | Quản lý trên hệ thống Params gốc |
| 5 | Phân quyền user phức tạp | Chỉ tập trung vào chức năng tra cứu (quyền cơ bản) |

---

## Actors

| Actor | Type | Role |
|---|---|---|
| Hệ thống Nguồn | External | Cung cấp danh sách (Digibank, Thẻ, IB TC). |
| Hệ thống Params | External | Cung cấp danh sách miễn giảm. |
| Dịch vụ Lịch (Calendar) | External/Internal | Cung cấp thông tin ngày lễ, ngày mùng 1 Âm lịch. |
| Core Banking | External | Thực hiện trích nợ tài khoản. |
| SMS Gateway | External | Gửi tin nhắn sau khi thu thành công. |
| Bank Staff | Primary | Sử dụng màn hình tra cứu. |

---

## User stories

### US-01 — Tiếp nhận danh sách từ các hệ thống nguồn
Là hệ thống, tôi cần tiếp nhận dữ liệu từ các hệ thống Digibank, hệ thống Thẻ, và hệ thống IB TC, áp dụng chính sách miễn giảm để xác định danh sách phải thu (>0).

### US-02 — Kiểm tra lịch thu phí tự động
Là hệ thống, trước khi gửi lệnh trích nợ, tôi cần kiểm tra ngày hiện tại so với lịch Âm và lịch nghỉ lễ quốc gia để đảm bảo không vi phạm quy tắc thời gian.
**Acceptance criteria**
- Nếu ngày hiện tại là mùng 1 Âm lịch hoặc ngày nghỉ lễ, hệ thống chặn toàn bộ lô thu phí của ngày đó.
- Lô thu phí bị chặn sẽ được dời sang ngày làm việc tiếp theo (theo cấu hình hệ thống).

### US-03 — Thực thi thu phí
Là hệ thống, tôi cần gửi lệnh trích nợ sang Core Banking đối với danh sách phải thu (sau khi qua gate US-02). (Các tiêu chí giữ nguyên như cũ, sinh lỗi số dư chuyển US-04).

### US-04 — Cơ chế AutoRetry
Là hệ thống, tôi tự động thử thu lại các khoản phí lỗi số dư tối đa 10 lần.

### US-05 — Thông báo sau khi thu
Là hệ thống, tôi gửi SMS cho khách hàng ngay khi thu phí thành công.

### US-06 — Màn hình tra cứu tổng hợp
Là nhân viên ngân hàng, tôi được cung cấp 1 màn hình UI để tra cứu chi tiết giao dịch, tổng hợp theo chi nhánh, và danh sách không đủ số dư.

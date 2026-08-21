# Test Plan — Hệ thống Thu các loại phí dịch vụ cho Ngân hàng

Nguồn tham chiếu: `Domain.md`, `Requirements.md`, `Quality-Gates.md`

---

## 1. Mục tiêu (Objective)

Xác minh hệ thống thu phí dịch vụ xử lý đúng: (1) lọc miễn giảm, (2) trích nợ qua Core Banking, (3) cơ chế AutoRetry tối đa 10 lần, (4) gửi SMS đúng đối tượng, (5) 3 loại báo cáo chính xác và khớp số liệu với nhau — trước khi release lên production.

## 2. Phạm vi kiểm thử (Test Scope)

**Trong phạm vi:**
- Tiếp nhận danh sách thu phí & danh sách miễn giảm (US-01)
- Trích nợ Core Banking (US-02)
- AutoRetry 10 lần (US-03)
- Gửi SMS (US-04)
- 3 báo cáo: Chi tiết, Tổng hợp, Không đủ số dư (US-05, US-06, US-07)
- Đối soát dữ liệu end-to-end
- Kiểm thử tách luồng Batch vs Query (phi chức năng)

**Ngoài phạm vi (không test vì ngoài scope hệ thống):**
- Hạch toán kế toán tổng hợp (GL)
- Thu phí tiền mặt tại quầy
- Quy trình hoàn phí (refund)
- Giao diện cấu hình tham số miễn giảm (hệ thống Params — chỉ test chiều đọc)
- Kênh thông báo Email/OTT

## 3. Mức kiểm thử (Test Levels)

| Cấp độ | Mục tiêu | Người thực hiện |
|---|---|---|
| Unit Test | Logic tính phí sau miễn giảm, bộ đếm Retry, phân loại lỗi Core Banking | Dev |
| Integration Test | Kết nối Hệ thống nguồn, Params, Core Banking (mock/stub), SMS Gateway | Dev/QA |
| System Test | Toàn luồng end-to-end trên môi trường staging | QA |
| Reconciliation Test | Đối soát số liệu giữa các báo cáo và log giao dịch gốc | QA |
| Non-functional Test | Hiệu năng, tách luồng Batch/Query, tải AutoRetry | QA/DevOps |
| UAT | Bank Staff xác nhận báo cáo đúng nghiệp vụ | Bank Staff |

## 4. Môi trường kiểm thử

- Stub/mock cho Core Banking cho phép giả lập các trạng thái: Thành công, Lỗi số dư, Tài khoản đóng, Tài khoản phong tỏa, Timeout.
- Stub cho Hệ thống Params cho phép giả lập: có miễn giảm một phần, miễn giảm hoàn toàn, không miễn giảm, timeout/không phản hồi.
- Stub cho SMS Gateway cho phép giả lập gửi thành công và gửi lỗi.
- Bộ dữ liệu mẫu bao phủ đủ các AppCode nguồn khác nhau.
- Khả năng chỉnh thời gian hệ thống (time-travel/fast-forward) để test đủ chu kỳ AutoRetry 10 lần mà không cần chờ thực tế.

## 5. Entry / Exit Criteria

**Entry criteria:** Hoàn thành QG-1 đến QG-8 (xem `Quality-Gates.md`) ở mức unit/integration; môi trường staging sẵn sàng với đầy đủ stub.

**Exit criteria:** Toàn bộ test case mức Critical/High ở mục 6 PASS; QG-9 (đối soát tổng thể) khớp 100%; không còn defect mở mức Critical/High.

---

## 6. Test Cases

### 6.1 Tiếp nhận danh sách & Miễn giảm (US-01 / QG-1)

| TC ID | Mô tả | Precondition | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|---|
| TC-01-01 | Nhận đúng danh sách thô đủ 6 trường | Có file/API từ Hệ thống nguồn | Gửi danh sách với đủ Ngày, AppCode, Mã KH, SĐT, STK, Số tiền | Hệ thống nhận và lưu đúng "Danh sách cần thu" (raw), không mất trường | Critical |
| TC-01-02 | Thiếu trường bắt buộc | Danh sách thô thiếu STK hoặc Số tiền | Gửi danh sách lỗi | Hệ thống từ chối/đánh dấu lỗi bản ghi, không đẩy sang bước trích nợ | High |
| TC-01-03 | Khách hàng không có trong danh sách miễn giảm | Params không trả về bản ghi miễn giảm cho KH X | Chạy đối chiếu | KH X vào "Danh sách phải thu" với đúng số tiền gốc | Critical |
| TC-01-04 | Khách hàng được miễn giảm một phần | Params trả miễn giảm 50% cho KH Y | Chạy đối chiếu | Số tiền phải thu = Số tiền gốc − mức miễn giảm, > 0, vào "Danh sách phải thu" | Critical |
| TC-01-05 | Khách hàng được miễn giảm hoàn toàn | Params trả miễn giảm 100% cho KH Z | Chạy đối chiếu | Số tiền = 0 → KH Z **bị loại khỏi** "Danh sách phải thu"; không phát sinh giao dịch trích nợ, không SMS | Critical |
| TC-01-06 | Hệ thống Params timeout/không phản hồi | Giả lập Params không phản hồi | Chạy đối chiếu | Bản ghi liên quan được log/cảnh báo rõ ràng, không tự ý coi là "được/không được miễn giảm" một cách âm thầm | High |
| TC-01-07 | Tách biệt raw vs processed | Đã chạy đối chiếu | Kiểm tra lưu trữ | "Danh sách cần thu" (raw) vẫn còn nguyên, không bị ghi đè bởi "Danh sách phải thu" | High |
| TC-01-08 | Mapping trường Chi nhánh | Có STK hợp lệ | Chạy xử lý danh sách | Trường Chi nhánh được gán đúng nguồn (Core Banking hoặc Hệ thống nguồn theo thiết kế), không rỗng | High |
| TC-01-09 | Thứ tự xử lý miễn giảm trước trích nợ | Có danh sách hỗn hợp | Theo dõi trace log toàn luồng | Bước đối chiếu miễn giảm hoàn tất 100% trước khi bản ghi đầu tiên được gửi sang Core Banking | Critical |

### 6.2 Thực thi trích nợ Core Banking (US-02 / QG-2)

| TC ID | Mô tả | Precondition | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|---|
| TC-02-01 | Trích nợ thành công | KH có đủ số dư | Gửi lệnh trích nợ | Core Banking trả Thành công → trạng thái cập nhật, chuyển US-04 | Critical |
| TC-02-02 | Lỗi số dư | KH không đủ số dư | Gửi lệnh trích nợ | Core Banking trả lỗi số dư → chuyển sang AutoRetry (US-03), không gửi SMS | Critical |
| TC-02-03 | Tài khoản đóng | STK đã đóng | Gửi lệnh trích nợ | Dừng thu phí ngay lập tức, **không** vào vòng lặp AutoRetry | Critical |
| TC-02-04 | Tài khoản bị phong tỏa | STK bị phong tỏa | Gửi lệnh trích nợ | Dừng thu phí ngay lập tức, **không** vào vòng lặp AutoRetry | Critical |
| TC-02-05 | Phân biệt lỗi số dư vs lỗi tài khoản đóng/phong tỏa | Giả lập 2 mã lỗi khác nhau từ Core Banking | Gửi 2 lệnh trích nợ tương ứng | Hệ thống định tuyến đúng 2 nhánh xử lý khác nhau, không nhầm lẫn | Critical |
| TC-02-06 | Timeout khi gọi Core Banking | Giả lập timeout | Gửi lệnh trích nợ, mất phản hồi | Không tạo giao dịch trùng khi hệ thống tự động gọi lại (idempotency); trạng thái được xác minh lại trước khi retry kỹ thuật | High |
| TC-02-07 | Trích nợ trùng lặp | Gửi 2 lần cùng 1 bản ghi phải thu (giả lập lỗi kỹ thuật) | Gửi lệnh trích nợ 2 lần | Chỉ 1 giao dịch trích nợ thực tế được ghi nhận | Critical |
| TC-02-08 | Log giao dịch đầy đủ | Bất kỳ kết quả nào | Gửi lệnh trích nợ | Log ghi đủ mã giao dịch, thời điểm, kết quả trả về | Medium |

### 6.3 AutoRetry (US-03 / QG-3)

| TC ID | Mô tả | Precondition | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|---|
| TC-03-01 | Vào AutoRetry sau lỗi số dư lần 1 | Giao dịch lỗi số dư | Kiểm tra hàng đợi Retry | Bản ghi được đưa vào AutoRetry với bộ đếm = 1 (hoặc theo quy ước) | Critical |
| TC-03-02 | Retry thành công ở lần thứ N (N<10) | KH nạp đủ tiền trước lần thử N | Scheduler chạy lại | Giao dịch chuyển Thành công, dừng Retry, chuyển US-04 | Critical |
| TC-03-03 | Retry đủ 10 lần vẫn thất bại | KH không nạp tiền trong suốt chu kỳ | Scheduler chạy đủ 10 lần | Sau lần 10, trạng thái chuyển "thất bại vĩnh viễn", không có lần thứ 11 | Critical |
| TC-03-04 | Không vượt quá 10 lần | Đã đạt lần 10 | Chạy scheduler thêm 1 chu kỳ | Bản ghi không bị đưa vào Retry lần 11 | Critical |
| TC-03-05 | Chuyển từ lỗi số dư sang lỗi tài khoản phong tỏa giữa chừng | Đang ở lần Retry thứ 3, tài khoản bị phong tỏa trước lần 4 | Scheduler chạy lần 4 | Thoát khỏi vòng lặp Retry ngay, không tính tiếp, chuyển trạng thái dừng do lỗi phi số dư | Critical |
| TC-03-06 | Bản ghi đang Retry hiển thị đúng trong Báo cáo không đủ số dư | Có bản ghi đang ở lần Retry thứ 5 | Truy vấn Báo cáo US-07 | Bản ghi xuất hiện với đúng số dư tài khoản tại lần kiểm tra gần nhất | Critical |
| TC-03-07 | Lịch chạy Scheduler đúng cấu hình | Cấu hình tần suất X giờ/lần | Theo dõi log Scheduler trong 24h | Số lần chạy khớp với tần suất cấu hình, không chạy dồn dập | Medium |
| TC-03-08 | Batch AutoRetry không khóa luồng Query | Batch đang chạy AutoRetry với dữ liệu lớn | Đồng thời truy vấn báo cáo | Báo cáo trả về đúng thời gian phản hồi cam kết (xem mục 7), không bị lock | High |

### 6.4 Gửi SMS (US-04 / QG-4)

| TC ID | Mô tả | Precondition | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|---|
| TC-04-01 | Gửi SMS khi trích nợ thành công | Giao dịch Thành công | Theo dõi hàng đợi SMS | SMS được gửi đúng SĐT khách hàng | Critical |
| TC-04-02 | Không gửi SMS khi thất bại | Giao dịch lỗi số dư (đang Retry) | Theo dõi hàng đợi SMS | Không có SMS nào được gửi cho bản ghi này | Critical |
| TC-04-03 | Không gửi SMS khi miễn giảm hoàn toàn | KH miễn giảm 100% | Theo dõi hàng đợi SMS | Không có SMS gửi cho KH này | Critical |
| TC-04-04 | SMS Gateway lỗi/timeout | Giả lập SMS Gateway lỗi | Trích nợ thành công, gửi SMS thất bại | Trạng thái giao dịch trích nợ **vẫn giữ nguyên** Thành công, không bị rollback; có cơ chế log/cảnh báo lỗi gửi SMS | High |
| TC-04-05 | Không gửi trùng SMS | Giao dịch thành công, hệ thống bị gọi xử lý 2 lần (lỗi kỹ thuật) | Theo dõi hàng đợi SMS | Chỉ 1 SMS được gửi cho cùng 1 giao dịch | High |

### 6.5 Báo cáo Chi tiết (US-05 / QG-5)

| TC ID | Mô tả | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|
| TC-05-01 | Đủ trường hiển thị | Truy vấn báo cáo | Hiển thị đủ STT, Ngày phải thu, Chi nhánh, Mã KH, SĐT, STK, Số tiền Phí, Remark, Trạng thái, Ngày thu | Critical |
| TC-05-02 | Phân biệt Ngày phải thu vs Ngày thu | Truy vấn giao dịch đã qua AutoRetry (Ngày thu ≠ Ngày phải thu) | 2 trường hiển thị đúng giá trị riêng biệt, không bị gán nhầm | Critical |
| TC-05-03 | Trạng thái phản ánh real-time | Giao dịch chuyển từ Đang Retry → Thành công | Trạng thái trên báo cáo cập nhật đúng ngay sau khi có kết quả mới | High |
| TC-05-04 | Đối chiếu với log gốc | Chọn ngẫu nhiên N bản ghi | So sánh số tiền/trạng thái/ngày với log giao dịch gốc | Khớp 100% | Critical |
| TC-05-05 | Báo cáo chỉ đọc | Người dùng thử sửa dữ liệu từ giao diện báo cáo | Không có chức năng chỉnh sửa | Critical |

### 6.6 Báo cáo Tổng hợp (US-06 / QG-6)

| TC ID | Mô tả | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|
| TC-06-01 | Đủ trường hiển thị | Truy vấn báo cáo | Hiển thị đủ STT, Ngày thu phí, Chi nhánh, Số tiền Phí (Tổng), Remark, Trạng thái | Critical |
| TC-06-02 | Tổng khớp với Chi tiết | Truy vấn cùng khoảng thời gian ở cả 2 báo cáo | Tổng tiền theo Chi nhánh + Ngày ở Báo cáo Tổng hợp = tổng cộng dồn các bản ghi Thành công tương ứng ở Báo cáo Chi tiết | Critical |
| TC-06-03 | Không lẫn giao dịch đang Retry vào tổng đã thu | Có giao dịch đang Retry trong kỳ | Kiểm tra số liệu tổng hợp | Giao dịch đang Retry không được cộng vào cột số tiền đã thu (trừ khi có cột riêng) | High |

### 6.7 Báo cáo không đủ số dư (US-07 / QG-7)

| TC ID | Mô tả | Bước thực hiện | Kết quả mong đợi | Mức độ |
|---|---|---|---|---|
| TC-07-01 | Đủ trường hiển thị | Truy vấn báo cáo | Hiển thị đủ STT, Ngày phải thu, Chi nhánh, Mã KH, SĐT, STK, Số tiền Phí, Số dư tài khoản, Ghi chú | Critical |
| TC-07-02 | Chỉ chứa giao dịch đang Retry | Có giao dịch Thành công + đang Retry + thất bại vĩnh viễn trong hệ thống | Truy vấn báo cáo | Chỉ các bản ghi đang AutoRetry (chưa quá 10 lần, chưa thành công) xuất hiện | Critical |
| TC-07-03 | Bản ghi biến mất khi kết thúc Retry | Giao dịch chuyển Thành công hoặc đạt lần 10 | Truy vấn lại báo cáo | Bản ghi không còn xuất hiện trong báo cáo này (hoặc chuyển trạng thái rõ ràng), không trùng lặp với báo cáo khác | Critical |
| TC-07-04 | Số dư tài khoản cập nhật | Bản ghi đang ở lần Retry thứ K | Truy vấn báo cáo | "Số dư tài khoản" là số dư tại lần kiểm tra gần nhất, không phải số dư ban đầu | Medium |

---

## 7. Kiểm thử phi chức năng (Non-functional)

| NFT ID | Mô tả | Kết quả mong đợi |
|---|---|---|
| NFT-01 | Tách luồng Batch/Query | Thời gian phản hồi truy vấn báo cáo không tăng quá X% khi batch AutoRetry chạy song song (ngưỡng X thống nhất với team) |
| NFT-02 | Tải AutoRetry lớn | Với ~10.000 bản ghi đang Retry đồng thời, Scheduler vẫn hoàn thành 1 chu kỳ trong SLA quy định, không quá tải Core Banking (rate limit) |
| NFT-03 | Khả năng phục hồi khi Core Banking gián đoạn | Khi Core Banking downtime giữa batch, hệ thống không đánh dấu nhầm hàng loạt giao dịch là "lỗi số dư"; có cơ chế phân biệt lỗi hệ thống vs lỗi nghiệp vụ |
| NFT-04 | Idempotency toàn luồng | Chạy lại cùng 1 batch job 2 lần do lỗi vận hành → không phát sinh trích nợ trùng, không gửi SMS trùng |

---

## 8. Kiểm thử đối soát tổng thể (QG-9 — End-to-end Reconciliation)

Chạy trên 1 chu kỳ dữ liệu đầy đủ (mô phỏng 1 ngày làm việc, có đủ các case: miễn giảm một phần/toàn phần, lỗi số dư, tài khoản đóng/phong tỏa, retry đủ 10 lần):

| RC ID | Phép đối soát | Kết quả mong đợi |
|---|---|---|
| RC-01 | Số bản ghi raw = Số miễn giảm hoàn toàn + Số bản ghi trong "Danh sách phải thu" | Khớp tuyệt đối |
| RC-02 | Số bản ghi "phải thu" = Thành công + Đang Retry + Thất bại vĩnh viễn + Dừng do lỗi phi số dư | Khớp tuyệt đối |
| RC-03 | Số SMS gửi = Số giao dịch Thành công | Khớp tuyệt đối |
| RC-04 | Tổng tiền Báo cáo Tổng hợp = Tổng tiền Thành công trong Báo cáo Chi tiết | Khớp tuyệt đối |
| RC-05 | Không có bản ghi "mất tích" | Mọi bản ghi raw truy vết được đến trạng thái cuối cùng |

---

## 9. Rủi ro & Giảm thiểu

| Rủi ro | Ảnh hưởng | Giảm thiểu |
|---|---|---|
| Nhầm lẫn lỗi số dư với lỗi tài khoản đóng/phong tỏa | Retry sai đối tượng, tốn tài nguyên hoặc bỏ sót dừng thu đúng lúc | Test case riêng TC-02-05, TC-03-05 với mã lỗi giả lập rõ ràng |
| Params không phản hồi khi đối chiếu miễn giảm | Thu sai (thiếu/thừa) phí khách hàng | TC-01-06, cần cơ chế cảnh báo bắt buộc, không fail-open/fail-close âm thầm |
| Trùng giao dịch trích nợ/SMS do lỗi kỹ thuật (timeout, retry hạ tầng) | Khách hàng bị trừ tiền/nhận SMS nhiều lần → khiếu nại | TC-02-06, TC-02-07, TC-04-05, NFT-04 |
| Trường Chi nhánh sai nguồn gốc | Báo cáo sai theo chi nhánh, ảnh hưởng đối soát vận hành | TC-01-08 |
| Batch AutoRetry ảnh hưởng hiệu năng báo cáo | Bank Staff không tra cứu được báo cáo kịp thời | NFT-01, NFT-02 |

---

## 10. Ma trận Test Case ↔ User Story / Quality Gate

| User Story | Quality Gate | Số test case | Ghi chú |
|---|---|---|---|
| US-01 | QG-1 | 9 (TC-01-xx) | Trọng tâm: miễn giảm hoàn toàn, thứ tự xử lý |
| US-02 | QG-2 | 8 (TC-02-xx) | Trọng tâm: phân biệt lỗi số dư vs đóng/phong tỏa |
| US-03 | QG-3 | 8 (TC-03-xx) | Trọng tâm: đúng 10 lần, thoát sớm khi lỗi phi số dư |
| US-04 | QG-4 | 5 (TC-04-xx) | Trọng tâm: đúng đối tượng nhận SMS |
| US-05 | QG-5 | 5 (TC-05-xx) | Trọng tâm: Ngày phải thu vs Ngày thu |
| US-06 | QG-6 | 3 (TC-06-xx) | Trọng tâm: khớp tổng với Chi tiết |
| US-07 | QG-7 | 4 (TC-07-xx) | Trọng tâm: chỉ chứa giao dịch đang Retry |
| — | QG-8 | 4 (NFT-xx) | Phi chức năng |
| — | QG-9 | 5 (RC-xx) | Đối soát tổng thể, gate cuối trước release |

**Tổng: 51 test case**, bao phủ toàn bộ 7 User Story và 9 Quality Gate đã định nghĩa.

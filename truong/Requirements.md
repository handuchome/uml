# Requirements

Source of truth: [Domain.md](Domain.md). Dựa trên yêu cầu từ `image_7beaf4.jpg`.

**Domain.** Hệ thống Thu các loại phí dịch vụ cho Ngân hàng.

**In scope.**
- Tiếp nhận danh sách thu phí và danh sách miễn giảm.
- Xử lý logic phí thực tế (>0).
- Trích nợ Core Banking.
- AutoRetry 10 lần.
- Gửi tin nhắn SMS.
- 03 loại Báo cáo (Chi tiết, Tổng hợp, Không đủ số dư).

**Out of scope.**
- Giao diện cấu hình chính sách miễn giảm (chỉ đọc từ Params).
- Thu phí thủ công tại quầy.

---

## Actors

| Actor | Type | Role |
|---|---|---|
| Hệ thống Nguồn | External | Cung cấp danh sách cần thu phí (AppCode, Số tiền...). |
| Hệ thống Params | External | Cung cấp danh sách khách hàng được miễn giảm. |
| Core Banking | External | Thực hiện trích nợ tài khoản. Trả về trạng thái và số dư. |
| SMS Gateway | External | Gửi tin nhắn cho khách hàng khi thu phí thành công. |
| Bank Staff | Primary | Tra cứu 03 loại báo cáo thu phí. |

---

## User stories

### US-01 — Tiếp nhận và xử lý danh sách phải thu
Là hệ thống, tôi cần tiếp nhận dữ liệu và áp dụng chính sách miễn giảm để xác định danh sách khách hàng thực sự cần trích nợ.
**Acceptance criteria**
- Nhận danh sách đầu vào với cấu trúc: Ngày, AppCode, Mã KH, SĐT, STK, Số tiền.
- Đối chiếu với nguồn Params để lọc danh sách khách hàng được miễn giảm.
- Sinh ra "Danh sách phải thu" chỉ bao gồm các khách hàng có mức phí > 0 (sau khi đã trừ miễn giảm).

### US-02 — Thực thi thu phí
Là hệ thống, tôi cần gửi lệnh trích nợ sang Core Banking đối với danh sách phải thu.
**Acceptance criteria**
- Gửi lệnh trích nợ dựa trên STK và Số tiền thực tế.
- Nếu Core Banking báo thành công, ghi nhận trạng thái giao dịch và chuyển sang US-04.
- Nếu Core Banking báo lỗi số dư, chuyển sang US-03.

### US-03 — Cơ chế AutoRetry
Là hệ thống, tôi cần tự động thử thu lại các khoản phí chưa thành công do lỗi số dư để tối ưu hóa doanh thu.
**Acceptance criteria**
- Với các giao dịch thất bại do không đủ số dư, hệ thống tự động đưa vào danh sách AutoRetry.
- Tối đa thực hiện Retry 10 lần cho mỗi khoản thu.
- Khi đạt đến lần thứ 10 vẫn thất bại, đánh dấu trạng thái thất bại vĩnh viễn (hoặc theo nghiệp vụ quy định).

### US-04 — Thông báo khách hàng
Là hệ thống, tôi cần gửi SMS cho khách hàng ngay khi thu phí thành công.
**Acceptance criteria**
- Chỉ kích hoạt gửi SMS khi Core Banking trả về trạng thái trích nợ thành công.
- Không gửi SMS cho các trường hợp thu thất bại hoặc được miễn giảm hoàn toàn (số tiền = 0).

### US-05 — Báo cáo tra cứu kết quả chi tiết
Là nhân viên ngân hàng, tôi muốn xem chi tiết từng giao dịch thu phí.
**Acceptance criteria**
- Hiển thị các trường: STT, Ngày phải thu, Chi nhánh, Mã KH, SĐT, STK, Số tiền Phí, Remark, Trạng thái, Ngày thu.

### US-06 — Báo cáo Tổng hợp
Là nhân viên ngân hàng, tôi muốn xem tổng quan dòng tiền thu phí theo chi nhánh và ngày.
**Acceptance criteria**
- Hiển thị các trường: STT, Ngày thu phí, Chi nhánh, Số tiền Phí (Tổng), Remark, Trạng thái.

### US-07 — Báo cáo khách hàng không đủ số dư
Là nhân viên ngân hàng, tôi muốn theo dõi danh sách khách hàng đang bị nợ phí do thiếu số dư.
**Acceptance criteria**
- Hiển thị các trường: STT, Ngày phải thu, Chi nhánh, Mã KH, SĐT, STK, Số tiền Phí, Số dư tài khoản, Ghi chú.


## Quality Gates — Hệ thống Thu các loại phí dịch vụ cho Ngân hàng

Nguồn tham chiếu: Domain.md, Requirements.md

Mục đích: định nghĩa các "cổng chất lượng" (quality gates) mà mỗi luồng nghiệp vụ / hạng mục phải vượt qua trước khi được coi là hoàn thành (Definition of Done) hoặc trước khi cho phép chuyển sang giai đoạn tiếp theo (ví dụ: từ Xử lý danh sách → Trích nợ → Thông báo → Báo cáo). Mỗi gate gồm: Điều kiện đầu vào (Entry), Tiêu chí kiểm tra (Checks), Điều kiện đạt (Exit/Pass), và Tham chiếu tới User Story / Domain.

### QG-0 — Ranh giới & Phạm vi (Scope Boundary Gate)

Áp dụng cho toàn bộ hệ thống trước khi thiết kế/triển khai bất kỳ module nào.

Checks

 Không có module nào thực hiện hạch toán kế toán tổng hợp (GL).
 Không có chức năng thu phí tiền mặt tại quầy.
 Không có quy trình hoàn phí (refund).
 Không có giao diện tạo/sửa tham số miễn giảm — hệ thống Params chỉ được đọc (read-only).
 Kênh thông báo chỉ giới hạn SMS; không phát sinh Email/OTT nếu chưa được yêu cầu bổ sung.
 Báo cáo chỉ giới hạn 3 loại: Chi tiết, Tổng hợp, Không đủ số dư — không phát sinh báo cáo kế toán GL.

Exit condition: Mọi hạng mục thiết kế/code review đối chiếu đúng danh sách In/Out ở trên; PR nào chạm vào phần "Out" phải bị từ chối hoặc yêu cầu làm rõ phạm vi.

### QG-1 — Tiếp nhận danh sách & Xử lý miễn giảm (US-01)

Entry: Có dữ liệu thô từ Hệ thống nguồn (AppCode) và dữ liệu miễn giảm từ hệ thống Params.

Checks

 Danh sách thô đầu vào có đủ 6 trường bắt buộc: Ngày, AppCode, Mã KH, SĐT, STK, Số tiền.
 "Danh sách cần thu" (raw) và "Danh sách phải thu" (processed) được lưu/tách biệt rõ ràng, không ghi đè lẫn nhau.
 Logic đối chiếu miễn giảm chạy trước khi bất kỳ bản ghi nào được đẩy sang bước trích nợ Core Banking.
 Khách hàng được miễn giảm hoàn toàn (số tiền sau miễn giảm = 0) bị loại khỏi "Danh sách phải thu".
 Chỉ các bản ghi có Số tiền > 0 (sau khi trừ miễn giảm) mới được đưa vào danh sách phải thu.
 Có cơ chế xử lý khi hệ thống Params không phản hồi/timeout (không được mặc định coi là "được miễn giảm" hoặc "không miễn giảm" một cách âm thầm — cần log/cảnh báo).
 Trường "Chi nhánh" được ánh xạ rõ nguồn gốc (từ STK/Core Banking hoặc từ Hệ thống nguồn) trước khi ghi vào bất kỳ báo cáo nào, vì trường này không có trong input thô.

Exit condition: 100% bản ghi trong "Danh sách phải thu" có Số tiền > 0, có Chi nhánh xác định, và có thể truy vết ngược về bản ghi raw + kết quả đối chiếu Params tương ứng.

### QG-2 — Thực thi trích nợ qua Core Banking (US-02)

Entry: Có "Danh sách phải thu" hợp lệ từ QG-1.

Checks

 Lệnh trích nợ gửi đi đúng STK và đúng Số tiền thực tế (đã trừ miễn giảm).
 Kết quả trả về từ Core Banking được phân loại rõ ràng theo tối thiểu 3 nhóm: Thành công, Lỗi số dư, Lỗi khác (tài khoản đóng/phong tỏa).
 Giao dịch thành công → cập nhật trạng thái + chuyển sang US-04 (SMS).
 Giao dịch lỗi số dư → chuyển sang US-03 (AutoRetry), không chuyển sang US-04.
 Giao dịch lỗi do tài khoản đóng/phong tỏa → dừng thu phí ngay, không đưa vào vòng lặp AutoRetry (đây là điểm dễ nhầm lẫn nhất — cần test case riêng để đảm bảo không lẫn với luồng lỗi số dư).
 Không có giao dịch trích nợ trùng lặp cho cùng một bản ghi phải thu (idempotency khi gọi API Core Banking, đặc biệt khi có timeout/retry ở tầng kỹ thuật).
 Mỗi lần gọi Core Banking đều được ghi log đủ để phục vụ đối soát (mã giao dịch, thời điểm, kết quả).

Exit condition: Mỗi bản ghi trong "Danh sách phải thu" kết thúc ở đúng một trong ba nhánh trạng thái (Thành công / Đang Retry / Dừng vĩnh viễn không do số dư), không có bản ghi "treo" không rõ trạng thái.

### QG-3 — Cơ chế AutoRetry (US-03)

Entry: Có giao dịch bị lỗi số dư từ QG-2.

Checks

 Giao dịch lỗi số dư được đưa vào hàng đợi AutoRetry với bộ đếm số lần retry khởi tạo đúng (0 hoặc 1 tùy quy ước).
 Có Scheduler/cơ chế định tuyến rõ ràng quyết định thời điểm chạy lại (tần suất, khung giờ) — không retry dồn dập gây quá tải Core Banking.
 Số lần retry tối đa = 10, không vượt quá.
 Sau lần thử thứ 10 vẫn thất bại → đánh dấu trạng thái thất bại vĩnh viễn (hoặc trạng thái nghiệp vụ quy định) và dừng đưa vào vòng lặp tiếp theo.
 Nếu trong quá trình retry, giao dịch gặp lỗi không phải do số dư (VD: tài khoản bị phong tỏa giữa chừng) → thoát khỏi vòng lặp Retry ngay, không tính tiếp số lần, theo đúng ngoại lệ đã định nghĩa ở Domain.
 Toàn bộ các bản ghi đang trong trạng thái AutoRetry (chưa đạt lần thứ 10) đồng thời xuất hiện trong "Báo cáo không đủ số dư" (US-07).
 Luồng Batch (nhập liệu + Retry) tách biệt về mặt xử lý/tài nguyên với luồng Query (báo cáo) — kiểm tra không có tình trạng khóa bảng (locking) giữa hai luồng khi chạy song song.

Exit condition: Không có giao dịch nào retry quá 10 lần; mọi giao dịch dừng đúng lý do (thành công / hết lượt retry / lỗi phi số dư).

### QG-4 — Thông báo SMS (US-04)

Entry: Có giao dịch với trạng thái xác định từ QG-2/QG-3.

Checks

 SMS chỉ được kích hoạt khi Core Banking trả về Thành công.
 Không gửi SMS cho giao dịch thất bại (kể cả đang trong AutoRetry).
 Không gửi SMS cho khách hàng được miễn giảm hoàn toàn (số tiền = 0, không phát sinh giao dịch trích nợ).
 Có cơ chế xử lý khi SMS Gateway lỗi/timeout — lỗi gửi SMS không được làm rollback hoặc thay đổi trạng thái giao dịch trích nợ đã thành công.
 Không gửi trùng SMS cho cùng một giao dịch thành công (idempotency).

Exit condition: Tỷ lệ SMS gửi đúng đối tượng = 100% giao dịch trạng thái Thành công, 0% cho các trạng thái khác.

### QG-5 — Báo cáo Chi tiết (US-05)

Checks

 Đủ các trường: STT, Ngày phải thu, Chi nhánh, Mã KH, SĐT, STK, Số tiền Phí, Remark, Trạng thái, Ngày thu.
 "Ngày phải thu" và "Ngày thu" là hai trường khác nhau và không bị gán nhầm giá trị cho nhau (quan trọng với các giao dịch AutoRetry — Ngày thu thực tế có thể khác Ngày phải thu ban đầu).
 Trạng thái hiển thị phản ánh đúng trạng thái mới nhất (Thành công / Đang Retry / Thất bại vĩnh viễn).
 Chi nhánh hiển thị đúng theo mapping đã xác định ở QG-1.
 Báo cáo chỉ đọc (read model), không cho phép chỉnh sửa dữ liệu giao dịch từ giao diện báo cáo.

Exit condition: Đối chiếu ngẫu nhiên N bản ghi báo cáo với log giao dịch gốc phải khớp 100% về số tiền, trạng thái, ngày.

### QG-6 — Báo cáo Tổng hợp (US-06)

Checks

 Đủ các trường: STT, Ngày thu phí, Chi nhánh, Số tiền Phí (Tổng), Remark, Trạng thái.
 Số tiền tổng theo Chi nhánh + Ngày = tổng cộng dồn từ các bản ghi chi tiết tương ứng (đối soát chéo với QG-5).
 Chỉ tổng hợp các giao dịch đã có kết quả cuối (không lẫn giao dịch đang chờ AutoRetry vào cột "đã thu", trừ khi có cột riêng thể hiện rõ).

Exit condition: Tổng số tiền trong Báo cáo Tổng hợp khớp tuyệt đối với tổng số tiền trạng thái Thành công trong Báo cáo Chi tiết, theo từng Chi nhánh/Ngày.

### QG-7 — Báo cáo khách hàng không đủ số dư (US-07)

Checks

 Đủ các trường: STT, Ngày phải thu, Chi nhánh, Mã KH, SĐT, STK, Số tiền Phí, Số dư tài khoản, Ghi chú.
 Danh sách chỉ chứa các bản ghi đang trong trạng thái AutoRetry (chưa vượt quá 10 lần và chưa thành công).
 "Số dư tài khoản" phản ánh số dư tại lần kiểm tra gần nhất, không phải số dư tại thời điểm phát sinh phí ban đầu.
 Khi giao dịch thành công hoặc đạt lần thứ 10, bản ghi phải biến mất khỏi báo cáo này (hoặc chuyển trạng thái rõ ràng), không tồn tại song song gây trùng lặp với báo cáo Chi tiết.

Exit condition: Số bản ghi trong báo cáo này == số giao dịch có trạng thái "Đang AutoRetry" tại cùng thời điểm truy vấn, không lệch.

### QG-8 — Kiến trúc & Phi chức năng (Architecture Implications)

Checks

 Luồng Batch (nhập liệu, xử lý miễn giảm, trích nợ, Retry) và luồng Query (3 báo cáo) chạy trên tài nguyên/tiến trình tách biệt, đảm bảo báo cáo không bị chậm/khóa khi batch đang chạy.
 Scheduler cho AutoRetry có cấu hình rõ: tần suất chạy, giới hạn 10 lần, khung giờ cho phép (nếu có ràng buộc nghiệp vụ ngân hàng, ví dụ không chạy trong giờ bảo trì Core Banking).
 Có cơ chế giám sát/log riêng cho luồng AutoRetry để phát hiện bất thường (VD: một giao dịch bị kẹt ở cùng 1 lần retry quá lâu).
 Nguồn gốc trường "Chi nhánh" được document hóa rõ trong thiết kế dữ liệu (mapping từ Core Banking hay Hệ thống nguồn), tránh mỗi module tự suy luận khác nhau.

Exit condition: Kiểm thử tải (load test) cho thấy luồng Query không bị ảnh hưởng >X% thời gian phản hồi khi luồng Batch đang chạy song song (ngưỡng X do team thống nhất).

### QG-9 — Đối soát tổng thể (End-to-end Reconciliation Gate)

Gate cuối cùng trước khi release, chạy trên tập dữ liệu đầy đủ một chu kỳ (ví dụ 1 ngày làm việc).

Checks

 Tổng số bản ghi "Danh sách cần thu" (raw) = Số bản ghi miễn giảm hoàn toàn + Số bản ghi trong "Danh sách phải thu".
 Tổng số bản ghi "Danh sách phải thu" = Số Thành công + Số đang AutoRetry + Số thất bại vĩnh viễn + Số dừng do lỗi phi số dư.
 Số lượng SMS gửi đi = Số giao dịch Thành công (không hơn, không kém).
 Tổng tiền Báo cáo Tổng hợp = Tổng tiền các giao dịch Thành công trong Báo cáo Chi tiết.
 Không có bản ghi nào "mất tích" giữa các bước (mọi bản ghi raw phải truy vết được đến trạng thái cuối cùng).

Exit condition: Tất cả 5 phép đối soát trên khớp tuyệt đối trên môi trường staging với dữ liệu mô phỏng đủ các edge case (miễn giảm hoàn toàn, lỗi số dư, tài khoản đóng/phong tỏa, retry đủ 10 lần) trước khi cho phép release lên production.

Bảng tổng hợp Gate ↔ User Story
Gate	Liên quan	Rủi ro chính nếu bỏ qua
QG-0	Toàn hệ thống	Lấn phạm vi, làm luôn phần Out of scope (GL, refund, quầy)
QG-1	US-01	Trích nợ nhầm khách được miễn giảm; sai Chi nhánh
QG-2	US-02	Trích nợ trùng; nhầm lỗi số dư với lỗi tài khoản đóng/phong tỏa
QG-3	US-03	Retry vô hạn hoặc quá 10 lần; quá tải Core Banking
QG-4	US-04	Gửi SMS sai đối tượng (thất bại/miễn giảm)
QG-5	US-05	Báo cáo sai lệch dữ liệu gốc
QG-6	US-06	Số liệu tổng hợp không khớp chi tiết
QG-7	US-07	Danh sách nợ phí không phản ánh đúng trạng thái hiện tại
QG-8	Architecture implications	Query bị chậm/khóa khi Batch chạy
QG-9	Toàn luồng	Thất thoát/sai lệch dữ liệu không bị phát hiện trước release



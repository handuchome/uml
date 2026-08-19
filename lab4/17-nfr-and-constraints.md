# 17. Non-Functional Requirements & Constraints

## 1. Business Rules (Constraints)
| ID | Rule | Constraint / Implementation | Priority |
|---|---|---|---|
| **BR-01** | Khoản thu hợp lệ | Chỉ xử lý nếu `Số tiền > 0` sau khi tính miễn giảm. | Must |
| **BR-02** | Ràng buộc lịch | **TUYỆT ĐỐI KHÔNG** phát sinh giao dịch trích nợ vào mùng 1 Âm lịch và Nghỉ lễ quốc gia. | Critical |
| **BR-03** | Giới hạn Retry | Lỗi số dư kích hoạt vòng lặp tối đa 10 lần. Sau đó đánh dấu thất bại vĩnh viễn. | Must |
| **BR-04** | Thông báo tức thời | Thu thành công bắt buộc phải gọi dịch vụ SMS ngay lập tức. | Must |
| **BR-05** | UI Constraints | Màn hình tra cứu không được truy vấn trực tiếp vào Core Banking. | Must |

## 2. NFRs (Non-Functional Requirements)
- **Performance:** Cơ chế lập lịch (Scheduler/Batch) phải xử lý phân trang, không load toàn bộ record lỗi lên RAM tránh OOM (Out Of Memory).
- **Scalability:** Áp dụng CQRS (Read/Write Split). UI đọc từ Replicated Database.
- **Availability:** Auto-reschedule nếu Calendar API down hoặc báo lễ.

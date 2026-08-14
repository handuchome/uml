# Hệ thống Thu các loại phí dịch vụ cho Ngân hàng

**Domain:** Bank Service Fee Collection System

**Phạm vi:** Hệ thống xử lý tập trung việc thu các loại phí dịch vụ từ tài khoản khách hàng (Digibank, Thẻ, IB TC), kiểm tra lịch thu, thực thi trích nợ tự động, và cung cấp màn hình tra cứu.

---

## 📋 Tài liệu chính

| Tài liệu | Mục đích |
|---|---|
| [Domain.md](Domain.md) | Định nghĩa domain, ranh giới hệ thống, In/Out scope, Business Rules |
| [Requirements.md](Requirements.md) | Danh sách chi tiết In scope, Out scope, Actors, User Stories (US-01...US-06) |
| [Analysis.md](Analysis.md) | Domain model, Business Rules, Flows (mermaid), Open assumptions |
| [Quality-Gates-Architecture.md](Quality-Gates-Architecture.md) | Checklist cho architecture design |
| [Quality-Gates-Design.md](Quality-Gates-Design.md) | Checklist cho logical design |

---

## 🎯 Công việc

1. ✅ Chuyển đổi scope sang các thông tin cụ thể (In scope / Out scope)
2. ✅ Generate lại requirement, analysis, Quality gates
3. 🔄 Generate detailed design and architecture (next phase)

---

## 📌 In Scope (7 thành phần chính)

1. Tiếp nhận danh sách từ 3 mảng (Digibank, Thẻ, IB TC)
2. Lọc danh sách miễn giảm (chỉ thu nếu Số tiền > 0)
3. Kiểm tra lịch thu phí tự động (Không thu mùng 1 Âm lịch / Nghỉ lễ)
4. Trích nợ Core Banking
5. Cơ chế AutoRetry (tối đa 10 lần)
6. Thông báo SMS sau khi thu thành công
7. Màn hình tra cứu UI (3 loại báo cáo)

---

## 🚫 Out of Scope (5 thành phần ngoài phạm vi)

1. Hạch toán kế toán tổng hợp (Do kế toán xử lý)
2. Thu phí tiền mặt tại quầy (Nằm ngoài kênh tự động)
3. Hoàn phí (Refund)
4. Tạo/Quản lý tham số miễn giảm (Quản lý trên hệ thống Params gốc)
5. Phân quyền user phức tạp (Chỉ tập trung vào chức năng tra cứu)
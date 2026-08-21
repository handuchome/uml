# Lab 1: Scopes with concrete values (Name-Identity Index)

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 1

---

## I-1. Team and topic

| Field | Your value |
|-------|------------|
| Group | Team 1 |
| Topic / initiative name | Bank Service Fee Collection System |
| System-in-focus | Fee Collection Hub |
| Goal | Centralize and automate fee collection across multiple banking channels with strict calendar constraints and retry mechanisms. |
| Outcome (measurable) | 100% compliance with holiday/lunar constraints, zero manual retry effort for insufficient funds (up to 10 times). |
| Product | Fee Collection Engine & Inquiry Portal |
| Contract | API Contracts for Source Ingestion, Core Debit Execution, and SMS Trigger. |
| Baseline → target | Fragmented, manual collection → Centralized, automated, compliant collection engine with CQRS reporting. |
| In scope | Ingestion (Digibank, Card, IB TC); Discount filtering (>0); Calendar check (Lunar 1st/Holiday); Core Banking debit; AutoRetry (max 10); SMS notification; Staff UI (3 reports). |
| Out of scope | Ledger accounting; OTC cash collection; Refunds; Param creation/management; Complex IAM. |

## I-2. Actors

| Name | ArchiMate | C4 (Person or —) | Role in the process |
|------|-----------|------------------|---------------------|
| Bank Staff | Business Actor | Person | Tra cứu kết quả thu phí (Chi tiết, Tổng hợp, Lỗi số dư) trên UI. |

## I-3. External systems

| Name (simulated) | Responsibility |
|------------------|----------------|
| Source System Digibank | Cung cấp danh sách phí mảng Digibank & SMS. |
| Source System Card | Cung cấp danh sách phí mảng Thẻ. |
| Source System IB TC | Cung cấp danh sách phí mảng Internet Banking Tổ chức. |
| Params System | Cung cấp danh sách/rule miễn giảm phí. |
| Calendar Service | Cung cấp API kiểm tra mùng 1 Âm lịch và Nghỉ lễ quốc gia. |
| Core Banking | Thực thi giao dịch trích nợ tài khoản (Debit). |
| SMS Gateway | Nhận lệnh và gửi tin nhắn SMS cho khách hàng. |

## I-4. Internal containers

| Name | Responsibility |
|------|----------------|
| Fee Ingestion Service | Tiếp nhận danh sách phí từ 3 nguồn, chuẩn hóa dữ liệu. |
| Fee Processing Engine | Áp dụng chính sách từ Params System, lọc phí > 0. |
| Calendar Gate | Chặn/Kiểm tra lịch thu phí trước khi gửi lệnh thực thi. |
| Execution Engine | Giao tiếp với Core Banking để thực hiện trích nợ. |
| Retry Scheduler | Lập lịch chạy lại (AutoRetry) cho các task lỗi số dư. |
| Notification Service | Kích hoạt gửi tin nhắn sang SMS Gateway khi thu thành công. |
| Fee Report API | Backend cung cấp dữ liệu báo cáo (Read Store). |
| Fee Inquiry Web App | Giao diện tra cứu dành cho Bank Staff. |
| Fee Database | Lưu trữ trạng thái xử lý chính (Write Store). |
| Report Database | Lưu trữ dữ liệu đã đồng bộ phục vụ tra cứu (Read Store). |

## I-5. Business process (happy path)

**Object:** `ProcessedFeeTask`

1. Fee Ingestion Service nhận danh sách từ các Source System và chuyển cho Fee Processing Engine.
2. Fee Processing Engine tính toán, tạo ProcessedFeeTask với số tiền > 0.
3. Calendar Gate kiểm tra ngày hiện tại, cho phép đi tiếp nếu không phải Lễ/Mùng 1 Âm lịch.
4. Execution Engine gửi lệnh trích nợ vào Core Banking thành công.
5. Notification Service gửi SMS; hệ thống đồng bộ dữ liệu sang Report Database.

**Principle / hard rules:**
- TUYỆT ĐỐI KHÔNG gửi lệnh trích nợ vào mùng 1 Âm lịch hoặc ngày Nghỉ lễ.
- Phải chia tách luồng ghi (Fee Database) và luồng đọc (Report Database).

## I-6. Named object states (use exactly on UML State)

**Object:** `ProcessedFeeTask`

| State | Trigger / event | Next state | Terminal? |
|-------|-----------------|------------|-----------|
| Created | Fee > 0 validated (BR-01) | Pending_Calendar | No |
| Pending_Calendar | Check Calendar (Pass) | Pending_Execution | No |
| Pending_Calendar | Check Calendar (Fail) | Rescheduled | No |
| Rescheduled | Next working day reached | Pending_Calendar | No |
| Pending_Execution | Debit Success | Completed | Yes |
| Pending_Execution | Debit Fail (Insufficient Funds) | Retrying | No |
| Retrying | Retry limits not reached (<10) | Pending_Execution | No |
| Retrying | Retry limits reached (10) | Failed_Permanently | Yes |

**Terminal states:**
- Completed
- Failed_Permanently

## I-7. Source of truth

| Data object | Meaning | Source of truth (one container or external) |
|-------------|---------|---------------------------------------------|
| RawFeeRecord | Dữ liệu gốc cần thu | Source System Digibank / Card / IB TC |
| ProcessedFeeTask | Trạng thái khoản thu | Fee Database |
| CalendarConstraint| Rule nghỉ lễ/Âm lịch | Calendar Service |
| FeeReport | Dữ liệu tra cứu | Report Database |

## I-8. Integration (label sync vs async on Container)

| Pattern | Mechanism | Example on your landscape |
|---------|-----------|---------------------------|
| Sync | REST API | Execution Engine gọi trích nợ sang Core Banking |
| Sync | REST API | Fee Inquiry Web App gọi Fee Report API |
| Async | Message Queue / Event | Execution Engine báo Notification Service gửi SMS |
| Async | Batch / File | Source Systems gửi file danh sách sang Fee Ingestion Service |
| Sync | REST API | Calendar Gate gọi Calendar Service |

## I-9. Deployment

| Location | What runs there |
|----------|-----------------|
| Internal App Zone | Fee Inquiry Web App, Fee Report API, Fee Ingestion Service, Fee Processing Engine, Calendar Gate, Execution Engine, Retry Scheduler, Notification Service |
| Internal Data Zone | Fee Database, Report Database |

**Forbidden path:** Fee Inquiry Web App KHÔNG ĐƯỢC query trực tiếp vào Core Banking hoặc Fee Database (phải qua Fee Report API & Report Database). Execution Engine KHÔNG ĐƯỢC chạy mà chưa thông qua Calendar Gate.

## I-10. Constraints (must appear on Motivation and on decision branches)

| ID | Constraint | Effect on the process |
|----|------------|------------------------|
| CON.1 (BR-01) | Phí > 0 | Lọc và loại bỏ các RawFeeRecord có số tiền <= 0 sau miễn giảm. |
| CON.2 (BR-02) | Chặn lịch (Lễ, Mùng 1 Âm) | Chuyển trạng thái task sang Rescheduled, không gửi lệnh Core. |
| CON.3 (BR-03) | AutoRetry Max 10 | Task lặp lại luồng trích nợ tối đa 10 lần, quá 10 lần -> Failed_Permanently. |
| CON.4 (BR-04) | Bắt buộc gửi SMS | Kích hoạt Notification Service ngay khi nhận kết quả thành công từ Core. |
| CON.5 (A5) | Read/Write Split | Dữ liệu UI đọc từ Report Database, tách biệt với luồng ghi trích nợ. |

## I-11. Named use cases for UML (not every component)

| Use case | Happy path | At least one exception (`alt`) |
|----------|------------|--------------------------------|
| UC-Ingestion | Tiếp nhận, kiểm tra Params, tạo Task phí >0 | `alt`: Phí <= 0 (Discard) |
| UC-Execution | Qua Calendar Gate, gọi Core thành công, gửi SMS | `alt`: Ngày Lễ (Reschedule); Lỗi số dư (To Retry) |
| UC-AutoRetry | Retry Scheduler chạy, gọi Core thành công | `alt`: Vượt quá 10 lần (Fail Permanently) |

**One container for optional C4 Component:** Execution Engine

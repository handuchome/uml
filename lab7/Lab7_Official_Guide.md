# Lab 7: Hierarchy, Focus Matrix, Quality Gates, RACI

**Project:** Bank Service Fee Collection System
**Phase:** Modeling - Lab 7
**RACI for this artifact:** R: EA (Nguyễn Nhật Trường) · A: Owner (Hàn Ngọc Đức)

---

## 1. Group Roster & Adoption Record

**Team:** Group 1
**Members:** Nguyễn Nhật Trường, Hà Ngọc Bắc, Dương Đỗ Minh, Hàn Ngọc Đức

**Role Mapping:**
*   **EA (Enterprise Architect):** Nguyễn Nhật Trường
*   **SA (Solution Architect):** Hà Ngọc Bắc
*   **Dev (Software Engineer):** Dương Đỗ Minh
*   **Test (Quality Engineer):** Hàn Ngọc Đức
*   **Owner (Business / Product Owner):** Hàn Ngọc Đức 
*   **BA (Business Analyst):** Nguyễn Nhật Trường 
*   **Sec / Ops:** Hà Ngọc Bắc 

**Adoption Record:**
Nhóm 1 cam kết chính thức áp dụng chuẩn phương pháp luận theo Hướng dẫn (Guide). Các cổng chất lượng (G1–G6) và mô hình RACI được tuân thủ nguyên bản, không sửa đổi, không tạo ra cổng G7+ và không tạo danh sách phân quyền (RACI) song song khác. Bộ hồ sơ Labs 1–6 (messy) đã được đóng gói (archived) nguyên trạng.

---

## 2. Diagram Header & RACI Line Template

*Biểu mẫu này sẽ được sao chép và dán vào tất cả các bản vẽ (diagrams) của cấu phần "After pack" (Lab 8, Lab 9, Lab 10).*

```text
Title:      [Tên bản vẽ - ví dụ: C4 Context / UC-Execution Sequence]
Viewpoint:  ArchiMate / C4 / UML [Chọn 1]
Layer(s):   Strategy / Business / App / Tech
As-Is | To-Be | Transition:  To-Be
Owner:      Role ________  Name ____________
RACI:       R ____  A ____  C ____  I ____
Version:    v1.0  Date 2026-08-21  Status Draft | Review | Approved
Legend:     [Mô tả các khoảng kết nối, đồng bộ/bất đồng bộ]
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: [Thành phần chính] / Out-of-scope: [Thành phần loại trừ]
```

---

## 3. Quality Gate Register (G1–G6)

*Ánh xạ trực tiếp từ Lab 2 Requirements (REQ-01 đến REQ-06) vào các tiêu chí (Pass Rule) được viết lại theo đúng ngữ cảnh sản phẩm (product wording) của hệ thống Bank Service Fee Collection.*

| Gate | Blocks | Pass Rule (Product Wording based on Lab 2) | Evidence Artifact | Pass? |
|---|---|---|---|---|
| **G1** Strategy signed | Solution design | Motivation/Strategy view must explicitly list the goal 'Centralize and automate fee collection' and constraints CON.1 to CON.5, directly mapping to **REQ-01, REQ-02, REQ-04, REQ-05, REQ-06**. | Lab 8: Motivation / Strategy View | Pending |
| **G2** Process + states | Dev + Test design | The business process must use the exact states for `ProcessedFeeTask` (Created, Pending_Calendar, Rescheduled, Pending_Execution, Retrying, Completed, Failed_Permanently) as defined in I-6 to fulfill **REQ-01 to REQ-05**. | Lab 8: Business Process View & Lab 10: State | Pending |
| **G3** C4 Context + Container | Implementation | No unnamed externals. Sync/async labels must reflect **REQ-01** (Async ingestion), **REQ-03** (Sync debit), **REQ-05** (Async SMS), **REQ-06** (Sync UI). Names must strictly match Lab 1 (I-3, I-4). | Lab 9: C4 Context (L1) & Container (L2) | Pending |
| **G4** Contracts | Coding of integrations | Every integration relationship (e.g., `Execution Engine` to `Core Banking` for **REQ-03**, `Report Projector` DB sync for **REQ-06**) must have a defined contract mapping to the Container diagram. | Lab 3: Contract Register | Pending |
| **G5** Critical exception path | Production release | Compensating actions for CON.1 (Fee <= 0 drop, **REQ-01**), CON.2 (Holiday block shift to Rescheduled, **REQ-02**), and CON.3 (Insufficient funds limit 10, **REQ-04**) must be visually modeled. | Lab 3: Exception Spec & Lab 5/10: UML | Pending |
| **G6** Test coverage | UAT sign-off | All `ProcessedFeeTask` state transitions and sequence `alt` branches (Holiday block, Insufficient funds) mapped to **REQ-01 to REQ-04** must be covered; participants strictly = C4 Container names. | Lab 10: Sequence diagrams & Coverage Note | Pending |

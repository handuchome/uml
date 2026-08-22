# Lab 10: System Modeling (UML Standardized)

**Project:** Bank Service Fee Collection System
**Phase:** After Pack (The Guide) - Lab 10
**Note:** Restyled from archived Lab 5. Explicitly strictly enforces Quality Gates G5 & G6, accurate C4 container strings, and mandatory Diagram Headers.

---

## 1. State Machine Diagram
*Satisfies G2 and G6: Exact I-6 states for ProcessedFeeTask.*

```text
Title:      State Machine - ProcessedFeeTask
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Test ________  Name Hàn Ngọc Đức
RACI:       R Hàn Ngọc Đức  A Nguyễn Nhật Trường  C Hà Ngọc Bắc  I Dương Đỗ Minh
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Arrows = State transitions | Brackets = Guards/Constraints
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: ProcessedFeeTask lifecycle explicitly mapping to CON.1-CON.3
```

```mermaid
stateDiagram-v2
    [*] --> Created: Ingested & Fee > 0 (CON.1)
    Created --> Pending_Calendar
    Pending_Calendar --> Pending_Execution: Calendar check passed
    Pending_Calendar --> Rescheduled: Calendar check failed (CON.2)
    Rescheduled --> Pending_Calendar: Next working day reached
    Pending_Execution --> Retrying: Debit fail (insufficient funds)
    Pending_Execution --> Completed: Debit success
    Retrying --> Pending_Execution: Retry limit < 10
    Retrying --> Failed_Permanently: Retry limit = 10 (CON.3)
    Completed --> [*]
    Failed_Permanently --> [*]
```

---

## 2. UC-Ingestion

### 2.1 Sequence Diagram
```text
Title:      UC-Ingestion Sequence Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Dev ________  Name Dương Đỗ Minh
RACI:       R Dương Đỗ Minh  A Hà Ngọc Bắc  C Nguyễn Nhật Trường  I Hàn Ngọc Đức
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Solid = Sync call | Dashed = Return/Async | alt = Exception path
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: Ingestion workflow and CON.1 exception handling
```

```mermaid
sequenceDiagram
    participant DCS as Digital Channel Source
    participant FIS as Fee Ingestion Service
    participant FPE as Fee Processing Engine
    participant Params as Params System
    participant DB as Fee Database

    Note over DCS,FIS: (Card & Corporate sources follow identical async flow)
    DCS->>FIS: Async FileTransfer / Batch
    FIS->>FPE: Forward raw records
    FPE->>Params: Fetch discount rules / fee config
    Params-->>FPE: Return policies
    alt Fee > 0 (CON.1)
        FPE->>DB: Insert ProcessedFeeTask (State: Created)
    else Fee <= 0
        FPE->>FPE: Discard record
    end
```

### 2.2 Activity Diagram
```text
Title:      UC-Ingestion Activity Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Test ________  Name Hàn Ngọc Đức
RACI:       R Hàn Ngọc Đức  A Nguyễn Nhật Trường  C Hà Ngọc Bắc  I Dương Đỗ Minh
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Diamonds = Decisions | Rectangles = Actions
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: Ingestion logic flow
```

```mermaid
flowchart TD
    Start([Receive Batch Files]) --> Parse[Parse RawFeeRecord]
    Parse --> Fetch[Fetch Policies from Params System]
    Fetch --> Calc[Calculate Final Fee]
    Calc --> Check{Fee > 0?}
    Check -- Yes --> Create[Create ProcessedFeeTask]
    Create --> Persist[Save to Fee Database as Created]
    Check -- No --> Discard[Discard Record]
    Persist --> End([End])
    Discard --> End
```

---

## 3. UC-Execution

### 3.1 Sequence Diagram
```text
Title:      UC-Execution Sequence Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Dev ________  Name Dương Đỗ Minh
RACI:       R Dương Đỗ Minh  A Hà Ngọc Bắc  C Nguyễn Nhật Trường  I Hàn Ngọc Đức
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Solid = Sync call | Dashed = Return/Async | alt = Exception path
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: Core execution, Calendar validation (CON.2), and Event dispatch
```

```mermaid
sequenceDiagram
    participant EE as Execution Engine
    participant Cal as Calendar Gate
    participant Core as Core Banking
    participant DB as Fee Database
    participant Broker as Message Broker

    EE->>DB: Query ProcessedFeeTask (Pending_Calendar)
    DB-->>EE: Return tasks
    EE->>Cal: GET /api/calendar/check
    alt Holiday/Lunar (CON.2)
        Cal-->>EE: Blocked
        EE->>DB: Update state to Rescheduled
    else Working Day
        Cal-->>EE: Allowed
        EE->>Core: POST /api/v1/core/debit
        alt Insufficient Funds
            Core-->>EE: 400 Error
            EE->>DB: Update state to Retrying
        else Success
            Core-->>EE: 200 OK
            EE->>DB: Update state to Completed
            EE->>Broker: Publish DebitSuccessEvent
        end
    end
```

### 3.2 Activity Diagram
```text
Title:      UC-Execution Activity Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Test ________  Name Hàn Ngọc Đức
RACI:       R Hàn Ngọc Đức  A Nguyễn Nhật Trường  C Hà Ngọc Bắc  I Dương Đỗ Minh
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Diamonds = Decisions | Rectangles = Actions
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: Execution logic flow and CON.2 enforcement
```

```mermaid
flowchart TD
    Start([Poll Pending_Calendar Tasks]) --> CalCheck[Call Calendar Gate]
    CalCheck --> IsBlocked{Blocked by Holiday?}
    IsBlocked -- Yes --> Reschedule[Set state: Rescheduled]
    IsBlocked -- No --> Debit[Call Core Banking Debit]
    Debit --> CheckFunds{Success?}
    CheckFunds -- No --> Retry[Set state: Retrying]
    CheckFunds -- Yes --> Complete[Set state: Completed]
    Complete --> Pub[Publish DebitSuccessEvent]
    Reschedule --> End([End])
    Retry --> End
    Pub --> End
```

---

## 4. UC-AutoRetry

### 4.1 Sequence Diagram
```text
Title:      UC-AutoRetry Sequence Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Dev ________  Name Dương Đỗ Minh
RACI:       R Dương Đỗ Minh  A Hà Ngọc Bắc  C Nguyễn Nhật Trường  I Hàn Ngọc Đức
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Solid = Sync call | Dashed = Return | alt = Exception path
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: AutoRetry constraint enforcement (CON.3)
```

```mermaid
sequenceDiagram
    participant Sched as Retry Scheduler
    participant DB as Fee Database
    participant Exec as Execution Engine

    Sched->>DB: Query ProcessedFeeTask (Retrying)
    DB-->>Sched: Return tasks
    alt Retry Count < 10
        Sched->>DB: Update state to Pending_Execution
        Sched->>Exec: Trigger Execution
    else Retry Count = 10 (CON.3)
        Sched->>DB: Update state to Failed_Permanently
    end
```

### 4.2 Activity Diagram
```text
Title:      UC-AutoRetry Activity Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Test ________  Name Hàn Ngọc Đức
RACI:       R Hàn Ngọc Đức  A Nguyễn Nhật Trường  C Hà Ngọc Bắc  I Dương Đỗ Minh
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Diamonds = Decisions | Rectangles = Actions
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: AutoRetry logic flow
```

```mermaid
flowchart TD
    Start([Poll Retrying Tasks]) --> CheckLimit{Retry Count == 10?}
    CheckLimit -- Yes --> Fail[Set state: Failed_Permanently]
    CheckLimit -- No --> Requeue[Set state: Pending_Execution]
    Requeue --> Trigger[Trigger Execution Engine]
    Fail --> End([End])
    Trigger --> End
```

---

## 5. UC-Inquiry

### 5.1 Sequence Diagram
```text
Title:      UC-Inquiry Sequence Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Dev ________  Name Dương Đỗ Minh
RACI:       R Dương Đỗ Minh  A Hà Ngọc Bắc  C Nguyễn Nhật Trường  I Hàn Ngọc Đức
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Solid = Sync call | Dashed = Return | alt = Conditional path
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: CQRS Report read flow
```

```mermaid
sequenceDiagram
    actor Staff as Bank Staff
    participant Web as Fee Inquiry Web App
    participant GW as API Gateway
    participant API as Fee Report API
    participant RDB as Report Database

    Staff->>Web: Request Fee Report
    Web->>GW: GET /api/reports
    GW->>API: Route Request
    API->>RDB: Query FeeReport
    alt Data Exists
        RDB-->>API: Return Records
        API-->>GW: 200 OK (Data)
        GW-->>Web: Forward Data
        Web-->>Staff: Display Dashboard
    else Empty Result
        RDB-->>API: Null
        API-->>GW: 404 / Empty List
        GW-->>Web: Forward Empty
        Web-->>Staff: Display "No Data"
    end
```

### 5.2 Activity Diagram
```text
Title:      UC-Inquiry Activity Diagram
Viewpoint:  UML
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role Test ________  Name Hàn Ngọc Đức
RACI:       R Hàn Ngọc Đức  A Nguyễn Nhật Trường  C Hà Ngọc Bắc  I Dương Đỗ Minh
Version:    v1.0  Date 2026-08-22  Status Approved
Legend:     Diamonds = Decisions | Rectangles = Actions
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: Inquiry logic flow
```

```mermaid
flowchart TD
    Start([User requests report]) --> Web[Web App calls API Gateway]
    Web --> Route[Gateway routes to Fee Report API]
    Route --> Query[API queries Report Database]
    Query --> Check{Data found?}
    Check -- Yes --> ReturnData[Format and return records]
    Check -- No --> ReturnEmpty[Return empty state]
    ReturnData --> Display[Render UI for Staff]
    ReturnEmpty --> Display
    Display --> End([End])
```

---

## 6. G5 & G6 Coverage Note (Test & Exception Matrix)
*Verifies compliance with Quality Gates G5 (Critical exceptions) and G6 (Test coverage).*

**G5 Compliance (Critical Exception Paths):**
- [x] **CON.1 (Fee <= 0):** Visually modeled in `UC-Ingestion` (`alt` branch dropping the task).
- [x] **CON.2 (Holiday/Lunar Block):** Visually modeled in `UC-Execution` (shifts to `Rescheduled`).
- [x] **CON.3 (AutoRetry Max 10):** Visually modeled in `UC-AutoRetry` (limits retries, shifts to `Failed_Permanently`).

**G6 Compliance (State & Sequence Coverage mapping to Lab 3 TS-xx):**
- [x] Transition: `Created` -> `Pending_Calendar` (Test ID: TS-02)
- [x] Transition: `Pending_Calendar` -> `Pending_Execution` (Test ID: TS-05)
- [x] Transition: `Pending_Calendar` -> `Rescheduled` (Test ID: TS-04)
- [x] Transition: `Rescheduled` -> `Pending_Calendar` (Test ID: TS-09)
- [x] Transition: `Pending_Execution` -> `Retrying` (Test ID: TS-07)
- [x] Transition: `Pending_Execution` -> `Completed` (Test ID: TS-08)
- [x] Transition: `Retrying` -> `Pending_Execution` (Test ID: TS-10)
- [x] Transition: `Retrying` -> `Failed_Permanently` (Test ID: TS-12)
- [x] UC-Ingestion `alt`: Fee <= 0 (CON.1) (Test ID: TS-01)
- [x] UC-Execution `alt`: Holiday/Lunar Block (CON.2) (Test ID: TS-03)
- [x] UC-Execution `alt`: Insufficient Funds (Test ID: TS-06)
- [x] UC-AutoRetry `alt`: Exceed max 10 retries (CON.3) (Test ID: TS-11)

---

## 7. Comparison Note (Lab 5 Messy vs Lab 10 Standardized)
*   **Name Identity & System Grain:** Ở Lab 5, các lifelines còn mang tính tự do/lộn xộn (ví dụ sử dụng `TaskPoller`, `DebitDispatcher`, gộp kênh `Digital / Card / Corp Channels`). Ở Lab 10, toàn bộ lifelines đã được audit và quy chuẩn 100% về tên C4 Container và External Systems đã chốt ở Lab 1/Lab 9.
*   **Governance & RACI:** Lab 5 hoàn toàn không có Header hay RACI (giai đoạn Messy). Sang Lab 10, mỗi bản vẽ đều được đóng dấu Diagram Header tiêu chuẩn với phân vai rõ ràng: Dev vẽ và SA duyệt Sequence; Test vẽ và BA duyệt Activity/State, đảm bảo tính khách quan (R ≠ A).
*   **Traceability & Quality Gates:** Lab 10 chuẩn hóa hoàn toàn các đường rẽ nhánh `alt` tương ứng với các ràng buộc CON.1, CON.2, CON.3 (đạt chuẩn G5), đồng thời có bảng đối chiếu G6 Test Coverage liên kết trực tiếp với mã kịch bản kiểm thử từ Lab 3.

# Lab 5: Low-Level Design (UML)

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 5
**Note:** Generated for named I-11 use cases only, current style (no Guide, no RACI).

---

## 1. State Machine Diagram
**Object:** `ProcessedFeeTask`

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
```mermaid
sequenceDiagram
    participant Sources as Digital / Card / Corp Channels
    participant FIS as Fee Ingestion Service
    participant FPE as Fee Processing Engine
    participant Params as Params System
    participant DB as Fee Database

    Sources->>FIS: Async FileTransfer / Batch
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
```mermaid
sequenceDiagram
    participant Poller as TaskPoller
    participant Disp as DebitDispatcher
    participant Cal as Calendar Gate
    participant Core as Core Banking
    participant DB as Fee Database
    participant Broker as Message Broker

    Poller->>DB: Query ProcessedFeeTask (Pending_Calendar)
    DB-->>Poller: Return tasks
    Poller->>Disp: Hand over tasks
    Disp->>Cal: GET /api/calendar/check
    alt Holiday/Lunar (CON.2)
        Cal-->>Disp: Blocked
        Disp->>DB: Update state to Rescheduled
    else Working Day
        Cal-->>Disp: Allowed
        Disp->>Core: POST /api/v1/core/debit
        alt Insufficient Funds
            Core-->>Disp: 400 Error
            Disp->>DB: Update state to Retrying
        else Success
            Core-->>Disp: 200 OK
            Disp->>DB: Update state to Completed
            Disp->>Broker: Publish DebitSuccessEvent
        end
    end
```

### 3.2 Activity Diagram
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

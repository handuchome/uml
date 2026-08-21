# Lab 5: UML Sequence Diagrams

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 5
*Note: One sequence diagram per named use case (I-11). Participants are strictly subsets of I-4 containers and I-3 externals.*

## UC-Ingestion: Tiếp nhận, kiểm tra Params, tạo Task phí >0
```mermaid
sequenceDiagram
    participant SS as Source System Digibank/Card/IB TC
    participant FIS as Fee Ingestion Service
    participant FPE as Fee Processing Engine
    participant DB as Fee Database

    SS->>FIS: Send RawFeeRecord
    FIS->>FPE: Validate and Calculate
    alt CON.1: Fee <= 0
        FPE-->>FIS: Discard (Do not process)
    else Fee > 0
        FPE->>DB: Save ProcessedFeeTask (State: Created)
    end
```

## UC-Execution: Qua Calendar Gate, gọi Core thành công, gửi SMS
```mermaid
sequenceDiagram
    participant DB as Fee Database
    participant EE as Execution Engine
    participant CG as Calendar Gate
    participant CB as Core Banking
    participant NS as Notification Service

    EE->>DB: Poll Tasks (State: Pending_Calendar)
    EE->>CG: Check Current Date
    alt CON.2: IsHoliday = True or IsLunarFirst = True
        CG-->>EE: Return Blocked
        EE->>DB: Update State (Rescheduled)
    else Normal Day
        CG-->>EE: Return Allowed
        EE->>DB: Update State (Pending_Execution)
        EE->>CB: POST /debit
        alt CON.3: Insufficient Funds
            CB-->>EE: 400 Bad Request
            EE->>DB: Update State (Retrying)
        else Debit Success
            CB-->>EE: 200 OK
            EE->>DB: Update State (Completed)
            EE->>NS: Emit DebitSuccessEvent (CON.4)
        end
    end
```

## UC-AutoRetry: Retry Scheduler chạy
```mermaid
sequenceDiagram
    participant RS as Retry Scheduler
    participant DB as Fee Database
    participant EE as Execution Engine

    RS->>DB: Poll Tasks (State: Retrying)
    alt CON.3: RetryCount >= 10
        RS->>DB: Update State (Failed_Permanently)
    else RetryCount < 10
        RS->>DB: Update RetryCount +1
        RS->>EE: Re-queue Task
        EE->>DB: Update State (Pending_Execution)
        Note over EE, DB: Task enters normal Execution flow
    end
```

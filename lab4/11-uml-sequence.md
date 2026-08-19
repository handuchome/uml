# 11. UML Sequence Diagrams

## 1. Sequence: Ingestion (US-01, BR-01)
```mermaid
sequenceDiagram
    participant Source as Nguồn (Digibank, Thẻ, IB TC)
    participant Ingest as Ingestion Service
    participant Params as Hệ thống Params
    participant DB as Primary DB

    Source->>Ingest: Gửi danh sách RawFeeRecord
    Ingest->>Params: Đối chiếu cấu hình miễn giảm
    Params-->>Ingest: Trả về Số tiền phí thực tế
    
    loop Per Record
        alt SoTienPhi > 0 (BR-01)
            Ingest->>DB: Tạo ProcessedFeeTask (Status=PENDING)
        else SoTienPhi <= 0
            Ingest->>DB: Ghi log Bỏ qua
        end
    end
```

## 2. Sequence: Calendar Check (US-02, BR-02)
```mermaid
sequenceDiagram
    participant Engine as Execution Engine
    participant Gate as Calendar Gate
    participant CalAPI as Calendar API
    participant Task as ProcessedFeeTask

    Engine->>Gate: Yêu cầu chạy Lô thu phí ngày X
    Gate->>CalAPI: GetDateInfo(X)
    CalAPI-->>Gate: {isLunarFirst, isHoliday}
    
    alt isLunarFirst == true OR isHoliday == true
        Gate-->>Engine: HALT (Cấm chạy)
        Engine->>Task: Update NgayPhaiThu = Next Working Day
    else Normal Day
        Gate-->>Engine: PROCEED
        Engine->>Task: Đẩy vào Queue trích nợ Core
    end
```

## 3. Sequence: Execution & SMS (US-03, US-05)
```mermaid
sequenceDiagram
    participant Engine as Execution Engine
    participant Core as Core Banking
    participant SMS as SMS Gateway
    participant DB as Primary DB

    Engine->>Core: Gửi lệnh trích nợ tài khoản (Debit)
    Core-->>Engine: Response: SUCCESS
    
    Engine->>SMS: Gửi thông báo trừ tiền (Send SMS)
    SMS-->>Engine: SMS Queued / Sent
    
    Engine->>DB: Update Task Status = SUCCESS
```

## 4. Sequence: AutoRetry (US-04, BR-03)
```mermaid
sequenceDiagram
    participant Engine as Execution Engine
    participant Core as Core Banking
    participant DB as Primary DB
    participant Batch as Retry Scheduler

    Engine->>Core: Gửi lệnh trích nợ
    Core-->>Engine: Response: ERR_INSUFFICIENT_FUNDS
    
    Engine->>DB: Read ProcessedFeeTask.RetryCount
    
    alt RetryCount < 10 (BR-03)
        Engine->>DB: Increment RetryCount (+1)
        Engine->>DB: Update Status = INSUFFICIENT_FUNDS
    else RetryCount == 10
        Engine->>DB: Update Status = PERMANENT_FAIL
    end
    
    Batch->>DB: Định kỳ quét các task INSUFFICIENT_FUNDS
    Batch->>Engine: Đẩy lại vào Execution Engine
```

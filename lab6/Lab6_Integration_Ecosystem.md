# Lab 6: Integration Ecosystem

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 6
**Note:** Informal integration map capturing connections based on Lab 1 (I-3, I-4, I-8). No formal ArchiMate/C4 standards applied.

---

## 1. Ecosystem Overview (As-Is / Current Style)

```mermaid
flowchart TD
    %% External Systems (I-3)
    subgraph External [External Systems]
        SrcDig[Digital Channel Source]
        SrcCard[Card Channel Source]
        SrcCorp[Corporate Channel Source]
        Params[Params System]
        CalSvc[Calendar Service]
        Core[Core Banking]
        SMS[SMS Gateway]
    end

    %% Internal Data Zone (I-9)
    subgraph DataZone [Internal Data Zone]
        DB_Fee[(Fee Database)]
        DB_Rep[(Report Database)]
    end

    %% Internal App Zone (I-9)
    subgraph AppZone [Internal App Zone]
        FIS[Fee Ingestion Service]
        FPE[Fee Processing Engine]
        CalGate[Calendar Gate]
        Exec[Execution Engine]
        Retry[Retry Scheduler]
        Notif[Notification Service]
        Proj[Report Projector]
        API_Rep[Fee Report API]
        Web[Fee Inquiry Web App]
        GW{{API Gateway}}
        Broker[[Message Broker]]
    end

    %% Actors (I-2)
    Staff((Bank Staff))
    Cust((Customer))

    %% Integrations (I-8)
    SrcDig & SrcCard & SrcCorp -- Async FileTransfer --> FIS
    FIS --> FPE
    FPE -- Read Config --> Params
    FPE -- Write (Created) --> DB_Fee

    Exec -- Poll --> DB_Fee
    Retry -- Poll / Update --> DB_Fee

    Exec -- Sync REST --> CalGate
    CalGate -- Sync REST --> CalSvc
    Exec -- Sync POST --> Core

    Exec -- Async Event --> Broker
    Broker -- Consume --> Notif
    Notif -- Sync REST/Command --> SMS
    SMS -- Delivery --> Cust

    Proj -- Sync JDBC Read --> DB_Fee
    Proj -- Sync JDBC Write --> DB_Rep

    Staff -- HTTPS --> Web
    Web -- Sync REST --> GW
    GW -- Route --> API_Rep
    API_Rep -- Read --> DB_Rep
```

---

## 2. Integration Pathways Summary

*   **Ingestion Path (Async):** Channel sources push data to the `Fee Ingestion Service`.
*   **Validation Path (Sync):** `Fee Processing Engine` calls `Params System`; `Calendar Gate` calls `Calendar Service`.
*   **Execution Path (Sync):** `Execution Engine` dispatches debits directly to `Core Banking`.
*   **Event Path (Async):** `Execution Engine` -> `Message Broker` -> `Notification Service` -> `SMS Gateway`.
*   **CQRS Sync Path (Sync/Polling):** `Report Projector` continuously mirrors state from `Fee Database` to `Report Database`.
*   **Inquiry Path (Sync):** `Fee Inquiry Web App` -> `API Gateway` -> `Fee Report API` -> `Report Database`.

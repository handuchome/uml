# Lab 9: System Modeling (C4 Context & Container)

**Project:** Bank Service Fee Collection System
**Phase:** After Pack (The Guide) - Lab 9
**Note:** Built strictly following Quality Gate G3 and Diagram Header Template defined in Lab 7.

---

## 1. C4 Level 1: System Context Diagram
*Demonstrates the overarching interactions between actors, the central system, and external systems.*

```text
Title:      C4 Context (Level 1) - Fee Collection Hub
Viewpoint:  C4 Model
Layer(s):   Business / Context
As-Is | To-Be | Transition:  To-Be
Owner:      Role SA ________  Name Hà Ngọc Bắc
RACI:       R SA__  A EA____  C Dev_  I Test
Version:    v1.0  Date 2026-08-21  Status Review
Legend:     Solid lines = Sync connections | Dashed lines = Async connections
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: Central Hub | Out-of-scope: Internal Hub details
```

```mermaid
flowchart TD
    classDef actor fill:#08427b,color:#fff,stroke:#052e56,stroke-width:2px;
    classDef system fill:#1168bd,color:#fff,stroke:#0b4884,stroke-width:2px;
    classDef external fill:#999999,color:#fff,stroke:#666666,stroke-width:2px;

    %% Actors (I-2)
    Staff((Bank Staff)):::actor
    Cust((Customer)):::actor

    %% Central System
    Hub[<<System>>
Fee Collection Hub]:::system

    %% External Systems (I-3)
    Digi[<<External System>>
Digital Channel Source]:::external
    Card[<<External System>>
Card Channel Source]:::external
    Corp[<<External System>>
Corporate Channel Source]:::external
    Params[<<External System>>
Params System]:::external
    Cal[<<External System>>
Calendar Service]:::external
    Core[<<External System>>
Core Banking]:::external
    SMS[<<External System>>
SMS Gateway]:::external

    %% High-level Context Relationships
    Digi -. "[REQ-01] Async Ingestion" .-> Hub
    Card -. "[REQ-01] Async Ingestion" .-> Hub
    Corp -. "[REQ-01] Async Ingestion" .-> Hub

    Hub -- "Sync Read" --> Params
    Hub -- "Sync Validate" --> Cal
    Hub -- "[REQ-03] Sync Debit" --> Core
    Hub -. "[REQ-05] Async/Sync Trigger" .-> SMS

    SMS -. "Deliver Notification" .-> Cust
    Staff -- "[REQ-06] Sync UI Report" --> Hub
```

---

## 2. C4 Level 2: Container Diagram
*Passes G3: Shows all internal containers (I-4) with strict sync/async labels satisfying REQ-01, REQ-03, REQ-05, REQ-06.*

```text
Title:      C4 Container (Level 2) - Fee Collection Hub
Viewpoint:  C4 Model
Layer(s):   Application
As-Is | To-Be | Transition:  To-Be
Owner:      Role SA ________  Name Hà Ngọc Bắc
RACI:       R SA__  A EA____  C Dev_  I Test
Version:    v1.0  Date 2026-08-21  Status Review
Legend:     Solid lines = Sync | Dashed lines = Async
RACI legend: R = draws · A = approves · C = consulted · I = informed
Scope:      In-scope: I-4 Containers mapping strictly to G3 synchronization rules.
```

```mermaid
flowchart TD
    classDef actor fill:#08427b,color:#fff,stroke:#052e56,stroke-width:2px;
    classDef container fill:#438dd5,color:#fff,stroke:#2e6295,stroke-width:2px;
    classDef database fill:#438dd5,color:#fff,stroke:#2e6295,stroke-width:2px,shape:cylinder;
    classDef external fill:#999999,color:#fff,stroke:#666666,stroke-width:2px;

    %% Actors
    Staff((Bank Staff)):::actor
    Cust((Customer)):::actor

    %% Externals (I-3)
    Digi[<<External System>>
Digital Channel Source]:::external
    Card[<<External System>>
Card Channel Source]:::external
    Corp[<<External System>>
Corporate Channel Source]:::external
    Params[<<External System>>
Params System]:::external
    Cal[<<External System>>
Calendar Service]:::external
    Core[<<External System>>
Core Banking]:::external
    SMS[<<External System>>
SMS Gateway]:::external

    %% Boundary
    subgraph Hub [Fee Collection Hub Boundary]
        FIS[<<Container: Service>>
Fee Ingestion Service]:::container
        FPE[<<Container: Engine>>
Fee Processing Engine]:::container
        CG[<<Container: Service>>
Calendar Gate]:::container
        EE[<<Container: Engine>>
Execution Engine]:::container
        RS[<<Container: Scheduler>>
Retry Scheduler]:::container
        MB[<<Container: Broker>>
Message Broker]:::container
        NS[<<Container: Service>>
Notification Service]:::container
        RP[<<Container: Projector>>
Report Projector]:::container
        FRA[<<Container: API>>
Fee Report API]:::container
        GW[<<Container: Gateway>>
API Gateway]:::container
        FIW[<<Container: Web App>>
Fee Inquiry Web App]:::container
        FDB[(<<Container: Database>>
Fee Database)]:::database
        RDB[(<<Container: Database>>
Report Database)]:::database
    end

    %% G3 Required Relationships (Sync/Async labels explicitly mapped to Requirements)
    Digi -. "[REQ-01] Async File Transfer" .-> FIS
    Card -. "[REQ-01] Async File Transfer" .-> FIS
    Corp -. "[REQ-01] Async File Transfer" .-> FIS

    FIS -- "Sync Forward" --> FPE
    FPE -- "Sync Read" --> Params
    FPE -- "Sync Write" --> FDB

    EE -- "Sync Poll" --> FDB
    RS -- "Sync Poll/Update" --> FDB

    EE -- "Sync REST" --> CG
    CG -- "Sync REST" --> Cal

    EE -- "[REQ-03] Sync POST /debit" --> Core

    EE -. "[REQ-05] Async Event Publish" .-> MB
    MB -. "[REQ-05] Async Event Consume" .-> NS
    NS -- "Sync REST/Command" --> SMS
    SMS -. "Async Delivery" .-> Cust

    FDB -- "Sync JDBC Read" --> RP
    RP -- "Sync JDBC Write" --> RDB

    Staff -- "Sync HTTPS" --> FIW
    FIW -- "[REQ-06] Sync UI Routing" --> GW
    GW -- "Sync REST" --> FRA
    FRA -- "Sync JDBC Read" --> RDB
```

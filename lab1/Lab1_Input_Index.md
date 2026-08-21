# Lab 1: Scopes with concrete values (Name-Identity Index)

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 1

---

## I-1. Team and topic

| Field | Your value |
|-------|------------|
| Group | Team 1 (Nguyễn Nhật Trường, Hà Ngọc Bắc, Dương Đỗ Minh, Hàn Ngọc Đức) |
| Topic / initiative name | Bank Service Fee Collection System |
| System-in-focus | Fee Collection Hub |
| Goal | Centralize and automate fee collection across multiple channels with strict calendar constraints and retry mechanisms. |
| Outcome (measurable) | 100% compliance with holiday/lunar constraints, zero manual retry effort for insufficient funds (up to 10 times). |
| Product | Fee Collection Hub |
| Contract | API Contracts for source ingestion, core debit execution, and SMS trigger. |
| Baseline → target | Fragmented manual collection → Centralized, automated, compliant collection engine with CQRS reporting. |
| In scope | `Digital Channel Source`, `Card Channel Source`, `Corporate Channel Source`, `Fee Ingestion Service`, `Fee Processing Engine`, `Params System`, `Calendar Gate`, `Execution Engine`, `Retry Scheduler`, `Notification Service`, `SMS Gateway`, `Fee Report API`, `Fee Inquiry Web App`, `Fee Database`, `Report Database`, `API Gateway`, `Message Broker`. |
| Out of scope | Ledger accounting, OTC cash collection, refunds, param creation/management, complex IAM. |

## I-2. Actors

| Name | ArchiMate | C4 (Person or —) | Role in the process |
|------|-----------|------------------|---------------------|
| Bank Staff | Business Actor | Person | View fee collection results (details, summary, insufficient funds) on the UI. |
| Customer | Business Actor | Person | Receive SMS notifications upon successful fee deduction. |

## I-3. External systems

| Name (simulated) | Responsibility |
|------------------|----------------|
| Digital Channel Source | Provide digital fee lists. |
| Card Channel Source | Provide card fee lists. |
| Corporate Channel Source | Provide corporate fee lists. |
| Params System | Provide discount rules and fee configuration. |
| Calendar Service | Provide API to check Lunar 1st and national holidays. |
| Core Banking | Execute account debit transactions. |
| SMS Gateway | Receive commands and deliver SMS to the Customer. |

## I-4. Internal containers

| Name | Responsibility |
|------|----------------|
| API Gateway | Route inquiry traffic to the reporting API. |
| Message Broker | Decouple execution success events from notifications. |
| Fee Ingestion Service | Ingest fee lists from the three source systems. |
| Fee Processing Engine | Apply policies from Params System and filter fees > 0. |
| Calendar Gate | Validate execution dates against holidays. |
| Execution Engine | Communicate with Core Banking for debits. |
| Retry Scheduler | Schedule AutoRetry for insufficient fund tasks. |
| Notification Service | Consume success events and trigger SMS Gateway. |
| Fee Report API | Provide backend reporting data (Read Store). |
| Fee Inquiry Web App | Provide the UI for Bank Staff. |
| Fee Database | Store main processing state (Write Store). |
| Report Database | Store synchronized data for inquiries (Read Store). |

## I-5. Business process (happy path)

**Object:** `ProcessedFeeTask`

1. `Fee Ingestion Service` receives lists from `Digital Channel Source`, `Card Channel Source`, and `Corporate Channel Source`.
2. `Fee Processing Engine` requests rules from `Params System`, calculates amounts, and creates `ProcessedFeeTask` for amounts > 0.
3. `Calendar Gate` validates the current date; allows processing if not a holiday/lunar 1st.
4. `Execution Engine` sends a debit command to `Core Banking` successfully.
5. `Execution Engine` publishes a success event to `Message Broker`.
6. `Notification Service` consumes the event and commands `SMS Gateway` to send an SMS to `Customer`.
7. System syncs state to `Report Database`, allowing `Bank Staff` to view results via `Fee Inquiry Web App` and `Fee Report API`.

**Principle / hard rules:**
- Absolutely no debit commands to `Core Banking` on lunar 1st or holidays.
- `Fee Inquiry Web App` must not query `Core Banking` or `Fee Database` directly.

## I-6. Named object states (use exactly on UML State)

**Object:** `ProcessedFeeTask`

| State | Trigger / event | Next state | Terminal? |
|-------|-----------------|------------|-----------|
| Created | Fee > 0 validated | Pending_Calendar | No |
| Pending_Calendar | Calendar check passed | Pending_Execution | No |
| Pending_Calendar | Calendar check failed (CON.2) | Rescheduled | No |
| Rescheduled | Next working day reached | Pending_Calendar | No |
| Pending_Execution | Debit fail (insufficient funds) | Retrying | No |
| Pending_Execution | Debit success | Completed | No |
| Retrying | Retry limit < 10 | Pending_Execution | No |
| Retrying | Retry limit = 10 (CON.3) | Failed_Permanently | No |
| Completed | None | None | Yes |
| Failed_Permanently | None | None | Yes |

**Terminal states:**
- Completed
- Failed_Permanently

## I-7. Source of truth

| Data object | Meaning | Source of truth (one container or external) |
|-------------|---------|---------------------------------------------|
| Digital RawFeeRecord | Digital fee lists | Digital Channel Source |
| Card RawFeeRecord | Card fee lists | Card Channel Source |
| Corporate RawFeeRecord | Corporate fee lists | Corporate Channel Source |
| ProcessedFeeTask | Task processing state | Fee Database |
| CalendarConstraint| Holiday rules | Calendar Service |
| FeeReport | Inquiry data | Report Database |

## I-8. Integration (label sync vs async on Container)

| Pattern | Mechanism | Example on your landscape |
|---------|-----------|---------------------------|
| Sync | REST API | `Execution Engine` calls `Core Banking` |
| Sync | REST API | `Fee Inquiry Web App` calls `Fee Report API` via `API Gateway` |
| Sync | REST API | `Calendar Gate` calls `Calendar Service` |
| Async | File/Batch | `Digital Channel Source` sends files to `Fee Ingestion Service` |
| Async | Message Event | `Execution Engine` publishes to `Message Broker`; `Notification Service` consumes |

## I-9. Deployment

| Location | What runs there |
|----------|-----------------|
| Internal App Zone | `Fee Inquiry Web App`, `Fee Report API`, `Fee Ingestion Service`, `Fee Processing Engine`, `Calendar Gate`, `Execution Engine`, `Retry Scheduler`, `Notification Service`, `API Gateway`, `Message Broker` |
| Internal Data Zone | `Fee Database`, `Report Database` |

**Forbidden path:** `Fee Inquiry Web App` must not read from `Fee Database` or `Core Banking`.

## I-10. Constraints (must appear on Motivation and on decision branches)

| ID | Constraint | Effect on the process |
|----|------------|------------------------|
| CON.1 | Fee > 0 | Filter and discard fees <= 0 after discount. |
| CON.2 | Holiday/Lunar Block | Block debits on holidays/lunar 1st; move task to Rescheduled. |
| CON.3 | AutoRetry Max 10 | Stop retrying and mark Failed_Permanently after 10 insufficient funds errors. |
| CON.4 | SMS Notification | Send SMS immediately after successful core debit. |
| CON.5 | CQRS Reporting | UI queries must use the read store, separating from the debit write flow. |

## I-11. Named use cases for UML (not every component)

| Use case | Happy path | At least one exception (`alt`) |
|----------|------------|--------------------------------|
| UC-Ingestion | Ingest lists, check params, create task | `alt`: Fee <= 0 (Discard) |
| UC-Execution | Check calendar, debit core, publish event | `alt`: Holiday (Reschedule), Insufficient funds (To Retry) |
| UC-AutoRetry | Poll retrying tasks, execute debit | `alt`: Exceed max 10 retries (Fail permanently) |
| UC-Inquiry | `Bank Staff` views report via `Fee Inquiry Web App` | `alt`: Empty result / store lag |

**One container for optional C4 Component:** `Execution Engine`
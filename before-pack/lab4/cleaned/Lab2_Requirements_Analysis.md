# Lab 2: Requirements, Analysis, and Trace Table

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 2

## 1. Requirements List
*Each requirement traces to Goal/Outcome, a CON.*, a process step, or a state.*

| Req ID | Requirement Description | Trace: Goal / Outcome | Trace: Process Step | Trace: CON.* | Trace: State |
|---|---|---|---|---|---|
| REQ-01 | `Fee Ingestion Service` receives data from `Digital Channel Source`, `Card Channel Source`, and `Corporate Channel Source`. `Fee Processing Engine` applies `Params System` policies to create tasks only if fee > 0. | Centralize and automate fee collection | Step 1 & 2 | CON.1 | `Created` |
| REQ-02 | `Calendar Gate` must block debits if the current date is a national holiday or lunar 1st, postponing them to the next working day. | 100% compliance with holiday/lunar constraints | Step 3 | CON.2 | `Pending_Calendar`, `Rescheduled` |
| REQ-03 | `Execution Engine` must execute the debit command via `Core Banking` for validated tasks. | Centralize and automate fee collection | Step 4 | N/A | `Pending_Execution`, `Completed` |
| REQ-04 | `Retry Scheduler` must automatically poll and re-queue failed tasks due to insufficient funds, up to a maximum of 10 times. | Zero manual retry effort for insufficient funds | Step 4 (Loop) | CON.3 | `Retrying`, `Failed_Permanently` |
| REQ-05 | Upon success, `Execution Engine` publishes an event to `Message Broker`, triggering `Notification Service` to command `SMS Gateway` to send an SMS to `Customer`. | Centralize and automate fee collection | Step 5 & 6 | CON.4 | `Completed` |
| REQ-06 | `Report Projector` must sync the state from `Fee Database` to `Report Database` so `Bank Staff` can view reports via `Fee Inquiry Web App` and `Fee Report API`. | CQRS reporting | Step 7 | CON.5 | N/A |

## 2. Analysis

### As-is vs To-be
| Aspect | As-is (Baseline) | To-be (Target) |
|---|---|---|
| **Data Ingestion** | Fragmented manual collection from multiple channels. | Centralized ingestion via `Fee Ingestion Service`. |
| **Calendar Check** | Manual check, high risk of violation. | Automated 100% compliance via `Calendar Gate`. |
| **Exception Handling** | Manual retry effort for insufficient funds. | Zero manual retry effort via `Retry Scheduler` (up to 10 limits). |
| **Reporting** | Querying the main write database directly. | CQRS reporting via `Report Projector` and `Report Database`. |

### Capabilities implied by the goal
- **Multi-channel Integration:** Capability to ingest structured data from `Digital Channel Source`, `Card Channel Source`, and `Corporate Channel Source`.
- **Rule Engine / Filtering:** Capability to calculate and drop invalid records (CON.1) using `Params System`.
- **Time-awareness:** Strict calendar validation before hitting `Core Banking` (CON.2).
- **Automated Scheduling:** Independent polling and retrying mechanism via `Retry Scheduler` (CON.3).
- **Event-driven Asynchrony:** Decoupling core processing from notifications via `Message Broker` (CON.4).

### Exception paths named
- **Path 1: Fee Discard.** Trigger: Fee <= 0 (CON.1). Action: No `ProcessedFeeTask` is created.
- **Path 2: Holiday/Lunar Block.** Trigger: `Calendar Gate` returns true for holiday. Action: Task shifts to `Rescheduled` state.
- **Path 3: Insufficient Funds.** Trigger: `Core Banking` rejects the debit. Action: Task shifts to `Retrying` state.
- **Path 4: Max Retries Exceeded.** Trigger: Retry limit reaches 10 (CON.3). Action: Task shifts to terminal `Failed_Permanently` state.

## 3. Trace Table
*Trace ID -> process step -> CON.* -> named object/state*

| Requirement ID | Process Step (I-5) | CON.* (I-10) | Named Object / State (I-6) |
|---|---|---|---|
| REQ-01 | Step 1 & 2 (Ingestion & Param Check) | CON.1 | `ProcessedFeeTask` / `Created` |
| REQ-02 | Step 3 (Calendar validation) | CON.2 | `ProcessedFeeTask` / `Pending_Calendar`, `Rescheduled` |
| REQ-03 | Step 4 (Core execution) | N/A | `ProcessedFeeTask` / `Pending_Execution`, `Completed` |
| REQ-04 | Step 4 Loop (AutoRetry logic) | CON.3 | `ProcessedFeeTask` / `Retrying`, `Pending_Execution`, `Failed_Permanently` |
| REQ-05 | Step 5 & 6 (Message Broker & SMS) | CON.4 | `ProcessedFeeTask` / `Completed` |
| REQ-06 | Step 7 (Report Projector sync) | CON.5 | `FeeReport` / N/A |
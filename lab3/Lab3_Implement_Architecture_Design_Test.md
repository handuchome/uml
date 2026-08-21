# Lab 3: Implement Architecture, Design, and Test

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 3

---

## 1. Build List
*Every I-4 container: owner (Dev name), build order (1…n), environment from I-9.*

| Build Order | Container (I-4 Name) | Environment (I-9 Location) | Owner |
|---|---|---|---|
| 1 | `Fee Database` | Internal Data Zone | DBA Team |
| 2 | `Report Database` | Internal Data Zone | DBA Team |
| 3 | `Message Broker` | Internal App Zone | Infra Team |
| 4 | `API Gateway` | Internal App Zone | Infra Team |
| 5 | `Fee Ingestion Service` | Internal App Zone | Backend Dev A |
| 6 | `Fee Processing Engine` | Internal App Zone | Backend Dev A |
| 7 | `Calendar Gate` | Internal App Zone | Backend Dev B |
| 8 | `Execution Engine` | Internal App Zone | Backend Dev B |
| 9 | `Retry Scheduler` | Internal App Zone | Backend Dev A |
| 10 | `Notification Service` | Internal App Zone | Integration Dev |
| 11 | `Report Projector` | Internal App Zone | Backend Dev C |
| 12 | `Fee Report API` | Internal App Zone | API Dev |
| 13 | `Fee Inquiry Web App` | Internal App Zone | Frontend Dev |

---

## 2. Contract Register
*One row per I-8 relationship: producer, consumer, sync or async, operation or event name.*

| Producer (Provider) | Consumer (Caller) | Sync/Async | Operation / Event Name |
|---|---|---|---|
| `Digital Channel Source` | `Fee Ingestion Service` | Async | `FileTransfer / Batch` |
| `Card Channel Source` | `Fee Ingestion Service` | Async | `FileTransfer / Batch` |
| `Corporate Channel Source` | `Fee Ingestion Service` | Async | `FileTransfer / Batch` |
| `Calendar Service` | `Calendar Gate` | Sync | `GET /api/calendar/check` |
| `Core Banking` | `Execution Engine` | Sync | `POST /api/v1/core/debit` |
| `Execution Engine` | `Message Broker` | Async | `Publish: DebitSuccessEvent` |
| `Message Broker` | `Notification Service` | Async | `Consume: DebitSuccessEvent` |
| `Fee Database` | `Report Projector` | Sync | `JDBC / Read` |
| `Fee Report API` | `Fee Inquiry Web App` | Sync | `GET /api/reports` (Routed via `API Gateway`) |

---

## 3. To-be Component
*Modules inside the one I-11 container (`Execution Engine`); neighbours as black boxes.*

**Selected Container (I-11):** `Execution Engine`

**Internal Modules:**
- `TaskPoller`: Polls tasks in `Pending_Calendar` state from the database.
- `DebitDispatcher`: Constructs the payload and coordinates the debit flow.
- `CoreClient`: The HTTP client wrapping communication with the external core system.
- `EventPublisher`: Constructs and publishes events upon successful processing.
- `StatusUpdater`: Persists state changes back to the database.

**Neighbour Black Boxes:**
- `Fee Database` (Storage)
- `Calendar Gate` (Internal Validator)
- `Core Banking` (External Executor)
- `Message Broker` (Event Router)

---

## 4. To-be Sequence
*Named use case: `UC-Execution`. Each message owned by a module or a neighbour container.*

```text
[Neighbour] Fee Database
[Module] TaskPoller (inside Execution Engine)
[Neighbour] Calendar Gate
[Module] StatusUpdater (inside Execution Engine)
[Module] DebitDispatcher (inside Execution Engine)
[Module] CoreClient (inside Execution Engine)
[Neighbour] Core Banking
[Module] EventPublisher (inside Execution Engine)
[Neighbour] Message Broker

1. TaskPoller -> Fee Database: Query ProcessedFeeTask (State: Pending_Calendar)
2. TaskPoller -> Calendar Gate: Validate current date
alt [CON.2 Holiday/Lunar Block]
    3a. Calendar Gate -> TaskPoller: Return Blocked
    4a. TaskPoller -> StatusUpdater: Command state change
    5a. StatusUpdater -> Fee Database: Update ProcessedFeeTask to Rescheduled
else [Normal Working Day]
    3b. Calendar Gate -> TaskPoller: Return Allowed
    4b. TaskPoller -> StatusUpdater: Command state change
    5b. StatusUpdater -> Fee Database: Update ProcessedFeeTask to Pending_Execution
    
    6. TaskPoller -> DebitDispatcher: Initiate Debit
    7. DebitDispatcher -> CoreClient: Execute
    8. CoreClient -> Core Banking: POST /debit
    
    alt [CON.3 Insufficient Funds]
        9a. Core Banking -> CoreClient: 400 Insufficient Funds
        10a. CoreClient -> DebitDispatcher: Return Error
        11a. DebitDispatcher -> StatusUpdater: Command state change
        12a. StatusUpdater -> Fee Database: Update ProcessedFeeTask to Retrying
    else [Debit Success]
        9b. Core Banking -> CoreClient: 200 OK
        10b. CoreClient -> DebitDispatcher: Return Success
        11b. DebitDispatcher -> StatusUpdater: Command state change
        12b. StatusUpdater -> Fee Database: Update ProcessedFeeTask to Completed
        13b. DebitDispatcher -> EventPublisher: Trigger Notification
        14b. EventPublisher -> Message Broker: Publish DebitSuccessEvent (CON.4)
    end
end
```

---

## 5. Exception Spec
*Critical failure path from CON.*: trigger, compensating action, who performs it.*

| Critical Failure Path | Trigger | Compensating Action | Who performs it (I-4 Name) |
|---|---|---|---|
| CON.1: Fee <= 0 | `Params System` logic results in fee amount 0 or negative. | Discard the record entirely. No `ProcessedFeeTask` is created. | `Fee Processing Engine` |
| CON.2: Holiday/Lunar Block | `Calendar Gate` returns true for holiday or lunar 1st. | Halt execution. Move task to `Rescheduled` to wait for the next working day. | `Execution Engine` |
| CON.3: AutoRetry Max 10 | Debit fails due to insufficient funds and retry count hits 10. | Stop retrying. Mark the task as `Failed_Permanently`. | `Retry Scheduler` |

---

## 6. Test Spec
*One row per I-6 transition and per sequence `alt`: ID, SUT (I-4 name), expected result.*

| Test ID | Mapped I-6 Transition / Sequence `alt` | SUT (I-4 Name) | Expected Result |
|---|---|---|---|
| TS-01 | `alt`: Fee <= 0 (CON.1) | `Fee Processing Engine` | Task is discarded. |
| TS-02 | Transition: `Created` -> `Pending_Calendar` | `Fee Processing Engine` | Valid task is persisted and ready for calendar check. |
| TS-03 | `alt`: Holiday/Lunar Block (CON.2) | `Execution Engine` | Debit flow is halted before hitting Core Banking. |
| TS-04 | Transition: `Pending_Calendar` -> `Rescheduled` | `Execution Engine` | Task state is updated correctly upon holiday block. |
| TS-05 | Transition: `Pending_Calendar` -> `Pending_Execution` | `Execution Engine` | Task state is updated upon passing calendar validation. |
| TS-06 | `alt`: Insufficient Funds | `Execution Engine` | Error is handled gracefully without crashing the engine. |
| TS-07 | Transition: `Pending_Execution` -> `Retrying` | `Execution Engine` | Task state is moved to Retrying upon funds failure. |
| TS-08 | Transition: `Pending_Execution` -> `Completed` | `Execution Engine` | State is Completed and event is sent to Message Broker. |
| TS-09 | Transition: `Rescheduled` -> `Pending_Calendar` | `Retry Scheduler` | Task is picked up on the next working day. |
| TS-10 | Transition: `Retrying` -> `Pending_Execution` | `Retry Scheduler` | Task is re-queued for execution (retry count < 10). |
| TS-11 | `alt`: Exceed max 10 retries (CON.3) | `Retry Scheduler` | Scheduler recognizes the limit and halts retry logic. |
| TS-12 | Transition: `Retrying` -> `Failed_Permanently` | `Retry Scheduler` | Task state is finalized as Failed_Permanently. |

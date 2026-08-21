# Lab 3: To-be Component and Sequence

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 3

## 1. To-be Component (Execution Engine)

*Modules inside the **one** I-11 container (Execution Engine); neighbours as black boxes.*

**Selected Container (I-11):** `Execution Engine`

**Internal Modules:**
- `TaskPoller`: Đọc các task có trạng thái `Pending_Execution` từ database.
- `DebitDispatcher`: Xây dựng payload và gọi sang CoreClient.
- `CoreClient`: Module giao tiếp trực tiếp với external Core Banking.
- `EventPublisher`: Bắn event sang Notification Service khi thành công.
- `StatusUpdater`: Cập nhật trạng thái vào Fee Database.

**Neighbour black boxes:**
- `Calendar Gate` (Upstream)
- `Fee Database` (State storage)
- `Core Banking` (External target)
- `Notification Service` (Downstream async)

## 2. To-be Sequence: UC-Execution

*Named use case: `UC-Execution`. Each message owned by a module or a neighbour container.*

```text
[Neighbour] Fee Database (Contains ProcessedFeeTask)
[Module] TaskPoller (inside Execution Engine)
[Neighbour] Calendar Gate
[Module] DebitDispatcher (inside Execution Engine)
[Module] CoreClient (inside Execution Engine)
[Neighbour] Core Banking
[Module] StatusUpdater (inside Execution Engine)
[Module] EventPublisher (inside Execution Engine)
[Neighbour] Notification Service

1. TaskPoller -> Fee Database: Lấy danh sách ProcessedFeeTask (Pending_Calendar)
2. TaskPoller -> Calendar Gate: Kiểm tra ngày hiện tại
alt [Ngày Lễ / Mùng 1 Âm (CON.2)]
    3a. Calendar Gate -> TaskPoller: Trả về IsHoliday = True
    4a. TaskPoller -> StatusUpdater: Đổi trạng thái thành Rescheduled
    5a. StatusUpdater -> Fee Database: Update(Rescheduled)
else [Ngày Thường]
    3b. Calendar Gate -> TaskPoller: Trả về IsHoliday = False
    4b. TaskPoller -> StatusUpdater: Đổi trạng thái thành Pending_Execution
    5b. StatusUpdater -> Fee Database: Update(Pending_Execution)

    6. TaskPoller -> DebitDispatcher: Giao việc trích nợ
    7. DebitDispatcher -> CoreClient: ExecuteDebit(SoTienPhi)
    8. CoreClient -> Core Banking: POST /debit

    alt [Lỗi số dư (CON.3)]
        9a. Core Banking -> CoreClient: 400 Insufficient Funds
        10a. CoreClient -> DebitDispatcher: Fail
        11a. DebitDispatcher -> StatusUpdater: Đổi trạng thái Retrying, Tăng RetryCount
        12a. StatusUpdater -> Fee Database: Update(Retrying)
    else [Thành công]
        9b. Core Banking -> CoreClient: 200 OK
        10b. CoreClient -> DebitDispatcher: Success
        11b. DebitDispatcher -> StatusUpdater: Đổi trạng thái Completed
        12b. StatusUpdater -> Fee Database: Update(Completed)
        13b. DebitDispatcher -> EventPublisher: Trigger SMS
        14b. EventPublisher -> Notification Service: Emit(DebitSuccessEvent) (CON.4)
    end
end
```

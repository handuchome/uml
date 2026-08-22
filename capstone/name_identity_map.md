# Name-Identity Mapping

> **Collapse Architecture Documented:** The entire system is collapsed into **One Process** (FastAPI in `src/main.py`), using an **In-memory store** (Python Dict/List), and an **In-process bus** (Observer Pattern).

## Zones
| Zone | Location | Contents |
|---|---|---|
| Internal App Zone | Single Python process | All I-4 Containers listed below |
| Internal Data Zone | Same process (in-memory) | `Fee Database` (Write Store), `Report Database` (Read Store) |

## Internal Containers (I-4)
| I-4 Container | Package/Module Path | Class Name (Python) |
|---|---|---|
| API Gateway | `src/infrastructure/api_gateway.py` | `APIGateway` |
| Message Broker | `src/infrastructure/message_broker.py` | `InMemoryMessageBroker` |
| Fee Ingestion Service | `src/containers/fee_ingestion_service.py` | `FeeIngestionService` |
| Fee Processing Engine | `src/containers/fee_processing_engine.py` | `FeeProcessingEngine` |
| Calendar Gate | `src/containers/calendar_gate.py` | `CalendarGate` |
| Execution Engine | `src/containers/execution_engine/` (L3 Decomposed) | `TaskPoller`, `DebitDispatcher`, `CoreClient`, `EventPublisher`, `StatusUpdater` |
| Retry Scheduler | `src/containers/retry_scheduler.py` | `RetryScheduler` |
| Notification Service | `src/containers/notification_service.py` | `NotificationService` |
| Report Projector | `src/storage/report_projector.py` | `ReportProjector` |
| Fee Report API | `src/containers/fee_report_api.py` | `FeeReportAPI` |
| Fee Inquiry Web App | N/A | N/A (Out of scope — simulated via HTTP TestClient) |

## Data Stores
| Data Store | Package/Module Path | Class Name (Python) |
|---|---|---|
| Fee Database | `src/storage/fee_database.py` | `FeeDatabase` (Write Store) |
| Report Database | `src/storage/report_database.py` | `ReportDatabase` (Read Store) |

## Object
- `ProcessedFeeTask` (`src/domain/processed_fee_task.py`)
  - States: `Created`, `Pending_Calendar`, `Rescheduled`, `Pending_Execution`, `Retrying`, `Completed`, `Failed_Permanently`.

## ASSUMPTIONS (Dev & Test Implementations)
- **APIs:** The 4 trigger APIs (`POST /api/ingestion/trigger`, `POST /api/execution/run`, `POST /api/retry/poll`, `GET /api/reports`) are implemented to facilitate automated testing of the landscape collapse in a single sitting. The original Lab 3 APIs (`GET /api/calendar/check`, `POST /api/v1/core/debit`) are internal module boundaries in this collapse.
- **Mocks:** We assume string tokens `HOLIDAY` in date triggers Calendar block, and `POOR_*` in account triggers Core Banking insufficient funds. `DIGI` is an assumed channel. Only 4 out of 7 I-3 mocks are fully implemented in code as the other 3 (Channel Sources) are replaced by the HTTP Ingestion trigger.

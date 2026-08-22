# Specification Traceability

## Participant = SUT Mapping
| Test Function | SUT (System Under Test) | I-4 Container |
|---|---|---|
| `test_ts01_con1_fee_less_than_zero` | `POST /api/ingestion/trigger` | Fee Processing Engine |
| `test_ts02_transition_created_to_pending_calendar` | `POST /api/ingestion/trigger` | Fee Processing Engine |
| `test_ts03_ts04_con2_holiday_block` | `POST /api/execution/run` | Calendar Gate |
| `test_ts05_ts08_con4_transition_to_completed_with_sms` | `POST /api/execution/run` | Calendar Gate → Execution Engine |
| `test_ts06_ts07_insufficient_funds_to_retrying` | `POST /api/execution/run` | Execution Engine |
| `test_ts09_ts10_ts11_ts12_con3_max_retry_flow` | `POST /api/retry/poll` | Retry Scheduler |
| `test_ts09_rescheduled_requeue` | `POST /api/retry/poll` | Retry Scheduler |
| `test_cqrs_reporting_and_api_responses` | `GET /api/reports` | API Gateway → Fee Report API |
| `test_i5_negative_bypass_calendar_rejected` | `DebitDispatcher.initiate_debit()` | Execution Engine |
| `test_i9_negative_forbidden_db_access` | `FeeReportAPI.__init__()` | Fee Report API |

## Use Case → Test Spec Trace
| Use Case | OpenAPI Endpoint | Package/Module | Test ID | Description |
|---|---|---|---|---|
| UC-Ingestion | `POST /api/ingestion/trigger` | `src/containers/fee_ingestion_service.py` | TS-01 | Discard fee <= 0 (CON.1) |
| UC-Ingestion | `POST /api/ingestion/trigger` | `src/containers/fee_processing_engine.py` | TS-02 | Created -> Pending_Calendar |
| UC-Execution | `POST /api/execution/run` | `src/containers/calendar_gate.py` | TS-03, TS-04 | Holiday/Lunar Block -> Rescheduled (CON.2) |
| UC-Execution | `POST /api/execution/run` | `src/containers/execution_engine/*` | TS-05 | Pending_Calendar -> Pending_Execution -> Completed |
| UC-Execution | `POST /api/execution/run` | `src/containers/execution_engine/*` | TS-06, TS-07 | Insufficient funds -> Retrying |
| UC-Execution | `POST /api/execution/run` | `src/containers/notification_service.py` | TS-08 | DebitSuccessEvent -> SMS (CON.4) |
| UC-AutoRetry | `POST /api/retry/poll` | `src/containers/retry_scheduler.py` | TS-09 | Rescheduled -> Pending_Calendar |
| UC-AutoRetry | `POST /api/retry/poll` | `src/containers/retry_scheduler.py` | TS-10, TS-11, TS-12 | Retrying -> re-debit; CON.3 max 10 -> Failed_Permanently |
| UC-Inquiry | `GET /api/reports` | `src/containers/fee_report_api.py` | TS-Inquiry | Query reports from Report Database (CQRS Read) |

## N/A Rows (Out of Scope / Collapse Internalized)
| Use Case / Actor | Reason |
|---|---|
| Fee Inquiry Web App | Replaced by HTTP client simulation (Out of scope for API implementation) |
| `GET /api/calendar/check` | Internalized as `CalendarGate.poll_and_validate()` in collapse |
| `POST /api/v1/core/debit` | Internalized as `DebitDispatcher.initiate_debit()` in collapse |

## Negative Tests (Hard Rules Verification)
| Hard Rule / Constraint | Test ID | SUT | Validation |
|---|---|---|---|
| **I-5 Violation** | `test_i5_negative_bypass_calendar_rejected` | `DebitDispatcher` (production) | Task not in `Pending_Execution` -> `PermissionError` |
| **I-9 Violation** | `test_i9_negative_forbidden_db_access` | `FeeReportAPI` (production) | Rejects `FeeDatabase` / `MockCoreBanking`; only `ReportDatabase` answers |

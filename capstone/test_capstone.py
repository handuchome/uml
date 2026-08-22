import pytest
from fastapi.testclient import TestClient
from src.main import app, fee_db, report_db, sms_gateway
from src.domain.processed_fee_task import TaskState, ProcessedFeeTask

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_state():
    fee_db.tasks.clear()
    report_db.reports.clear()
    sms_gateway.sent_messages.clear()

# ---------------------------------------------------------------------------
# UC-Ingestion
# ---------------------------------------------------------------------------

def test_ts01_con1_fee_less_than_zero():
    """TS-01 | SUT = Fee Processing Engine | CON.1: Fee <= 0 discarded (200 + 0 count)"""
    resp = client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t1", "account_id": "ACC1", "amount": 0, "channel": "DIGI", "date": "2026-08-22"}
        ]
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["processed_count"] == 0
    assert "t1" not in fee_db.tasks

def test_ts02_transition_created_to_pending_calendar(monkeypatch):
    """TS-02 | SUT = Fee Processing Engine | Created -> Pending_Calendar via HTTP ingest"""
    created_state_observed = []
    original_insert = fee_db.insert

    def intercept_insert(task):
        created_state_observed.append(task.state)
        original_insert(task)

    monkeypatch.setattr(fee_db, "insert", intercept_insert)

    resp = client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t2", "account_id": "ACC2", "amount": 100, "channel": "DIGI", "date": "2026-08-22"}
        ]
    })
    assert resp.status_code == 200
    assert TaskState.Created in created_state_observed   # mid-state observed
    assert fee_db.tasks["t2"].state == TaskState.Pending_Calendar  # after-state

# ---------------------------------------------------------------------------
# UC-Execution
# ---------------------------------------------------------------------------

def test_ts03_ts04_con2_holiday_block():
    """TS-03/04 | SUT = Calendar Gate | CON.2: Holiday -> Rescheduled (200 + compensate)"""
    client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t3", "account_id": "ACC3", "amount": 100, "channel": "DIGI", "date": "2026-08-22 HOLIDAY"}
        ]
    })
    resp = client.post("/api/execution/run")
    assert resp.status_code == 200
    assert fee_db.tasks["t3"].state == TaskState.Rescheduled

def test_ts05_ts08_con4_transition_to_completed_with_sms():
    """TS-05/08 | SUT = Calendar Gate + Execution Engine | Pending_Execution observed, then Completed + SMS (CON.4)"""
    client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t4", "account_id": "ACC4", "amount": 100, "channel": "DIGI", "date": "2026-08-22"}
        ]
    })

    # Step 1: Gate only — observe Pending_Execution mid-state
    from src.main import calendar_gate
    calendar_gate.poll_and_validate()
    assert fee_db.tasks["t4"].state == TaskState.Pending_Execution

    # Step 2: Engine — Completed + SMS
    resp = client.post("/api/execution/run")
    assert resp.status_code == 200
    assert fee_db.tasks["t4"].state == TaskState.Completed
    assert len(sms_gateway.sent_messages) == 1
    assert sms_gateway.sent_messages[0]["customer_id"] == "ACC4"

def test_ts06_ts07_insufficient_funds_to_retrying():
    """TS-06/07 | SUT = Execution Engine | CON.3: Insufficient Funds -> Retrying (200 + compensate)"""
    client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t5", "account_id": "POOR_ACC", "amount": 100, "channel": "DIGI", "date": "2026-08-22"}
        ]
    })
    resp = client.post("/api/execution/run")
    assert resp.status_code == 200
    assert fee_db.tasks["t5"].state == TaskState.Retrying

# ---------------------------------------------------------------------------
# UC-AutoRetry
# ---------------------------------------------------------------------------

def test_ts09_ts10_ts11_ts12_con3_max_retry_flow():
    """TS-09..12 | SUT = Retry Scheduler | CON.3: 10x retry -> Failed_Permanently"""
    client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t6", "account_id": "POOR_ACC", "amount": 100, "channel": "DIGI", "date": "2026-08-22"}
        ]
    })
    client.post("/api/execution/run")
    assert fee_db.tasks["t6"].state == TaskState.Retrying

    for i in range(1, 11):
        resp = client.post("/api/retry/poll")
        assert resp.status_code == 200
        if i < 10:
            assert fee_db.tasks["t6"].state == TaskState.Retrying
            assert fee_db.tasks["t6"].retry_count == i
        else:
            assert fee_db.tasks["t6"].state == TaskState.Failed_Permanently
            assert fee_db.tasks["t6"].retry_count == 10

def test_ts09_rescheduled_requeue():
    """TS-09 | SUT = Retry Scheduler | Rescheduled -> Pending_Calendar via POST /api/retry/poll"""
    client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t_resched", "account_id": "ACC", "amount": 10, "channel": "DIGI", "date": "2026-08-22 HOLIDAY"}
        ]
    })
    client.post("/api/execution/run")
    assert fee_db.tasks["t_resched"].state == TaskState.Rescheduled

    # Retry poll requeues Rescheduled -> Pending_Calendar
    resp = client.post("/api/retry/poll")
    assert resp.status_code == 200
    assert fee_db.tasks["t_resched"].state == TaskState.Pending_Calendar

# ---------------------------------------------------------------------------
# UC-Inquiry
# ---------------------------------------------------------------------------

def test_cqrs_reporting_and_api_responses():
    """TS-Inquiry | SUT = API Gateway + Fee Report API | CQRS Read from Report Database"""
    resp = client.get("/api/reports")
    assert resp.status_code == 404

    client.post("/api/ingestion/trigger", json={
        "records": [
            {"id": "t7", "account_id": "ACC7", "amount": 100, "channel": "DIGI", "date": "2026-08-22"}
        ]
    })

    resp = client.get("/api/reports")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == "t7"

# ---------------------------------------------------------------------------
# Negative Tests (Hard Rules)
# ---------------------------------------------------------------------------

def test_i5_negative_bypass_calendar_rejected():
    """I-5 | SUT = DebitDispatcher (production) | Task not in Pending_Execution -> PermissionError"""
    from src.containers.execution_engine.debit_dispatcher import DebitDispatcher
    from src.main import core_client, status_updater, event_publisher

    dispatcher = DebitDispatcher(core_client, status_updater, event_publisher)
    task = ProcessedFeeTask(id="bypass", account_id="ACC", amount=50, date="2026-08-22")
    task.state = TaskState.Created

    with pytest.raises(PermissionError) as exc_info:
        dispatcher.initiate_debit(task)
    assert "I-5 Violation" in str(exc_info.value)

def test_i9_negative_forbidden_db_access():
    """I-9 | SUT = FeeReportAPI (production) | Reject FeeDatabase & CoreBanking, assert ReportDatabase answered"""
    from src.containers.fee_report_api import FeeReportAPI
    from src.main import fee_db, core_banking, report_db

    # 1. Reject Fee Database (Write Store)
    with pytest.raises(PermissionError) as exc_info:
        FeeReportAPI(fee_db)
    assert "I-9 Violation" in str(exc_info.value)

    # 2. Reject Core Banking (External System)
    with pytest.raises(PermissionError) as exc_info:
        FeeReportAPI(core_banking)
    assert "I-9 Violation" in str(exc_info.value)

    # 3. Assert Report Database answered successfully
    report_db.insert_all([{"id": "valid_r1", "account_id": "ACC1", "amount": 100, "state": "Completed", "date": "2026-08-22"}])
    valid_api = FeeReportAPI(report_db)
    result = valid_api.get_reports()
    assert len(result) == 1
    assert result[0]["id"] == "valid_r1"

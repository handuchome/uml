from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
import os
import sys

# Support absolute imports for tests and local execution
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.domain.processed_fee_task import RawFeeRecord
from src.infrastructure.mocks.mocks import MockParamsSystem, MockCalendarService, MockCoreBanking, MockSMSGateway
from src.infrastructure.message_broker import InMemoryMessageBroker
from src.infrastructure.api_gateway import APIGateway
from src.storage.fee_database import FeeDatabase
from src.storage.report_database import ReportDatabase
from src.storage.report_projector import ReportProjector
from src.containers.fee_processing_engine import FeeProcessingEngine
from src.containers.fee_ingestion_service import FeeIngestionService
from src.containers.calendar_gate import CalendarGate
from src.containers.execution_engine.status_updater import StatusUpdater
from src.containers.execution_engine.core_client import CoreClient
from src.containers.execution_engine.event_publisher import EventPublisher
from src.containers.execution_engine.debit_dispatcher import DebitDispatcher
from src.containers.execution_engine.task_poller import TaskPoller
from src.containers.retry_scheduler import RetryScheduler
from src.containers.notification_service import NotificationService
from src.containers.fee_report_api import FeeReportAPI

app = FastAPI(title="Fee Collection Hub", version="1.0.0")

# Setup Architecture (In-memory single process setup)
fee_db = FeeDatabase()
report_db = ReportDatabase()
broker = InMemoryMessageBroker()

params_system = MockParamsSystem()
calendar_service = MockCalendarService()
core_banking = MockCoreBanking()
sms_gateway = MockSMSGateway()

notification_service = NotificationService(sms_gateway)
broker.subscribe(notification_service)

processing_engine = FeeProcessingEngine(fee_db, params_system)
ingestion_service = FeeIngestionService(processing_engine)

calendar_gate = CalendarGate(calendar_service, fee_db)
status_updater = StatusUpdater(fee_db)
core_client = CoreClient(core_banking)
event_publisher = EventPublisher(broker)
debit_dispatcher = DebitDispatcher(core_client, status_updater, event_publisher)
task_poller = TaskPoller(fee_db, debit_dispatcher)

retry_scheduler = RetryScheduler(fee_db, debit_dispatcher, status_updater)
report_projector = ReportProjector(fee_db, report_db)

report_api = FeeReportAPI(report_db)
gateway = APIGateway(report_api)

class IngestionRequest(BaseModel):
    records: List[RawFeeRecord]

@app.post("/api/ingestion/trigger")
def trigger_ingestion(req: IngestionRequest):
    if not req.records:
        raise HTTPException(status_code=400, detail="Empty records")
    results = ingestion_service.ingest(req.records)
    report_projector.sync()
    return {"message": "Successfully ingested", "processed_count": sum(results)}

@app.post("/api/execution/run")
def trigger_execution():
    calendar_gate.poll_and_validate()
    count = task_poller.run()
    report_projector.sync()
    return {"message": "Execution Engine triggered", "processed_count": count}

@app.post("/api/retry/poll")
def poll_retry():
    count = retry_scheduler.poll()
    if count == 0:
        raise HTTPException(status_code=404, detail="No tasks found to retry")
    report_projector.sync()
    return {"message": "Polling triggered successfully", "retried_count": count}

@app.get("/api/reports")
def get_reports():
    reports = gateway.get_reports()
    if not reports:
        raise HTTPException(status_code=404, detail="Report not found")
    return reports

from enum import Enum
from pydantic import BaseModel

class TaskState(str, Enum):
    Created = "Created"
    Pending_Calendar = "Pending_Calendar"
    Rescheduled = "Rescheduled"
    Pending_Execution = "Pending_Execution"
    Retrying = "Retrying"
    Completed = "Completed"
    Failed_Permanently = "Failed_Permanently"

class RawFeeRecord(BaseModel):
    id: str
    account_id: str
    amount: float
    channel: str
    date: str

class ProcessedFeeTask:
    def __init__(self, id: str, account_id: str, amount: float, date: str):
        self.id = id
        self.account_id = account_id
        self.amount = amount
        self.date = date
        self.state = TaskState.Created
        self.retry_count = 0

    def ready_for_calendar(self):
        self.state = TaskState.Pending_Calendar

    def reschedule(self):
        self.state = TaskState.Rescheduled

    def ready_for_execution(self):
        self.state = TaskState.Pending_Execution

    def mark_retrying(self):
        self.state = TaskState.Retrying

    def mark_completed(self):
        self.state = TaskState.Completed

    def fail_permanently(self):
        self.state = TaskState.Failed_Permanently
        
    def increment_retry(self):
        self.retry_count += 1

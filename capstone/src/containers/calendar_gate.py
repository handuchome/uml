from src.infrastructure.mocks.mocks import MockCalendarService
from src.storage.fee_database import FeeDatabase
from src.domain.processed_fee_task import TaskState

class CalendarGate:
    def __init__(self, calendar_service: MockCalendarService, fee_db: FeeDatabase):
        self.calendar_service = calendar_service
        self.fee_db = fee_db

    def poll_and_validate(self):
        tasks = self.fee_db.get_tasks_by_state(TaskState.Pending_Calendar)
        for task in tasks:
            if self.calendar_service.check_holiday_or_lunar(task.date):
                task.reschedule()
                self.fee_db.update(task)
            else:
                task.ready_for_execution()
                self.fee_db.update(task)

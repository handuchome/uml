from src.storage.fee_database import FeeDatabase
from src.containers.execution_engine.debit_dispatcher import DebitDispatcher
from src.containers.execution_engine.status_updater import StatusUpdater
from src.domain.processed_fee_task import TaskState

class RetryScheduler:
    def __init__(self, fee_db: FeeDatabase, debit_dispatcher: DebitDispatcher, status_updater: StatusUpdater):
        self.fee_db = fee_db
        self.debit_dispatcher = debit_dispatcher
        self.status_updater = status_updater

    def poll(self):
        tasks = self.fee_db.get_tasks_by_state(TaskState.Retrying)
        rescheduled_tasks = self.fee_db.get_tasks_by_state(TaskState.Rescheduled)
        
        processed_count = 0
        for task in rescheduled_tasks:
            task.ready_for_calendar()
            self.status_updater.save(task)
            processed_count += 1
        for task in tasks:
            if task.retry_count >= 10:
                task.fail_permanently()
                self.status_updater.save(task)
            else:
                task.increment_retry()
                task.ready_for_execution()
                self.status_updater.save(task)
                self.debit_dispatcher.initiate_debit(task)
                if task.state == TaskState.Retrying and task.retry_count >= 10:
                    task.fail_permanently()
                    self.status_updater.save(task)
            processed_count += 1
        return processed_count

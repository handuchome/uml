from src.storage.fee_database import FeeDatabase
from src.containers.execution_engine.debit_dispatcher import DebitDispatcher
from src.domain.processed_fee_task import TaskState

class TaskPoller:
    def __init__(self, fee_db: FeeDatabase, debit_dispatcher: DebitDispatcher):
        self.fee_db = fee_db
        self.debit_dispatcher = debit_dispatcher

    def run(self):
        tasks = self.fee_db.get_tasks_by_state(TaskState.Pending_Execution)
        processed_count = 0
        for task in tasks:
            self.debit_dispatcher.initiate_debit(task)
            processed_count += 1
        return processed_count

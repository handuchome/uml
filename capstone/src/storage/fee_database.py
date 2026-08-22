from typing import Dict, List
from src.domain.processed_fee_task import ProcessedFeeTask, TaskState

class FeeDatabase:
    def __init__(self):
        self.tasks: Dict[str, ProcessedFeeTask] = {}

    def insert(self, task: ProcessedFeeTask):
        self.tasks[task.id] = task

    def update(self, task: ProcessedFeeTask):
        self.tasks[task.id] = task

    def get_tasks_by_state(self, state: TaskState) -> List[ProcessedFeeTask]:
        return [t for t in self.tasks.values() if t.state == state]
    
    def get(self, task_id: str) -> ProcessedFeeTask:
        return self.tasks.get(task_id)

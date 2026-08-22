from src.containers.execution_engine.core_client import CoreClient
from src.containers.execution_engine.status_updater import StatusUpdater
from src.containers.execution_engine.event_publisher import EventPublisher
from src.domain.processed_fee_task import TaskState

class DebitDispatcher:
    def __init__(self, core_client: CoreClient, status_updater: StatusUpdater, event_publisher: EventPublisher):
        self.core_client = core_client
        self.status_updater = status_updater
        self.event_publisher = event_publisher

    def initiate_debit(self, task):
        if task.state != TaskState.Pending_Execution:
            raise PermissionError("I-5 Violation: Task must pass Calendar Gate before debit execution.")
            
        success = self.core_client.execute(task.account_id, task.amount)
        if success:
            task.mark_completed()
            self.status_updater.save(task)
            self.event_publisher.publish(task)
        else:
            task.mark_retrying()
            self.status_updater.save(task)

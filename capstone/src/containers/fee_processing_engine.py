from src.domain.processed_fee_task import RawFeeRecord, ProcessedFeeTask
from src.storage.fee_database import FeeDatabase
from src.infrastructure.mocks.mocks import MockParamsSystem

class FeeProcessingEngine:
    def __init__(self, fee_db: FeeDatabase, params: MockParamsSystem):
        self.fee_db = fee_db
        self.params = params

    def process(self, raw_record: RawFeeRecord) -> bool:
        final_amount = self.params.apply_discount(raw_record.amount)
        if final_amount <= 0:
            return False

        task = ProcessedFeeTask(
            id=raw_record.id,
            account_id=raw_record.account_id,
            amount=final_amount,
            date=raw_record.date
        )
        # Explicitly save 'Created' state to be observable
        self.fee_db.insert(task)
        
        # Transition to Pending_Calendar
        task.ready_for_calendar()
        self.fee_db.update(task)
        return True

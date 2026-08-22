from src.storage.fee_database import FeeDatabase
from src.storage.report_database import ReportDatabase

class ReportProjector:
    def __init__(self, fee_db: FeeDatabase, report_db: ReportDatabase):
        self.fee_db = fee_db
        self.report_db = report_db

    def sync(self):
        records = []
        for task in self.fee_db.tasks.values():
            records.append({
                "id": task.id,
                "account_id": task.account_id,
                "amount": task.amount,
                "state": task.state.value,
                "date": task.date
            })
        self.report_db.insert_all(records)

from src.storage.fee_database import FeeDatabase

class StatusUpdater:
    def __init__(self, fee_db: FeeDatabase):
        self.fee_db = fee_db

    def save(self, task):
        self.fee_db.update(task)

from src.storage.report_database import ReportDatabase
from src.storage.fee_database import FeeDatabase
from src.infrastructure.mocks.mocks import MockCoreBanking

class FeeReportAPI:
    def __init__(self, report_db: ReportDatabase):
        if isinstance(report_db, FeeDatabase) or isinstance(report_db, MockCoreBanking) or not isinstance(report_db, ReportDatabase):
            raise PermissionError("I-9 Violation: Forbidden access. Inquiry path must read from Report Database, not Fee Database or Core Banking.")
        self.report_db = report_db

    def get_reports(self):
        return self.report_db.get_all()

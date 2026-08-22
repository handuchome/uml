from typing import List

class ReportDatabase:
    def __init__(self):
        self.reports: List[dict] = []

    def insert_all(self, records: List[dict]):
        self.reports = records

    def get_all(self) -> List[dict]:
        return self.reports

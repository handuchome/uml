from src.containers.fee_processing_engine import FeeProcessingEngine
from src.domain.processed_fee_task import RawFeeRecord
from typing import List

class FeeIngestionService:
    def __init__(self, processing_engine: FeeProcessingEngine):
        self.processing_engine = processing_engine

    def ingest(self, records: List[RawFeeRecord]):
        results = []
        for r in records:
            res = self.processing_engine.process(r)
            results.append(res)
        return results

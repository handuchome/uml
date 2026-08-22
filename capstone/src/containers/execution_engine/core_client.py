from src.infrastructure.mocks.mocks import MockCoreBanking

class CoreClient:
    def __init__(self, core: MockCoreBanking):
        self.core = core

    def execute(self, account_id: str, amount: float) -> bool:
        return self.core.debit(account_id, amount)

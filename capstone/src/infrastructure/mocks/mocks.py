class MockCalendarService:
    def check_holiday_or_lunar(self, date_str: str) -> bool:
        return "HOLIDAY" in date_str.upper()

class MockCoreBanking:
    def debit(self, account_id: str, amount: float) -> bool:
        if account_id.startswith("POOR"):
            return False
        return True

class MockParamsSystem:
    def apply_discount(self, amount: float) -> float:
        return amount

class MockSMSGateway:
    def __init__(self):
        self.sent_messages = []
        
    def send_sms(self, customer_id: str, message: str):
        self.sent_messages.append({"customer_id": customer_id, "message": message})

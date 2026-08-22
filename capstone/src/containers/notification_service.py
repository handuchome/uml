from src.infrastructure.mocks.mocks import MockSMSGateway

class NotificationService:
    def __init__(self, sms_gateway: MockSMSGateway):
        self.sms_gateway = sms_gateway

    def handle_debit_success(self, task):
        message = f"Fee of {task.amount} collected successfully."
        self.sms_gateway.send_sms(task.account_id, message)

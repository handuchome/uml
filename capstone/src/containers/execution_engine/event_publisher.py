from src.infrastructure.message_broker import InMemoryMessageBroker

class EventPublisher:
    def __init__(self, broker: InMemoryMessageBroker):
        self.broker = broker

    def publish(self, task):
        self.broker.publish_debit_success(task)

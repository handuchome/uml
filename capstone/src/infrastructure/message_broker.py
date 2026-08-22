class InMemoryMessageBroker:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def publish_debit_success(self, task):
        for sub in self.subscribers:
            sub.handle_debit_success(task)

class APIGateway:
    def __init__(self, report_api):
        self.report_api = report_api

    def get_reports(self):
        return self.report_api.get_reports()

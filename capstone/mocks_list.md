# Mocks & Stubs for External Systems (I-3)

| External System (I-3) | Mock/Stub Definition (In-memory) | Description |
|---|---|---|
| Digital Channel Source | N/A | Simulated via HTTP Ingestion Trigger |
| Card Channel Source | N/A | Simulated via HTTP Ingestion Trigger |
| Corporate Channel Source | N/A | Simulated via HTTP Ingestion Trigger |
| Params System | `MockParamsSystem` | Provides discount rates, fee rules. |
| Calendar Service | `MockCalendarService` | Returns holiday/lunar dates for CON.2 validation. |
| Core Banking | `MockCoreBanking` | Simulates debit operations (success, insufficient funds for CON.3). |
| SMS Gateway | `MockSMSGateway` | Logs sent SMS messages triggered by Notification Service (CON.4). |

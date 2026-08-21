# Lab 3: Build List and Contract Register

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 3

## 1. Build List

*Every I-4 container mapped to build order, environment (from I-9), and Dev owner.*

| Build Order | Container (I-4 Name) | Environment (I-9 Location) | Owner (Dev Name) |
|---|---|---|---|
| 1 | Fee Database | Internal Data Zone | DB Admin Team |
| 2 | Report Database | Internal Data Zone | DB Admin Team |
| 3 | Fee Ingestion Service | Internal App Zone | Backend Dev A |
| 4 | Fee Processing Engine | Internal App Zone | Backend Dev A |
| 5 | Calendar Gate | Internal App Zone | Backend Dev B |
| 6 | Execution Engine | Internal App Zone | Backend Dev B |
| 7 | Notification Service | Internal App Zone | Integration Dev |
| 8 | Retry Scheduler | Internal App Zone | Backend Dev A |
| 9 | Fee Report API | Internal App Zone | Frontend/API Dev |
| 10 | Fee Inquiry Web App | Internal App Zone | Frontend Dev |

## 2. Contract Register (G4 Evidence)

*One row per I-8 relationship.*

| Producer (Provider) | Consumer (Caller) | Sync/Async | Operation / Event Name |
|---|---|---|---|
| Core Banking (External) | Execution Engine | Sync | `POST /api/v1/core/debit` |
| Fee Report API | Fee Inquiry Web App | Sync | `GET /api/reports/summary`, `GET /api/reports/details` |
| Notification Service | Execution Engine | Async | `Event: DebitSuccessEvent` |
| Fee Ingestion Service | Source Systems (Digibank, Card, IB TC) | Async | `FileTransfer / BatchIngest` |
| Calendar Service (External) | Calendar Gate | Sync | `GET /api/calendar/check-date` |

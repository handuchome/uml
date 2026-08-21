# Lab 4: Cleaned 1-3 Pack & Name-Identity Check

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 4

## 1. Cleaned 1-3 Pack Summary
*Copies of Lab 1-3 have been reviewed. The following is the strictly enforced consolidated list of Containers and Actors used across all artifacts.*

**Consolidated Actors (I-2):**
- Bank Staff

**Consolidated Containers (I-4):**
- Fee Ingestion Service
- Fee Processing Engine
- Calendar Gate
- Execution Engine
- Retry Scheduler
- Notification Service
- Fee Report API
- Fee Inquiry Web App
- Fee Database
- Report Database

**Consolidated Externals (I-3):**
- Source System Digibank
- Source System Card
- Source System IB TC
- Params System
- Calendar Service
- Core Banking
- SMS Gateway

## 2. Name-Identity Check
*Audit of all strings in Labs 2-3 against Lab 1 Index.*

| Artifact audited | Target String | Match Status | Corrected / Cleaned |
|---|---|---|---|
| Lab 2 Requirements | "hệ thống Thẻ" | Forked | Cleaned to `Source System Card` |
| Lab 3 Sequence | "Core" | Forked | Cleaned to `Core Banking` |
| Lab 3 Test Spec | "Core" | Forked | Cleaned to `Core Banking` |
| Lab 3 Test Spec (SUT) | "Fee Processing Engine" | 100% Match | Validated |
| Lab 3 Exception Spec | "Calendar Gate" | 100% Match | Validated |
| Lab 3 Build List | "Fee Database" | 100% Match | Validated |

*Result: Zero forks remaining. All artifacts now strictly use I-1 to I-11 names.*
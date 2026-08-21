# Lab 4: Standardize Following Modeling-Driven Design (First Cleanup)

**Project:** Bank Service Fee Collection System  
**Phase:** Before Modeling (Messy) - Lab 4  
**Role:** SA (Responsible) · EA (Accountable)  

---

## 1. Cleaned 1–3 Pack Summary
*Review and consolidation of Labs 1–3 to ensure strict name-identity compliance.*

- **Actors (I-2):** `Bank Staff`, `Customer`
- **External Systems (I-3):** `Digital Channel Source`, `Card Channel Source`, `Corporate Channel Source`, `Params System`, `Calendar Service`, `Core Banking`, `SMS Gateway`
- **Internal Containers (I-4):** `API Gateway`, `Message Broker`, `Fee Ingestion Service`, `Fee Processing Engine`, `Calendar Gate`, `Execution Engine`, `Retry Scheduler`, `Notification Service`, `Report Projector`, `Fee Report API`, `Fee Inquiry Web App`, `Fee Database`, `Report Database`
- **Named Object (I-6):** `ProcessedFeeTask`
- **Constraints (I-10):** `CON.1` through `CON.5`

---

## 2. Name-Identity Check
*Audit of all strings used across Labs 2 and 3 against the locked Lab 1 Name-Identity Index.*

| Artifact Audited | Target String (As First Written) | Match Status | Corrected / Cleaned String |
|---|---|---|---|
| Lab 2 Requirements (REQ-01) | "Digital/Card/IB TC sources" | Forked | `Digital Channel Source`, `Card Channel Source`, `Corporate Channel Source` |
| Lab 3 Contract Register | "Core" | Forked | `Core Banking` |
| Lab 3 To-be Sequence | "Calendar API" | Forked | `Calendar Gate` / `Calendar Service` |
| Lab 3 Test Spec (TS-03) | "Execution Engine" | Adjusted | `Execution Engine (via Calendar Gate)` |
| Lab 2 & 3 Process Step 7 | "System syncs state" | Vague / Forked | `Report Projector` |

*Result:* Zero identity forks remaining. All text artifacts strictly use the locked index strings.

---

## 3. Defect List (Before)
*Failures found in Labs 1–3 during the initial messy writing phase.*

| Defect ID | Location | Description of Failure (Messy Phase) | Owner |
|---|---|---|---|
| DEF-01 | Lab 2 (REQ-01) | Used informal channel names instead of exact I-3 identifiers (`Digital Channel Source`, etc.). | BA |
| DEF-02 | Lab 3 (Sequence) | Omitted the explicit CQRS projector component, relying on vague system sync wording. | Dev / SA |
| DEF-03 | Lab 3 (Sequence) | `TaskPoller` directly invoked `Calendar Gate`, violating component separation of concerns. | Dev |
| DEF-04 | Lab 3 (Test Spec TS-03) | SUT for calendar block only listed `Execution Engine`, missing the interaction with `Calendar Gate`. | Test |

---

## 4. Comparison Note
*What was cleaned — and what we still do not know how to standardize.*

### What we cleaned:
1. **Strict Name-Identity Enforcement:** Eradicated all informal or shorthand terms (e.g., replacing "Core" with `Core Banking`, and defining `Report Projector` for state synchronization).
2. **Component Responsibilities:** Refined the execution sequence so that `DebitDispatcher` coordinates calendar validation, maintaining clean separation from database polling (`TaskPoller`).
3. **Traceability:** Aligned the Lab 2 Trace Table precisely with the lifecycle states defined in Lab 1 (I-6).

### What we still do not know how to standardize (Pending the Guide - Lab 7):
1. **Formal Notation Standards:** We are using text-based tables and basic sequence text blocks; we do not yet know how to formally render these into ArchiMate or C4 layers.
2. **Architecture Governance:** We lack formal RACI matrices tied to review sign-offs (currently handled informally).
3. **Ecosystem Structuring:** While we listed API Gateway and Message Broker as containers, we do not know the precise structural constraints for enterprise-grade enterprise service bus/gateway patterns without the Guide framework.

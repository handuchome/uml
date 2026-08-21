# Lab 4: Standardize Following Modeling-Driven Design (First Cleanup)

**Project:** Bank Service Fee Collection System  
**Phase:** Before Modeling (Messy) - Lab 4  
**Role:** SA / EA  

---

## 1. Cleaned 1–3 Pack Summary
*Review and consolidation of Labs 1–3, with baseline copies preserved in `lab4/cleaned/`.*

- **Actors (I-2):** `Bank Staff`, `Customer`[cite: 8]
- **External Systems (I-3):** `Digital Channel Source`, `Card Channel Source`, `Corporate Channel Source`, `Params System`, `Calendar Service`, `Core Banking`, `SMS Gateway`[cite: 8]
- **Internal Containers (I-4):** `API Gateway`, `Message Broker`, `Fee Ingestion Service`, `Fee Processing Engine`, `Calendar Gate`, `Execution Engine`, `Retry Scheduler`, `Notification Service`, `Report Projector`, `Fee Report API`, `Fee Inquiry Web App`, `Fee Database`, `Report Database`[cite: 8]
- **Named Object (I-6):** `ProcessedFeeTask`[cite: 8]
- **Constraints (I-10):** `CON.1` through `CON.5`[cite: 8]

---

## 2. Name-Identity Check
*Audit of files in `lab4/cleaned/` against the locked Lab 1 Name-Identity Index.*

| Lab 2 string | Lab 3 string (in `lab4/cleaned/`) | Lab 1 index | match? |
|---|---|---|---|
| Step 3: Calendar validation in pipeline flow | `TaskPoller` invokes `Calendar Gate` directly in sequence | `Calendar Gate` | No (Fork: pipeline step vs polling execution sequence caller)[cite: 10] |
| Step 7 / REQ-06: Inquiry data path (omits gateway) | `GET /api/reports` routed via `API Gateway` | `API Gateway`, `Fee Report API`, `Fee Inquiry Web App` | No (Fork: I-5 step 7 and REQ-06 omit API Gateway present in Contract Register)[cite: 10] |
| REQ-06: `Report Projector` sync state | Missing explicit write edge in Contract Register (I-8) | `Report Projector`, `Report Database` | No (Fork: Contract Register omits the write edge to Report Database)[cite: 10] |
| REQ-05: `Notification Service` commands `SMS Gateway` | Missing explicit SMS trigger edge in Contract Register (I-8) | `Notification Service`, `SMS Gateway` | No (Fork: Contract Register omits the notification dispatch row)[cite: 10] |

---

## 3. Defect List (Before)
*Failures and structural inconsistencies found in the files as first written (kept as-is for the messy pack).*

| Defect ID | Location | Description of Failure (Pass Pack) | Owner (Person Name) |
|---|---|---|---|
| DEF-01 | I-5 vs Lab 3 Sequence | Inconsistency in who invokes `Calendar Gate` (pipeline process step vs polling execution task flow). | Nguyễn Nhật Trường[cite: 10] |
| DEF-02 | Lab 3 Contract Register (I-8) | Omission of data sync and messaging integration rows (`Report Projector` → `Report Database`, `Notification Service` → `SMS Gateway`). | Hà Ngọc Bắc[cite: 10] |
| DEF-03 | I-5 Step 7 / REQ-06 vs UC-Inquiry | Inconsistency regarding `API Gateway` presence in the reporting inquiry flow (omitted in I-5 step 7/REQ-06 but present in Contract Register). | Dương Đỗ Minh[cite: 10] |
| DEF-04 | Lab 3 Exception Spec | Failure paths for CON.4 (SMS notification failure) and CON.5 (CQRS projection lag) are completely absent from the Exception Spec. | Hàn Ngọc Đức[cite: 10] |

---

## 4. Comparison Note
*What is frozen in the pack — and what remaining forks are logged as known leftovers.*

### 4.1 What was actually done:
1. **Files Kept As-Is:** The files inside `lab4/cleaned/` are preserved directly from the Pass baseline without in-place code rewrites. 
2. **Forks Logged as Known Leftovers:** All minor structural and naming discrepancies between I-5, I-8, and Lab 3 sequence/test specs are explicitly acknowledged and logged in §2 and §3 rather than being falsely claimed as resolved. They are treated as known leftovers of the messy phase.

### 4.2 What we still do not know how to standardize (Pending the Guide - Lab 7)[cite: 1, 10]:
1. **Formal Notation Standards:** We are using text-based tables and basic sequence text blocks; we do not yet know how to formally render these into ArchiMate or C4 layers.
2. **Architecture Governance:** We lack formal RACI matrices tied to review sign-offs (currently handled informally).
3. **Ecosystem Structuring:** While we listed API Gateway and Message Broker as containers, we do not know the precise structural constraints for enterprise-grade enterprise service bus/gateway patterns without the Guide framework.
# Lab 5: G6 Coverage Checklist

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 5
*Note: Evidence that each state transition and sequence `alt` branch has a planned test.*

| UML State Transition / Sequence `alt` Branch | Planned Test ID (from Lab 3) | Coverage Status |
|---|---|---|
| Transition: `Created` -> `Pending_Calendar` | TC-01 | Covered |
| `alt`: Fee <= 0 (Discard branch in Ingestion) | TC-02 | Covered |
| Transition: `Pending_Calendar` -> `Pending_Execution` | TC-03 | Covered |
| Transition: `Pending_Calendar` -> `Rescheduled` | TC-04 | Covered |
| `alt`: IsHoliday / IsLunarFirst = True (Reschedule branch) | TC-05 | Covered |
| Transition: `Rescheduled` -> `Pending_Calendar` | TC-06 | Covered |
| Transition: `Pending_Execution` -> `Completed` | TC-07 | Covered |
| Transition: `Pending_Execution` -> `Retrying` | TC-08 | Covered |
| `alt`: Insufficient Funds (To Retry branch in Execution) | TC-09 | Covered |
| Transition: `Retrying` -> `Pending_Execution` | TC-10 | Covered |
| Transition: `Retrying` -> `Failed_Permanently` | TC-11 | Covered |
| `alt`: RetryCount >= 10 (Fail permanently branch) | TC-12 | Covered |

*All components verified. Ready to proceed to Lab 6.*

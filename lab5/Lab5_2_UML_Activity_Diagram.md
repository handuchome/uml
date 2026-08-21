# Lab 5: UML Activity Diagram

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 5
*Note: Happy path matches I-5. Decisions show CON.* explicitly.*

## Main Process Flow
```mermaid
stateDiagram-v2
    state "Receive List from Source Systems" as S1
    state "Filter Fee & Calculate" as S2
    state "Check Calendar API" as S3
    state "Execute Core Banking Debit" as S4
    state "Sync to Report DB" as S5
    state "Trigger SMS" as S6

    [*] --> S1
    S1 --> S2

    state decision_fee <<choice>>
    S2 --> decision_fee: Check CON.1
    decision_fee --> S3: Fee > 0
    decision_fee --> [*]: Discard (Fee <= 0)

    state decision_cal <<choice>>
    S3 --> decision_cal: Check CON.2
    decision_cal --> [*]: Halt / Reschedule (Holiday / Lunar 1st)
    decision_cal --> S4: Normal Working Day

    state decision_core <<choice>>
    S4 --> decision_core
    decision_core --> [*]: To AutoRetry (Insufficient Funds - CON.3)
    decision_core --> S6: Success

    S6 --> S5: (CON.4 - SMS Sent)
    S5 --> [*]: (CON.5 - Ready for UI Query)
```

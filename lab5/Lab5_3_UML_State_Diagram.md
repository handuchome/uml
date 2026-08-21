# Lab 5: UML State Diagram

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 5
*Note: Strictly ONE object per machine. States perfectly match I-6.*

## Object: `ProcessedFeeTask`
```mermaid
stateDiagram-v2
    [*] --> Created: Validated Fee > 0 (CON.1)

    Created --> Pending_Calendar: Ready for check

    Pending_Calendar --> Pending_Execution: Check Calendar (Pass)
    Pending_Calendar --> Rescheduled: Check Calendar Fail (CON.2)

    Rescheduled --> Pending_Calendar: Next working day reached

    Pending_Execution --> Completed: Debit Success
    Pending_Execution --> Retrying: Debit Fail - Insufficient Funds

    Retrying --> Pending_Execution: Retry limits not reached (<10)
    Retrying --> Failed_Permanently: Retry limits reached (=10) (CON.3)

    Completed --> [*]: (Terminal)
    Failed_Permanently --> [*]: (Terminal)
```

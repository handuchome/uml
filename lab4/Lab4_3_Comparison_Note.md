# Lab 4: Comparison Note

**Project:** Bank Service Fee Collection System
**Phase:** Before Modeling (Messy) - Lab 4

## What we cleaned in Labs 1-3:
1. **Strict String Matching:** We swept through the Requirements (Lab 2) and Design/Test Specs (Lab 3) to eradicate informal names (e.g., changing "hệ thống Thẻ" to `Source System Card`, "Core" to `Core Banking`). 
2. **Container Boundaries:** Clarified that the `Fee Inquiry Web App` only talks to the `Fee Report API`, explicitly listing the exact container names to avoid ambiguity.
3. **Consolidated List:** Created a single, unified list of Actors and Containers that serves as the absolute source of truth for all documentation going forward.

## What we still do not know how to standardize:
1. **Diagram Notations:** We are currently using free-form text and basic sequence text blocks. We don't yet know how to formally draw these systems using C4 Model or ArchiMate.
2. **Enterprise Layer Mapping:** We have business constraints (CON.1-CON.5) but no standard way to map these strategy/motivation elements into our architecture diagrams.
3. **Ecosystem & Gateways:** We know we have APIs, but we don't know how to correctly represent an API Gateway or Message Broker in our container views yet without violating standards.
4. **Governance (RACI):** We haven't applied formal RACI matrices to our artifacts yet, so ownership is still somewhat loose.
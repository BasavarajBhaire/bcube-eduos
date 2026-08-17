# Preschool Technology Architecture

**Status:** Conceptual foundation

## Goal

Define the digital capabilities that support Bcube Future Preschool without coupling the operating model to a single implementation prematurely.

## Capability landscape

- Parent experience / communication
- Teacher workspace
- School administration
- Admissions / CRM
- Student information
- Attendance
- Academic planning and progress
- Fee / payment management
- Staff operations
- Inventory / assets
- Notifications
- Reporting / analytics
- Identity and access
- Audit / observability

## Conceptual context

```mermaid
flowchart TD
    Parent[Parents] --> ParentExperience[Parent Experience]
    Teacher[Teachers] --> TeacherWorkspace[Teacher Workspace]
    Admin[School / Central Team] --> AdminPortal[Administration]

    ParentExperience --> Platform[EduOS Platform Services]
    TeacherWorkspace --> Platform
    AdminPortal --> Platform

    Platform --> Student[Student & Admissions]
    Platform --> Academic[Academic]
    Platform --> Attendance
    Platform --> Finance[Fees / Finance]
    Platform --> Comms[Communication]
    Platform --> Analytics

    Student --> Data[(Operational Data)]
    Academic --> Data
    Attendance --> Data
    Finance --> Data

    Platform --> IAM[Identity & Access]
    Platform --> Audit[Audit / Observability]
```

## Architecture principles

- Child and parent data protection by design
- Role-based least-privilege access
- Auditable administrative actions
- API-first integration where appropriate
- Avoid duplicating authoritative data
- Operational workflows must continue safely during reasonable technology failures
- Architecture decisions with material long-term impact require ADRs

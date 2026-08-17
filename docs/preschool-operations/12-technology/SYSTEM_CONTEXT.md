# Preschool Technology System Context

**Status:** Draft v0.1

## Purpose

Define the major users, external systems and platform boundaries that support Bcube Future Preschool operations.

```mermaid
flowchart LR
  Parent[Parent / Guardian] --> ParentApp[Parent Experience]
  Teacher[Teacher] --> TeacherApp[Teacher Workspace]
  Admin[Branch / Central Admin] --> AdminPortal[Admin Portal]
  Finance[Finance] --> AdminPortal

  ParentApp --> APIGW[EduOS API Layer]
  TeacherApp --> APIGW
  AdminPortal --> APIGW

  APIGW --> Admissions[Admissions / CRM]
  APIGW --> Student[Student Information]
  APIGW --> Attendance[Attendance]
  APIGW --> Academic[Academic Planning]
  APIGW --> Assessment[Observation / Assessment]
  APIGW --> Billing[Fees / Billing]
  APIGW --> Comms[Communication]
  APIGW --> Ops[Operations / Incidents]
  APIGW --> Reporting[Reporting / Analytics]

  Billing --> Payment[Payment Gateway]
  Comms --> Msg[Email / SMS / Push / Messaging Provider]
  APIGW --> IAM[Identity & Access]
  APIGW --> Audit[Audit / Observability]
```

## Architectural boundary

EduOS should coordinate preschool workflows and data while avoiding unnecessary duplication of authoritative information. External providers such as payment, messaging and identity systems should be integrated through well-defined interfaces.

## Core principles

- role-based least privilege
- auditable sensitive actions
- API-first integrations where useful
- offline-safe operational fallbacks for safety-critical school processes
- explicit ownership of each data domain
- traceability from business process to application capability

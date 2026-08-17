# Application Architecture

**Status:** Draft v0.1

## Experience applications

| Application | Primary users | Core capabilities |
|---|---|---|
| Parent Experience | Parents / guardians | communication, attendance visibility, progress, fees, requests, events |
| Teacher Workspace | Teachers / coordinators | classroom roster, lesson plans, attendance, observations, progress, parent notes |
| Admin Portal | Branch / central teams | admissions, students, staff, finance, operations, reporting, configuration |

## Domain services

| Domain | Responsibility |
|---|---|
| Admissions / CRM | enquiry, counselling, visit, application, conversion |
| Student Information | student profile, guardians, programme, enrolment, branch/class assignment |
| Attendance | arrival, attendance state, late/absence, dispersal status |
| Academic Planning | programme, curriculum references, lesson plans, delivery status |
| Assessment | observation evidence, learning outcome progress, review cycles |
| Parent Engagement | PTM, requests, feedback, complaints, communications |
| Fees / Billing | fee plans, invoices/demand, payments, receipts, outstanding balance |
| People | staff profile, role, branch assignment, training / onboarding references |
| Safety / Operations | incidents, authorized pickup references, operational checks |
| Inventory / Assets | materials, stock, assets and branch inventory |
| Notifications | channel orchestration, templates and delivery status |
| Reporting | operational and academic metrics, branch scorecards |

## Design principle

Start with clear domain boundaries. Physical deployment may initially be a modular monolith or a small number of services; domain separation should not automatically imply microservices.

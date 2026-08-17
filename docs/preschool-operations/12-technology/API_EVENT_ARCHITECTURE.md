# API & Event Architecture

**Status:** Draft v0.1

## Interaction styles

Use synchronous APIs for user-driven commands/queries that need an immediate result. Use domain events for meaningful state changes that other capabilities may react to asynchronously.

## Example API resource families

- `/admissions/enquiries`
- `/admissions/applications`
- `/students`
- `/students/{id}/guardians`
- `/enrolments`
- `/classrooms`
- `/attendance`
- `/academic/lesson-plans`
- `/academic/observations`
- `/academic/progress`
- `/fees/accounts`
- `/payments`
- `/communications`
- `/operations/incidents`

These are conceptual resource boundaries, not an approved external API contract.

## Candidate domain events

| Event | Produced when | Typical consumers |
|---|---|---|
| `EnquiryCreated` | enquiry captured | CRM analytics / follow-up |
| `ApplicationSubmitted` | application completed | admissions workflow |
| `StudentEnrolled` | enrolment activated | student, billing, academic setup |
| `StudentArrived` | arrival verified | attendance / parent notification |
| `StudentDispersed` | authorized handover completed | attendance / parent notification |
| `LessonDelivered` | planned learning delivered | academic analytics |
| `ObservationRecorded` | learning evidence saved | progress aggregation |
| `ProgressReportPublished` | report approved/published | parent experience |
| `PaymentRecorded` | payment confirmed | ledger / receipt / analytics |
| `IncidentRecorded` | incident logged | safety workflow / escalation |

## Event requirements

Events should contain stable identifiers, event type/version, occurred-at time, producer, correlation identifier and the minimum data necessary for consumers. Avoid broadcasting sensitive child data when identifiers are sufficient.

## Reliability

Where events drive material state changes, use durable delivery patterns, idempotent consumers, retry/dead-letter handling and observability. Do not rely on asynchronous notifications as the sole control for immediate child safety.

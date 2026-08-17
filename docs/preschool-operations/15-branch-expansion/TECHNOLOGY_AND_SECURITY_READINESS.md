# Branch Technology & Security Readiness

**Status:** Draft v0.1

## Objective

Ensure a new branch can operate core EduOS workflows reliably while preserving safe manual fallback for child-safety-critical operations.

## Readiness domains

### Connectivity
- primary internet service active and tested
- Wi-Fi coverage validated in required staff/admin areas
- secure network configuration
- documented outage fallback

### End-user equipment
- approved administrative devices
- teacher devices where part of operating model
- printing/scanning capability where required
- protected charging/storage

### Identity & access
- named staff accounts
- role assignment based on approved RBAC
- no shared privileged credentials
- joiner/mover/leaver procedure
- MFA where supported/required

### EduOS capabilities
- admissions access
- student records
- attendance
- academic planning
- parent communication
- fee / finance access by authorized roles
- reporting

### Physical security technology
Where adopted and lawful:
- access-control equipment
- CCTV camera placement against approved safety/privacy design
- recording/storage validation
- restricted access to recordings
- retention aligned to approved policy

### Data protection
- avoid uncontrolled local copies of sensitive records
- screen/device locking
- secure handling of printed records
- backup/recovery responsibility defined
- incident reporting route known to staff

## Go-live tests

1. User login and role access.
2. Student lookup / admission workflow.
3. Attendance workflow.
4. Parent communication test using non-sensitive test data.
5. Authorized finance workflow test.
6. Printing / document handling where required.
7. Network outage fallback drill.
8. Restore / recovery responsibility confirmed.
9. Access/CCTV verification where implemented.
10. Critical support contacts available.

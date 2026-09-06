# Stakeholder Validation

## Purpose

The prototype was reviewed from the perspective of the main
organisational roles that would use a healthcare release risk monitor.

This is a simulated stakeholder walkthrough and not a formal
clinical or hospital-user study.

---

## Stakeholder 1 — Release Engineer

### Main concern

The release engineer needs to know whether a release can proceed
without manually checking multiple deployment signals.

### Prototype walkthrough

Scenario:

- Release selected from the dashboard
- CPU, memory, error rate and latency displayed
- Canary comparison displayed
- Risk decision generated
- Progressive rollout action displayed

### Expected feedback

The dashboard should make SAFE, HOLD and BLOCK decisions easy to
understand and should clearly explain why a release was stopped.

### Action taken

The prototype displays the risk decision and rollout action directly
on the dashboard.

---

## Stakeholder 2 — Operations Admin

### Main concern

The operations admin needs control over risk thresholds and
configuration while preventing unauthorized users from changing
important rules.

### Prototype walkthrough

Scenario:

- Operations Admin logs in
- Configuration permissions are checked
- Risk thresholds are configurable through configuration
- Release Engineer attempts unauthorized configuration access

### Expected feedback

Configuration should be flexible while sensitive actions should be
restricted and audited.

### Action taken

Role-based access control and audit logging were implemented.

---

## Stakeholder 3 — Hospital IT / Deployment Manager

### Main concern

The deployment manager needs confidence that a problematic release
will not automatically reach all hospitals.

### Prototype walkthrough

Scenario:

- Release begins progressive rollout
- Canary health is monitored
- Risk becomes unsafe
- Rollout is stopped or placed on HOLD
- Monitoring failure triggers fallback behavior

### Expected feedback

The system should fail safely when monitoring information is
unavailable.

### Action taken

The prototype implements HOLD fallback behavior and
store-and-forward processing.

---

## Validation Summary

| Area | Result |
|---|---|
| Release decision visibility | PASS |
| Progressive rollout visibility | PASS |
| Configurable rules | PASS |
| Role-based access | PASS |
| Audit logging | PASS |
| Failure handling | PASS |
| Store-and-forward | PASS |

## Conclusion

The simulated stakeholder walkthrough indicates that the prototype
addresses the main workflow needs of release engineering,
operations administration and hospital deployment management.

Further validation with real hospital IT and release-management users
would be required before production deployment.
# Healthcare Release Risk Monitor

A field-ready prototype for monitoring healthcare software releases across multiple hospital deployments.

## Overview

Healthcare software vendors may maintain separate deployments for many hospitals. A release that appears safe in one deployment may behave differently in another deployment.

This project provides a pre-release and progressive-delivery risk monitoring prototype that evaluates deployment health signals and produces one of four decisions:

- SAFE
- WARNING
- HOLD
- BLOCK

The system combines deployment events, infrastructure health metrics, error budgets, canary comparison results, validation, noise handling, fallback behavior, role-based access control, audit logging, and progressive rollout simulation.

---

## Problem Statement

Release failures may only become visible after a deployment reaches a customer environment.

The goal of this project is to detect potential release risk before broader rollout and prevent unsafe deployments from progressing automatically.

The prototype is designed around these safety principles:

1. Validate incoming observations.
2. Treat missing or unreliable observations conservatively.
3. Compare stable and canary behavior.
4. Calculate a configurable risk score.
5. Convert the score into a release decision.
6. Control progressive rollout based on that decision.
7. Maintain fallback and audit information.

---

## Key Features

### Risk Evaluation

The risk engine evaluates:

- CPU usage
- Memory usage
- Error rate
- Latency
- Remaining error budget
- Canary risk
- Deployment status

Each signal contributes configurable risk points.

### Risk Decisions

The system produces:

| Decision | Meaning |
|---|---|
| SAFE | Release can proceed |
| WARNING | Manual review is required |
| HOLD | Rollout is paused for safety |
| BLOCK | Release must not proceed |

Missing or noisy monitoring data results in a HOLD decision.

Critical canary failure results in BLOCK.

---

## Progressive Delivery

The prototype models progressive rollout using four stages:

```text
5% → 25% → 50% → 100%

## Evaluation Scope and Limitations

The evaluation in this project is based on a synthetic dataset containing
5,000 simulated hospital deployment records.

The dataset was generated to represent different deployment conditions,
including healthy, degraded, noisy, and harmful release scenarios.

The reported metrics such as precision, recall, false-positive rate, and
harmful-release detection are therefore prototype evaluation results on
simulated data.

They should not be interpreted as production, clinical, or real-world
hospital performance measurements.

In a production environment, the system would require validation using
real deployment telemetry, historical incidents, organization-specific
thresholds, and controlled rollout data before being used for operational
release decisions.
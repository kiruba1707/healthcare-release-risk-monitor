# Healthcare Release Risk Monitor

A healthcare software release risk monitoring and progressive delivery prototype for software vendors managing separate deployments across multiple hospitals.

## Problem Statement

Healthcare software vendors may maintain separate deployments for many hospitals. A release can appear healthy during deployment but later cause performance degradation, increased errors, or service instability.

This project provides a pre-release risk monitoring system that combines deployment signals, system health metrics, error budgets, and canary comparison results to identify potentially harmful releases before wider rollout.

## Key Features

- Multi-hospital deployment monitoring
- Risk evaluation using multiple telemetry signals
- Risk decisions:
  - SAFE
  - WARNING
  - HOLD
  - BLOCK
- CPU and memory monitoring
- Error-rate monitoring
- Latency monitoring
- Error-budget analysis
- Stable vs canary error-rate comparison
- Deployment-status analysis
- Progressive rollout control
- Rollout stages:
  - 5%
  - 25%
  - 50%
  - 100%
- Missing and noisy observation handling
- Fallback and store-and-forward support
- Role-based access control
- Authentication and account settings
- Audit logging
- Configurable risk thresholds and weights
- Streamlit monitoring dashboard

## System Architecture

```text
Deployment Events
       |
       v
Data Validation
       |
       v
Noise Handling
       |
       +-------------------+
       |                   |
       v                   v
Error Budget          Canary Analysis
       |                   |
       +---------+---------+
                 |
                 v
           Risk Engine
                 |
                 v
       SAFE / WARNING / HOLD / BLOCK
                 |
                 v
      Progressive Delivery
        5% -> 25% -> 50% -> 100%
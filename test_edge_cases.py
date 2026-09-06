import pandas as pd

from core.noise_handler import clean_dataset
from core.canary import calculate_canary_risk
from core.error_budget import calculate_error_budget_risk
from core.fallback import apply_fallback
from core.risk_engine import evaluate_dataset


def prepare_and_evaluate(data):
    df = pd.DataFrame([data])

    df = clean_dataset(df)
    df = calculate_error_budget_risk(df)
    df = calculate_canary_risk(df)
    df = apply_fallback(df)
    df = evaluate_dataset(df)

    return df.iloc[0]


def test_missing_critical_metric():
    case = {
        "release_id": "EDGE001",
        "hospital_id": "H001",
        "version": "v3.0",
        "cpu_usage": 60,
        "memory_usage": 55,
        "error_rate": None,
        "latency_ms": 180,
        "error_budget_remaining": 70,
        "stable_error_rate": 1.0,
        "canary_error_rate": 1.2,
        "stable_latency_ms": 170,
        "deployment_status": "SUCCESS",
    }

    result = prepare_and_evaluate(case)

    assert result["risk_decision"] == "HOLD"


def test_noisy_cpu_metric():
    case = {
        "release_id": "EDGE002",
        "hospital_id": "H002",
        "version": "v3.0",
        "cpu_usage": 99,
        "memory_usage": 60,
        "error_rate": 1.0,
        "latency_ms": 180,
        "error_budget_remaining": 70,
        "stable_error_rate": 1.0,
        "canary_error_rate": 1.1,
        "stable_latency_ms": 170,
        "deployment_status": "SUCCESS",
    }

    result = prepare_and_evaluate(case)

    assert result["risk_decision"] == "HOLD"


def test_canary_failure():
    case = {
        "release_id": "EDGE003",
        "hospital_id": "H003",
        "version": "v3.0",
        "cpu_usage": 60,
        "memory_usage": 55,
        "error_rate": 2.0,
        "latency_ms": 500,
        "error_budget_remaining": 60,
        "stable_error_rate": 1.0,
        "canary_error_rate": 8.0,
        "stable_latency_ms": 180,
        "deployment_status": "SUCCESS",
    }

    result = prepare_and_evaluate(case)

    assert result["risk_decision"] == "BLOCK"

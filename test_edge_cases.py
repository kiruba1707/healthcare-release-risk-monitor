import pandas as pd

from core.noise_handler import clean_dataset
from core.canary import calculate_canary_risk
from core.error_budget import calculate_error_budget_risk
from core.fallback import apply_fallback
from core.risk_engine import evaluate_dataset


def prepare_and_evaluate(data):
    """
    Run one release through the complete
    monitoring pipeline.
    """

    df = pd.DataFrame([data])

    # Data quality
    df = clean_dataset(df)

    # Error budget
    df = calculate_error_budget_risk(df)

    # Canary comparison
    df = calculate_canary_risk(df)

    # Fallback
    df = apply_fallback(df)

    # Risk engine
    df = evaluate_dataset(df)

    return df.iloc[0]


print("=" * 70)
print("EDGE AND FAILURE CASE TESTS")
print("=" * 70)


# ==========================================================
# CASE 1 — Missing critical metric
# ==========================================================

case_1 = {
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

    "deployment_status": "SUCCESS"
}


result_1 = prepare_and_evaluate(case_1)

print("\nCASE 1 — Missing Error Rate")
print("Expected: HOLD")
print("Actual:", result_1["risk_decision"])


# ==========================================================
# CASE 2 — Noisy / abnormal metric
# ==========================================================

case_2 = {
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

    "deployment_status": "SUCCESS"
}


result_2 = prepare_and_evaluate(case_2)

print("\nCASE 2 — Noisy CPU")
print("Expected: HOLD")
print("Actual:", result_2["risk_decision"])


# ==========================================================
# CASE 3 — Canary significantly worse
# ==========================================================

case_3 = {
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

    "deployment_status": "SUCCESS"
}


result_3 = prepare_and_evaluate(case_3)

print("\nCASE 3 — Canary Failure")
print("Expected: BLOCK")
print("Actual:", result_3["risk_decision"])


# ==========================================================
# Final summary
# ==========================================================

results = [
    result_1["risk_decision"] == "HOLD",
    result_2["risk_decision"] == "HOLD",
    result_3["risk_decision"] == "BLOCK"
]


print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

print("Case 1:", "PASS" if results[0] else "FAIL")
print("Case 2:", "PASS" if results[1] else "FAIL")
print("Case 3:", "PASS" if results[2] else "FAIL")

print(
    "\nPassed:",
    sum(results),
    "/",
    len(results)
)
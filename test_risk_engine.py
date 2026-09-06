import pandas as pd

from core.noise_handler import clean_dataset
from core.canary import calculate_canary_risk
from core.error_budget import calculate_error_budget_risk
from core.fallback import apply_fallback
from core.risk_engine import evaluate_dataset


# Load dataset
df = pd.read_csv("data/releases_raw.csv")


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


print("=" * 70)
print("HEALTHCARE RELEASE RISK ENGINE")
print("=" * 70)


print("\nDecision Distribution:")
print(
    df["risk_decision"].value_counts()
)


print("\nRisk Score Statistics:")
print(
    df["risk_score"].describe()
)


print("\nSample Results:")

print(
    df[
        [
            "release_id",
            "hospital_id",
            "version",
            "cpu_usage",
            "memory_usage",
            "error_rate",
            "latency_ms",
            "error_budget_remaining",
            "canary_risk",
            "risk_score",
            "risk_decision"
        ]
    ].head(20)
)
import pandas as pd

from core.noise_handler import clean_dataset
from core.error_budget import calculate_error_budget_risk
from core.fallback import apply_fallback


# Load dataset
df = pd.read_csv("data/releases_raw.csv")


# Step 1: detect missing/noisy observations
df = clean_dataset(df)


# Step 2: calculate error-budget status
df = calculate_error_budget_risk(df)


# Step 3: apply fallback behaviour
df = apply_fallback(df)


print("=" * 60)
print("FALLBACK + ERROR BUDGET TEST")
print("=" * 60)


print("\nError Budget Status:")
print(
    df["error_budget_status"].value_counts()
)


print("\nFallback Actions:")
print(
    df["fallback_action"].value_counts()
)


print("\nSample:")
print(
    df[
        [
            "release_id",
            "hospital_id",
            "error_budget_remaining",
            "error_budget_status",
            "missing_metric",
            "noisy_metric",
            "fallback_action"
        ]
    ].head(15)
)
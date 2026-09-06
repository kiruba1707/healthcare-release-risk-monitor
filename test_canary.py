import pandas as pd

from core.canary import calculate_canary_risk


# Load dataset
df = pd.read_csv("data/releases_raw.csv")


# Calculate canary comparison
df = calculate_canary_risk(df)


print("=" * 60)
print("CANARY COMPARISON TEST")
print("=" * 60)


print("\nCanary Risk:")
print(
    df["canary_risk"].value_counts()
)


print("\nAverage metrics:")

print(
    "\nStable error rate:",
    round(df["stable_error_rate"].mean(), 2)
)

print(
    "Canary error rate:",
    round(df["canary_error_rate"].mean(), 2)
)

print(
    "\nStable latency:",
    round(df["stable_latency_ms"].mean(), 2)
)

print(
    "Canary latency:",
    round(df["latency_ms"].mean(), 2)
)


print("\nSample:")
print(
    df[
        [
            "release_id",
            "hospital_id",
            "stable_error_rate",
            "canary_error_rate",
            "canary_error_difference",
            "stable_latency_ms",
            "latency_ms",
            "canary_latency_difference",
            "canary_risk"
        ]
    ].head(10)
)
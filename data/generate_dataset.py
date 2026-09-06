import pandas as pd
import numpy as np

# Reproducible dataset
np.random.seed(42)

# Project configuration
NUM_RELEASES = 100
NUM_HOSPITALS = 50

data = []

for release_num in range(1, NUM_RELEASES + 1):

    release_id = f"R{release_num:03d}"
    version = f"v{2 + release_num // 50}.{release_num % 50 + 1}"

    # Decide whether this release is harmful
    harmful_release = np.random.random() < 0.30

    for hospital_num in range(1, NUM_HOSPITALS + 1):

        hospital_id = f"H{hospital_num:03d}"

        # -----------------------------
        # Rollout stage
        # -----------------------------
        rollout_stage = np.random.choice(
            [5, 10, 25, 50, 100],
            p=[0.30, 0.25, 0.20, 0.15, 0.10]
        )

        # -----------------------------
        # Stable version metrics
        # -----------------------------
        stable_error_rate = np.random.uniform(0.5, 2.0)
        stable_latency = np.random.uniform(100, 250)

        # -----------------------------
        # Healthy release
        # -----------------------------
        if not harmful_release:

            cpu_usage = np.random.normal(50, 10)
            memory_usage = np.random.normal(55, 8)

            error_rate = np.random.uniform(0.5, 3.0)
            latency_ms = np.random.uniform(100, 300)

            canary_error_rate = np.random.uniform(0.5, 3.0)

            error_budget_remaining = np.random.uniform(50, 100)

            deployment_status = np.random.choice(
                ["SUCCESS", "IN_PROGRESS"],
                p=[0.90, 0.10]
            )

        # -----------------------------
        # Harmful release
        # -----------------------------
        else:

            cpu_usage = np.random.normal(75, 12)
            memory_usage = np.random.normal(75, 10)

            error_rate = np.random.uniform(5, 12)
            latency_ms = np.random.uniform(400, 800)

            # Canary becomes worse than stable
            canary_error_rate = np.random.uniform(5, 12)

            error_budget_remaining = np.random.uniform(0, 30)

            deployment_status = np.random.choice(
                ["SUCCESS", "FAILED", "ROLLED_BACK"],
                p=[0.55, 0.30, 0.15]
            )

        # Keep percentages within realistic boundaries
        cpu_usage = np.clip(cpu_usage, 0, 100)
        memory_usage = np.clip(memory_usage, 0, 100)

        # -----------------------------
        # Missing observations
        # -----------------------------
        # Around 3% of observations have
        # one missing monitoring value.

        if np.random.random() < 0.03:

            missing_column = np.random.choice([
                "cpu_usage",
                "memory_usage",
                "error_rate",
                "latency_ms"
            ])

        else:
            missing_column = None

        # -----------------------------
        # Noisy observations
        # -----------------------------
        # Around 2% contain an abnormal spike.

        if np.random.random() < 0.02:

            noisy_column = np.random.choice([
                "cpu_usage",
                "memory_usage",
                "error_rate",
                "latency_ms"
            ])

        else:
            noisy_column = None

        # -----------------------------
        # Build row
        # -----------------------------

        row = {
            "release_id": release_id,
            "hospital_id": hospital_id,
            "version": version,
            "rollout_stage": rollout_stage,

            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2),
            "error_rate": round(error_rate, 2),
            "latency_ms": round(latency_ms, 2),

            "error_budget_remaining": round(
                error_budget_remaining, 2
            ),

            "stable_error_rate": round(
                stable_error_rate, 2
            ),

            "stable_latency_ms": round(
                stable_latency, 2
            ),

            "canary_error_rate": round(
                canary_error_rate, 2
            ),

            "deployment_status": deployment_status,

            # Ground truth used only for evaluation
            "harmful": harmful_release
        }

        # -----------------------------
        # Apply missing value
        # -----------------------------

        if missing_column:
            row[missing_column] = np.nan

        # -----------------------------
        # Apply noisy value
        # -----------------------------

        if noisy_column:

            if noisy_column == "cpu_usage":
                row["cpu_usage"] = 100

            elif noisy_column == "memory_usage":
                row["memory_usage"] = 100

            elif noisy_column == "error_rate":
                row["error_rate"] *= 4

            elif noisy_column == "latency_ms":
                row["latency_ms"] *= 4

        data.append(row)


# -----------------------------
# Create DataFrame
# -----------------------------

df = pd.DataFrame(data)

# -----------------------------
# Save dataset
# -----------------------------

output_path = "data/releases_raw.csv"

df.to_csv(output_path, index=False)

# -----------------------------
# Dataset information
# -----------------------------

print("=" * 60)
print("Healthcare Release Risk Monitor")
print("Synthetic Dataset Generator")
print("=" * 60)

print(f"\nTotal rows       : {len(df)}")
print(f"Total columns    : {len(df.columns)}")
print(f"Releases         : {df['release_id'].nunique()}")
print(f"Hospitals        : {df['hospital_id'].nunique()}")
print(f"Versions         : {df['version'].nunique()}")

print("\nHarmful releases:")
print(df["harmful"].value_counts())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDeployment status:")
print(df["deployment_status"].value_counts())

print("\nRollout stages:")
print(df["rollout_stage"].value_counts().sort_index())

print(f"\nDataset saved to: {output_path}")
print("=" * 60)
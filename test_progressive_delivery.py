import pandas as pd

from core.progressive_delivery import (
    simulate_all_releases
)


# Load evaluated releases
df = pd.read_csv(
    "data/releases_evaluated.csv"
)


# Simulate rollout
rollout_events = simulate_all_releases(df)


print("=" * 70)
print("PROGRESSIVE DELIVERY TEST")
print("=" * 70)


print("\nTotal releases:")
print(len(df))


print("\nTotal rollout events:")
print(len(rollout_events))


print("\nRollout actions:")
print(
    rollout_events["action"].value_counts()
)


print("\nRollout percentages:")
print(
    rollout_events["rollout_percentage"].value_counts()
)


print("\nSample:")
print(
    rollout_events.head(20).to_string(
        index=False
    )
)


# Save result
rollout_events.to_csv(
    "data/progressive_rollout_events.csv",
    index=False
)


print("\nSaved:")
print(
    "data/progressive_rollout_events.csv"
)
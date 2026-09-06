import pandas as pd

from core.progressive_delivery import (
    simulate_all_releases,
    save_rollout_events
)


INPUT_FILE = "data/releases_evaluated.csv"
OUTPUT_FILE = "data/rollout_events.csv"


print("=" * 60)
print("PROGRESSIVE ROLLOUT EVENT GENERATOR")
print("=" * 60)


# Load evaluated releases
df = pd.read_csv(INPUT_FILE)

print(f"Loaded releases: {len(df)}")


# Generate rollout events
events = simulate_all_releases(df)

print(f"Generated rollout events: {len(events)}")


# Save events
save_rollout_events(
    events,
    OUTPUT_FILE
)


print(f"Saved to: {OUTPUT_FILE}")

print("\nFirst 10 events:")
print(events.head(10))


print("\nAction distribution:")
print(
    events["action"].value_counts()
)

print("\n" + "=" * 60)
print("COMPLETED")
print("=" * 60)
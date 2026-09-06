import pandas as pd

from core.deployment_events import generate_deployment_events


# Load evaluated releases
df = pd.read_csv(
    "data/releases_evaluated.csv"
)


# Generate deployment history
events = generate_deployment_events(df)


print("=" * 70)
print("DEPLOYMENT EVENT TEST")
print("=" * 70)


print("\nTotal release records:")
print(len(df))


print("\nTotal deployment events:")
print(len(events))


print("\nEvent types:")
print(
    events["event_type"].value_counts()
)


print("\nSample events:")

print(
    events[
        [
            "release_id",
            "hospital_id",
            "version",
            "event_type",
            "decision",
            "timestamp"
        ]
    ].head(20).to_string(index=False)
)


# Save event log
events.to_csv(
    "data/deployment_events.csv",
    index=False
)


print("\nSaved:")
print("data/deployment_events.csv")
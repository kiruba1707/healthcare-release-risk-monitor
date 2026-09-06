import pandas as pd

from core.deployment_events import generate_deployment_events


def test_deployment_events_generated():
    df = pd.read_csv("data/releases_evaluated.csv")

    events = generate_deployment_events(df)

    assert events is not None
    assert len(events) > 0


def test_deployment_event_columns():
    df = pd.read_csv("data/releases_evaluated.csv")

    events = generate_deployment_events(df)

    required_columns = [
        "release_id",
        "hospital_id",
        "version",
        "event_type",
        "decision",
        "timestamp",
    ]

    for column in required_columns:
        assert column in events.columns


def test_deployment_events_match_records():
    df = pd.read_csv("data/releases_evaluated.csv")

    events = generate_deployment_events(df)

    assert len(events) >= len(df)

    assert events["release_id"].notna().all()
    assert events["hospital_id"].notna().all()
    assert events["version"].notna().all()
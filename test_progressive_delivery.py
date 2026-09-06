import pandas as pd

from core.progressive_delivery import simulate_all_releases


def load_evaluated_data():
    return pd.read_csv("data/releases_evaluated.csv")


def test_rollout_events_generated():
    df = load_evaluated_data()

    rollout_events = simulate_all_releases(df)

    assert len(rollout_events) > 0


def test_rollout_required_columns():
    df = load_evaluated_data()

    rollout_events = simulate_all_releases(df)

    required_columns = [
        "release_id",
        "hospital_id",
        "version",
        "action",
        "rollout_percentage",
    ]

    for column in required_columns:
        assert column in rollout_events.columns


def test_rollout_percentages():
    df = load_evaluated_data()

    rollout_events = simulate_all_releases(df)

    valid_percentages = {5, 25, 50, 100}

    assert set(rollout_events["rollout_percentage"].unique()).issubset(
        valid_percentages
    )


def test_rollout_actions():
    df = load_evaluated_data()

    rollout_events = simulate_all_releases(df)

    valid_actions = {"CONTINUE", "HOLD", "STOP"}

    assert set(rollout_events["action"].unique()).issubset(
        valid_actions
    )

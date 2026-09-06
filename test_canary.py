import pandas as pd

from core.canary import calculate_canary_risk


def test_canary_risk_calculation():
    df = pd.read_csv("data/releases_raw.csv")

    result = calculate_canary_risk(df)

    assert "canary_risk" in result.columns
    assert "canary_error_difference" in result.columns
    assert "canary_latency_difference" in result.columns

    assert len(result) == len(df)
    assert result["canary_risk"].notna().all()


def test_canary_comparison_columns():
    df = pd.read_csv("data/releases_raw.csv")

    result = calculate_canary_risk(df)

    required_columns = [
        "stable_error_rate",
        "canary_error_rate",
        "stable_latency_ms",
        "latency_ms",
        "canary_error_difference",
        "canary_latency_difference",
        "canary_risk",
    ]

    for column in required_columns:
        assert column in result.columns


def test_canary_risk_values_are_valid():
    df = pd.read_csv("data/releases_raw.csv")

    result = calculate_canary_risk(df)

    assert result["canary_risk"].isin(
        ["SAFE", "WARNING", "CRITICAL", "UNKNOWN"]
    ).all()

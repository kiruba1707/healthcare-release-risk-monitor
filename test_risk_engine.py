import pandas as pd

from core.noise_handler import clean_dataset
from core.canary import calculate_canary_risk
from core.error_budget import calculate_error_budget_risk
from core.fallback import apply_fallback
from core.risk_engine import evaluate_dataset


def prepare_risk_data():
    df = pd.read_csv("data/releases_raw.csv")

    df = clean_dataset(df)
    df = calculate_error_budget_risk(df)
    df = calculate_canary_risk(df)
    df = apply_fallback(df)
    df = evaluate_dataset(df)

    return df


def test_risk_columns_exist():
    df = prepare_risk_data()

    assert "risk_score" in df.columns
    assert "risk_decision" in df.columns


def test_risk_score_is_numeric():
    df = prepare_risk_data()

    assert pd.api.types.is_numeric_dtype(df["risk_score"])


def test_risk_decisions_are_valid():
    df = prepare_risk_data()

    valid_decisions = {"SAFE", "WARNING", "HOLD", "BLOCK"}

    assert set(df["risk_decision"].dropna().unique()).issubset(
        valid_decisions
    )


def test_risk_score_has_values():
    df = prepare_risk_data()

    assert df["risk_score"].notna().all()
    assert len(df) > 0

import pandas as pd

from core.noise_handler import clean_dataset
from core.error_budget import calculate_error_budget_risk
from core.fallback import apply_fallback


def prepare_fallback_data():
    df = pd.read_csv("data/releases_raw.csv")

    df = clean_dataset(df)
    df = calculate_error_budget_risk(df)
    df = apply_fallback(df)

    return df


def test_error_budget_calculation():
    df = prepare_fallback_data()

    assert "error_budget_status" in df.columns
    assert df["error_budget_status"].notna().all()


def test_fallback_action_generated():
    df = prepare_fallback_data()

    assert "fallback_action" in df.columns
    assert df["fallback_action"].notna().all()


def test_fallback_preserves_dataset_size():
    original = pd.read_csv("data/releases_raw.csv")
    result = prepare_fallback_data()

    assert len(result) == len(original)

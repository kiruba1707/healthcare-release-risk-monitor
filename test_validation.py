import pandas as pd

from core.noise_handler import clean_dataset


def test_clean_dataset_preserves_row_count():
    df = pd.read_csv("data/releases_raw.csv")

    result = clean_dataset(df)

    assert len(result) == len(df)


def test_clean_dataset_creates_quality_flags():
    df = pd.read_csv("data/releases_raw.csv")

    result = clean_dataset(df)

    assert "missing_metric" in result.columns
    assert "noisy_metric" in result.columns


def test_quality_flags_are_boolean():
    df = pd.read_csv("data/releases_raw.csv")

    result = clean_dataset(df)

    assert result["missing_metric"].dtype == bool
    assert result["noisy_metric"].dtype == bool

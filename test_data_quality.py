import pandas as pd

from core.noise_handler import (
    clean_dataset,
    get_data_quality_summary
)


def test_data_quality_cleaning():
    df = pd.read_csv("data/releases_raw.csv")

    cleaned_df = clean_dataset(df)

    assert len(cleaned_df) == len(df)
    assert "missing_metric" in cleaned_df.columns
    assert "noisy_metric" in cleaned_df.columns


def test_data_quality_summary():
    df = pd.read_csv("data/releases_raw.csv")

    cleaned_df = clean_dataset(df)
    summary = get_data_quality_summary(cleaned_df)

    assert "total_rows" in summary
    assert "rows_with_missing_metrics" in summary
    assert "rows_with_noisy_metrics" in summary

    assert summary["total_rows"] == len(cleaned_df)

    assert summary["rows_with_missing_metrics"] >= 0
    assert summary["rows_with_noisy_metrics"] >= 0
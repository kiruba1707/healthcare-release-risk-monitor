import pandas as pd
import numpy as np


METRIC_COLUMNS = [
    "cpu_usage",
    "memory_usage",
    "error_rate",
    "latency_ms"
]


def handle_missing_values(df):
    """
    Detect missing monitoring observations.

    We do NOT blindly replace missing values with zero,
    because zero could incorrectly look like a healthy metric.
    """

    df = df.copy()

    df["missing_metric"] = df[METRIC_COLUMNS].isnull().any(axis=1)

    return df


def detect_noisy_values(df):
    """
    Detect suspicious metric spikes using simple thresholds.
    """

    df = df.copy()

    df["noisy_metric"] = False

    # Suspicious CPU
    if "cpu_usage" in df.columns:
        df.loc[
            df["cpu_usage"].notna() & (df["cpu_usage"] > 95),
            "noisy_metric"
        ] = True

    # Suspicious memory
    if "memory_usage" in df.columns:
        df.loc[
            df["memory_usage"].notna() & (df["memory_usage"] > 95),
            "noisy_metric"
        ] = True

    # Suspicious error rate
    if "error_rate" in df.columns:
        df.loc[
            df["error_rate"].notna() & (df["error_rate"] > 15),
            "noisy_metric"
        ] = True

    # Suspicious latency
    if "latency_ms" in df.columns:
        df.loc[
            df["latency_ms"].notna() & (df["latency_ms"] > 2000),
            "noisy_metric"
        ] = True

    return df


def clean_dataset(df):
    """
    Main preprocessing pipeline.
    """

    df = df.copy()

    # Detect missing observations
    df = handle_missing_values(df)

    # Detect noisy observations
    df = detect_noisy_values(df)

    return df


def get_data_quality_summary(df):
    """
    Return summary of missing and noisy observations.
    """

    summary = {
        "total_rows": len(df),
        "rows_with_missing_metrics": int(
            df["missing_metric"].sum()
        ),
        "rows_with_noisy_metrics": int(
            df["noisy_metric"].sum()
        )
    }

    return summary
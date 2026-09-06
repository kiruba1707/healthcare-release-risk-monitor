import pandas as pd


def compare_error_rate(stable_error_rate, canary_error_rate):
    """
    Compare error rates between stable and canary versions.

    Positive value means canary is worse.
    """

    if pd.isna(stable_error_rate) or pd.isna(canary_error_rate):
        return None

    return canary_error_rate - stable_error_rate


def compare_latency(stable_latency, canary_latency):
    """
    Compare latency between stable and canary versions.

    Positive value means canary is slower.
    """

    if pd.isna(stable_latency) or pd.isna(canary_latency):
        return None

    return canary_latency - stable_latency


def calculate_canary_error_ratio(
    stable_error_rate,
    canary_error_rate
):
    """
    Calculate how many times worse the canary
    error rate is compared with stable.
    """

    if pd.isna(stable_error_rate) or pd.isna(canary_error_rate):
        return None

    if stable_error_rate <= 0:
        return None

    return canary_error_rate / stable_error_rate


def classify_canary_risk(
    stable_error_rate,
    canary_error_rate,
    stable_latency,
    canary_latency
):
    """
    Classify canary comparison.

    SAFE:
        Canary is similar to stable.

    WARNING:
        Canary is moderately worse.

    CRITICAL:
        Canary is significantly worse.
    """

    error_difference = compare_error_rate(
        stable_error_rate,
        canary_error_rate
    )

    latency_difference = compare_latency(
        stable_latency,
        canary_latency
    )

    if error_difference is None or latency_difference is None:
        return "UNKNOWN"

    # Canary error rate more than 2 percentage points worse
    # OR latency more than 200 ms worse
    if error_difference > 2 or latency_difference > 200:
        return "CRITICAL"

    # Canary error rate more than 1 percentage point worse
    # OR latency more than 100 ms worse
    if error_difference > 1 or latency_difference > 100:
        return "WARNING"

    return "SAFE"


def calculate_canary_risk(df):
    """
    Add canary comparison results to the dataset.
    """

    df = df.copy()

    df["canary_error_difference"] = (
        df["canary_error_rate"]
        - df["stable_error_rate"]
    )

    df["canary_latency_difference"] = (
        df["latency_ms"]
        - df["stable_latency_ms"]
    )

    df["canary_error_ratio"] = (
        df["canary_error_rate"]
        / df["stable_error_rate"]
    )

    df["canary_risk"] = df.apply(
        lambda row: classify_canary_risk(
            row["stable_error_rate"],
            row["canary_error_rate"],
            row["stable_latency_ms"],
            row["latency_ms"]
        ),
        axis=1
    )

    return df
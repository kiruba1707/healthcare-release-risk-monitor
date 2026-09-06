import pandas as pd


REQUIRED_COLUMNS = [
    "release_id",
    "hospital_id",
    "version",
    "rollout_stage",
    "cpu_usage",
    "memory_usage",
    "error_rate",
    "latency_ms",
    "error_budget_remaining",
    "stable_error_rate",
    "stable_latency_ms",
    "canary_error_rate",
    "deployment_status"
]


def validate_columns(df):
    """
    Check whether all required columns exist.
    """

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        return False, missing_columns

    return True, []


def validate_ranges(df):
    """
    Check whether metric values are within
    physically/logically valid ranges.
    """

    problems = []

    # CPU must be between 0 and 100
    if "cpu_usage" in df.columns:
        invalid_cpu = (
            df["cpu_usage"].notna()
            & ~df["cpu_usage"].between(0, 100)
        )

        if invalid_cpu.any():
            problems.append(
                f"Invalid CPU values: {invalid_cpu.sum()}"
            )

    # Memory must be between 0 and 100
    if "memory_usage" in df.columns:
        invalid_memory = (
            df["memory_usage"].notna()
            & ~df["memory_usage"].between(0, 100)
        )

        if invalid_memory.any():
            problems.append(
                f"Invalid memory values: {invalid_memory.sum()}"
            )

    # Error rate cannot be negative
    if "error_rate" in df.columns:
        invalid_errors = (
            df["error_rate"].notna()
            & (df["error_rate"] < 0)
        )

        if invalid_errors.any():
            problems.append(
                f"Invalid error rates: {invalid_errors.sum()}"
            )

    # Latency cannot be negative
    if "latency_ms" in df.columns:
        invalid_latency = (
            df["latency_ms"].notna()
            & (df["latency_ms"] < 0)
        )

        if invalid_latency.any():
            problems.append(
                f"Invalid latency values: {invalid_latency.sum()}"
            )

    return problems


def check_missing_values(df):
    """
    Report missing monitoring observations.
    """

    missing = df.isnull().sum()

    return missing[missing > 0].to_dict()


def validate_dataset(df):
    """
    Run all validation checks.
    """

    results = {
        "valid_columns": True,
        "missing_columns": [],
        "range_problems": [],
        "missing_values": {}
    }

    # Column validation
    valid, missing_columns = validate_columns(df)

    results["valid_columns"] = valid
    results["missing_columns"] = missing_columns

    # Range validation
    results["range_problems"] = validate_ranges(df)

    # Missing values
    results["missing_values"] = check_missing_values(df)

    return results
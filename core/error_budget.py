import pandas as pd


def calculate_error_budget_status(error_budget_remaining):
    """
    Classify the remaining error budget.
    """

    if pd.isna(error_budget_remaining):
        return "UNKNOWN"

    if error_budget_remaining <= 10:
        return "CRITICAL"

    if error_budget_remaining <= 30:
        return "LOW"

    return "HEALTHY"


def calculate_error_budget_risk(df):
    """
    Add an error-budget risk classification.
    """

    df = df.copy()

    df["error_budget_status"] = (
        df["error_budget_remaining"]
        .apply(calculate_error_budget_status)
    )

    return df
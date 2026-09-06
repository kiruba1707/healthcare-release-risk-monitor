import json
import pandas as pd


def load_config(config_path="config.json"):
    """
    Load configurable risk rules.
    """

    with open(config_path, "r") as file:
        return json.load(file)


def calculate_metric_risk(value, warning, critical):
    """
    Return risk points for a metric.
    """

    if pd.isna(value):
        return 0

    if value >= critical:
        return 2

    if value >= warning:
        return 1

    return 0


def calculate_error_budget_risk(value, config):
    """
    Calculate risk based on remaining error budget.
    """

    if pd.isna(value):
        return 1

    thresholds = config["thresholds"]

    if value <= thresholds["error_budget_critical"]:
        return 2

    if value <= thresholds["error_budget_low"]:
        return 1

    return 0


def calculate_canary_risk(canary_status):
    """
    Convert canary classification into risk level.
    """

    if canary_status == "CRITICAL":
        return 2

    if canary_status == "WARNING":
        return 1

    if canary_status == "UNKNOWN":
        return 1

    return 0


def calculate_deployment_risk(status):
    """
    Deployment failure increases risk.
    """

    if status == "FAILED":
        return 2

    if status == "ROLLED_BACK":
        return 2

    if status == "IN_PROGRESS":
        return 1

    return 0


def calculate_risk_score(row, config):
    """
    Combine all monitoring signals into a risk score.
    """

    thresholds = config["thresholds"]
    weights = config["weights"]

    score = 0

    # CPU
    cpu_risk = calculate_metric_risk(
        row["cpu_usage"],
        thresholds["cpu_warning"],
        thresholds["cpu_critical"]
    )

    score += cpu_risk * weights["cpu"]

    # Memory
    memory_risk = calculate_metric_risk(
        row["memory_usage"],
        thresholds["memory_warning"],
        thresholds["memory_critical"]
    )

    score += memory_risk * weights["memory"]

    # Error rate
    error_risk = calculate_metric_risk(
        row["error_rate"],
        thresholds["error_rate_warning"],
        thresholds["error_rate_critical"]
    )

    score += error_risk * weights["error_rate"]

    # Latency
    latency_risk = calculate_metric_risk(
        row["latency_ms"],
        thresholds["latency_warning"],
        thresholds["latency_critical"]
    )

    score += latency_risk * weights["latency"]

    # Error budget
    budget_risk = calculate_error_budget_risk(
        row["error_budget_remaining"],
        config
    )

    score += budget_risk * weights["error_budget"]

    # Canary
    canary_risk = calculate_canary_risk(
        row["canary_risk"]
    )

    score += canary_risk * weights["canary"]

    # Deployment status
    deployment_risk = calculate_deployment_risk(
        row["deployment_status"]
    )

    score += deployment_risk * weights["deployment"]

    return score


def make_decision(row, score, config):
    """
    Convert risk score into a release decision.
    """

    thresholds = config["thresholds"]

    # Secure default:
    # incomplete or unreliable data should not
    # automatically allow rollout.

    if row.get("missing_metric", False):
        return "HOLD"

    if row.get("noisy_metric", False):
        return "HOLD"

    if row["canary_risk"] == "CRITICAL":
        return "BLOCK"

    if score >= thresholds["risk_block"]:
        return "BLOCK"

    if score >= thresholds["risk_warning"]:
        return "WARNING"

    return "SAFE"


def evaluate_release(row, config):
    """
    Calculate score and final decision.
    """

    score = calculate_risk_score(row, config)

    decision = make_decision(
        row,
        score,
        config
    )

    return score, decision


def evaluate_dataset(df, config_path="config.json"):
    """
    Evaluate complete dataset.
    """

    config = load_config(config_path)

    df = df.copy()

    results = df.apply(
        lambda row: evaluate_release(row, config),
        axis=1
    )

    df["risk_score"] = results.apply(
        lambda result: result[0]
    )

    df["risk_decision"] = results.apply(
        lambda result: result[1]
    )

    return df
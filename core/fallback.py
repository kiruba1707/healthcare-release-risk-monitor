import json
import os
from datetime import datetime


QUEUE_FILE = "data/fallback_queue.json"


def ensure_queue():
    """Create fallback queue if it does not exist."""

    os.makedirs("data", exist_ok=True)

    if not os.path.exists(QUEUE_FILE):

        with open(QUEUE_FILE, "w") as file:
            json.dump([], file, indent=4)


def store_event(event):
    """
    Store a deployment event when monitoring is unavailable.
    """

    ensure_queue()

    with open(QUEUE_FILE, "r") as file:
        queue = json.load(file)

    event["stored_at"] = datetime.now().isoformat()
    event["status"] = "PENDING"

    queue.append(event)

    with open(QUEUE_FILE, "w") as file:
        json.dump(queue, file, indent=4)

    return True


def get_stored_events():
    """Return all pending events."""

    ensure_queue()

    with open(QUEUE_FILE, "r") as file:
        queue = json.load(file)

    return queue


def clear_stored_events():
    """Clear processed fallback events."""

    ensure_queue()

    with open(QUEUE_FILE, "w") as file:
        json.dump([], file, indent=4)


def fallback_decision(monitoring_available):
    """
    Fail-safe decision when monitoring is unavailable.
    """

    if not monitoring_available:
        return "HOLD"

    return "PROCESS"


def process_stored_events(process_function):
    """
    Process all events that were stored while
    monitoring was unavailable.
    """

    ensure_queue()

    events = get_stored_events()

    if not events:
        return []

    results = []

    for event in events:

        try:
            result = process_function(event)

            event["status"] = "PROCESSED"
            event["result"] = result

            results.append(event)

        except Exception as error:

            event["status"] = "FAILED"
            event["error"] = str(error)

            results.append(event)

    # Keep only events that failed.
    pending_events = [
        event
        for event in results
        if event["status"] == "FAILED"
    ]

    with open(QUEUE_FILE, "w") as file:
        json.dump(
            pending_events,
            file,
            indent=4
        )

    return results

def apply_fallback(df):
    """
    Apply fail-safe fallback policy.
    """

    df = df.copy()

    df["fallback_action"] = "PROCESS"

    if "missing_metric" in df.columns:
        df.loc[
            df["missing_metric"] == True,
            "fallback_action"
        ] = "HOLD"

    if "noisy_metric" in df.columns:
        df.loc[
            df["noisy_metric"] == True,
            "fallback_action"
        ] = "HOLD"

    return df
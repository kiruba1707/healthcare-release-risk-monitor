import json
import os
from datetime import datetime


AUDIT_FILE = "data/audit_log.json"


def write_audit_log(
    username,
    role,
    action,
    resource,
    result
):
    """
    Record an important system action.
    """

    os.makedirs("data", exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "username": username,
        "role": role,
        "action": action,
        "resource": resource,
        "result": result
    }

    logs = []

    if os.path.exists(AUDIT_FILE):

        try:
            with open(AUDIT_FILE, "r") as file:
                logs = json.load(file)

        except (json.JSONDecodeError, OSError):
            logs = []

    logs.append(log_entry)

    with open(AUDIT_FILE, "w") as file:
        json.dump(
            logs,
            file,
            indent=4
        )


def read_audit_logs():
    """
    Read stored audit events.
    """

    if not os.path.exists(AUDIT_FILE):
        return []

    try:
        with open(AUDIT_FILE, "r") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []
import json
import os
from datetime import datetime


BUFFER_FILE = "data/offline_buffer.json"


def _load_buffer():
    """
    Load events currently waiting in the local buffer.
    """

    if not os.path.exists(BUFFER_FILE):
        return []

    try:
        with open(BUFFER_FILE, "r") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def _save_buffer(events):
    """
    Save events to the local offline buffer.
    """

    os.makedirs("data", exist_ok=True)

    with open(BUFFER_FILE, "w") as file:
        json.dump(events, file, indent=4)


def store_event(event):
    """
    Store an event locally when the monitoring
    service is unavailable.
    """

    buffer = _load_buffer()

    event = dict(event)

    event["stored_at"] = datetime.now().isoformat()

    buffer.append(event)

    _save_buffer(buffer)

    return True


def get_buffered_events():
    """
    Return all events waiting to be forwarded.
    """

    return _load_buffer()


def forward_events(server_available=True):
    """
    Forward buffered events when the server becomes available.

    In this prototype, forwarding is simulated.
    """

    buffer = _load_buffer()

    if not server_available:
        return {
            "status": "OFFLINE",
            "forwarded": 0,
            "remaining": len(buffer)
        }

    forwarded = len(buffer)

    # Simulate successful forwarding.
    _save_buffer([])

    return {
        "status": "FORWARDED",
        "forwarded": forwarded,
        "remaining": 0
    }
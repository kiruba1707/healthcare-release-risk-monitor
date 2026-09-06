import pandas as pd


EVENT_SEQUENCE = [
    "RELEASE_CREATED",
    "DEPLOYMENT_STARTED",
    "CANARY_STARTED",
    "CANARY_EVALUATED",
    "ROLLOUT_DECISION",
    "DEPLOYMENT_COMPLETED"
]


def create_deployment_event(
    release_id,
    hospital_id,
    version,
    event_type,
    decision=None,
    timestamp=None
):
    """
    Create one deployment event.
    """

    return {
        "release_id": release_id,
        "hospital_id": hospital_id,
        "version": version,
        "event_type": event_type,
        "decision": decision,
        "timestamp": timestamp
    }


def generate_deployment_events(df):
    """
    Generate a deployment event history for each release.
    """

    events = []

    base_time = pd.Timestamp("2026-01-01 08:00:00")

    for index, row in df.iterrows():

        release_id = row["release_id"]
        hospital_id = row["hospital_id"]
        version = row["version"]

        risk_decision = row.get(
            "risk_decision",
            "UNKNOWN"
        )

        current_time = (
            base_time
            + pd.Timedelta(minutes=index * 10)
        )

        # Release created
        events.append(
            create_deployment_event(
                release_id,
                hospital_id,
                version,
                "RELEASE_CREATED",
                timestamp=current_time
            )
        )

        # Deployment started
        events.append(
            create_deployment_event(
                release_id,
                hospital_id,
                version,
                "DEPLOYMENT_STARTED",
                timestamp=current_time
                + pd.Timedelta(minutes=1)
            )
        )

        # Canary started
        events.append(
            create_deployment_event(
                release_id,
                hospital_id,
                version,
                "CANARY_STARTED",
                timestamp=current_time
                + pd.Timedelta(minutes=2)
            )
        )

        # Canary evaluated
        events.append(
            create_deployment_event(
                release_id,
                hospital_id,
                version,
                "CANARY_EVALUATED",
                decision=risk_decision,
                timestamp=current_time
                + pd.Timedelta(minutes=5)
            )
        )

        # Decision
        events.append(
            create_deployment_event(
                release_id,
                hospital_id,
                version,
                "ROLLOUT_DECISION",
                decision=risk_decision,
                timestamp=current_time
                + pd.Timedelta(minutes=6)
            )
        )

        # Complete only if safe
        if risk_decision == "SAFE":

            events.append(
                create_deployment_event(
                    release_id,
                    hospital_id,
                    version,
                    "DEPLOYMENT_COMPLETED",
                    decision="SAFE",
                    timestamp=current_time
                    + pd.Timedelta(minutes=10)
                )
            )

        else:

            events.append(
                create_deployment_event(
                    release_id,
                    hospital_id,
                    version,
                    "ROLLOUT_STOPPED",
                    decision=risk_decision,
                    timestamp=current_time
                    + pd.Timedelta(minutes=10)
                )
            )

    return pd.DataFrame(events)


    
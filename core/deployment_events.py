import pandas as pd


def create_deployment_event(
    release_id,
    hospital_id,
    version,
    event_type,
    decision=None,
    timestamp=None
):
    return {
        "release_id": release_id,
        "hospital_id": hospital_id,
        "version": version,
        "event_type": event_type,
        "decision": decision,
        "timestamp": timestamp
    }


def generate_deployment_events(df):

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

        # 1. Release created
        events.append(
            create_deployment_event(
                release_id,
                hospital_id,
                version,
                "RELEASE_CREATED",
                timestamp=current_time
            )
        )

        # 2. Deployment started
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

        # 3. Canary started
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

        # 4. Canary evaluated
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

        # 5. Rollout decision
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

        # 6. Final outcome
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
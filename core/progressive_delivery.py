import pandas as pd


ROLLOUT_STAGES = [
    5,
    25,
    50,
    100
]


def evaluate_stage(risk_decision):
    """
    Decide whether rollout can move to the next stage.
    """

    if risk_decision == "SAFE":
        return "CONTINUE"

    if risk_decision == "WARNING":
        return "HOLD"

    if risk_decision == "BLOCK":
        return "STOP"

    if risk_decision == "HOLD":
        return "HOLD"

    return "HOLD"


def simulate_progressive_rollout(row):
    """
    Simulate progressive rollout for one release.

    Rollout stages:
    5% → 25% → 50% → 100%
    """

    events = []

    release_id = row["release_id"]
    hospital_id = row["hospital_id"]
    version = row["version"]
    risk_decision = row["risk_decision"]

    for stage in ROLLOUT_STAGES:

        action = evaluate_stage(risk_decision)

        if action == "CONTINUE":

            events.append({
                "release_id": release_id,
                "hospital_id": hospital_id,
                "version": version,
                "rollout_percentage": stage,
                "action": "CONTINUE"
            })

        elif action == "HOLD":

            events.append({
                "release_id": release_id,
                "hospital_id": hospital_id,
                "version": version,
                "rollout_percentage": stage,
                "action": "HOLD"
            })

            break

        else:

            events.append({
                "release_id": release_id,
                "hospital_id": hospital_id,
                "version": version,
                "rollout_percentage": stage,
                "action": "STOP"
            })

            break

    return events


def simulate_all_releases(df):
    """
    Simulate progressive rollout for all releases.
    """

    all_events = []

    for _, row in df.iterrows():

        events = simulate_progressive_rollout(row)

        all_events.extend(events)

    return pd.DataFrame(all_events)



def save_rollout_events(events_df, output_path):
    """
    Save progressive rollout events to CSV.
    """

    events_df.to_csv(
        output_path,
        index=False
    )
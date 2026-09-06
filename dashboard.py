import json
import pandas as pd
import streamlit as st



from core.progressive_delivery import simulate_progressive_rollout

from core.auth import authenticate, has_permission
from core.audit_log import (
    write_audit_log,
    read_audit_logs
)
from core.risk_engine import evaluate_release


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Healthcare Release Risk Monitor",
    page_icon="🏥",
    layout="wide"
)


# ==========================================================
# LOAD DATA
# ==========================================================

@st.cache_data
def load_releases():

    try:
        return pd.read_csv(
            "data/releases_evaluated.csv"
        )

    except FileNotFoundError:
        return pd.DataFrame()


@st.cache_data
def load_events():

    try:
        return pd.read_csv(
            "data/deployment_events.csv"
        )

    except FileNotFoundError:
        return pd.DataFrame()


def load_config():

    try:
        with open("config.json", "r") as file:
            return json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        return {}


df = load_releases()
events = load_events()


# ==========================================================
# SESSION STATE
# ==========================================================

if "user" not in st.session_state:
    st.session_state.user = None


# ==========================================================
# LOGIN PAGE
# ==========================================================

if st.session_state.user is None:

    st.title("🏥 Healthcare Release Risk Monitor")

    st.subheader("Secure Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button("Login"):

        user = authenticate(
            username,
            password
        )

        if user:

            st.session_state.user = user

            write_audit_log(
                user["username"],
                user["role"],
                "LOGIN",
                "dashboard",
                "ALLOWED"
            )

            st.rerun()

        else:

            write_audit_log(
                username,
                "unknown",
                "LOGIN",
                "dashboard",
                "DENIED"
            )

            st.error(
                "Invalid username or password"
            )

    st.info(
        "Use the configured prototype accounts."
    )

    st.stop()


# ==========================================================
# USER INFORMATION
# ==========================================================

user = st.session_state.user

username = user["username"]
role = user["role"]


# ==========================================================
# SIDEBAR
# ==========================================================

st.sidebar.title("🏥 Release Monitor")

st.sidebar.success(
    f"Logged in as: {username}"
)

st.sidebar.write(
    f"Role: **{role}**"
)


if st.sidebar.button("Logout"):

    write_audit_log(
        username,
        role,
        "LOGOUT",
        "dashboard",
        "ALLOWED"
    )

    st.session_state.user = None

    st.rerun()


# ==========================================================
# HEADER
# ==========================================================

st.title(
    "🏥 Healthcare Release Risk Monitor"
)

st.caption(
    "Pre-release risk monitoring for hospital deployments"
)


# ==========================================================
# NO DATA
# ==========================================================

if df.empty:

    st.error(
        "No evaluated release data found."
    )

    st.stop()


# ==========================================================
# METRICS
# ==========================================================

total_releases = len(df)

total_hospitals = df["hospital_id"].nunique()

safe_count = (
    df["risk_decision"] == "SAFE"
).sum()

warning_count = (
    df["risk_decision"] == "WARNING"
).sum()

block_count = (
    df["risk_decision"] == "BLOCK"
).sum()

hold_count = (
    df["risk_decision"] == "HOLD"
).sum()


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "🏥 Hospitals",
    total_hospitals
)

col2.metric(
    "📦 Releases",
    total_releases
)

col3.metric(
    "✅ Safe",
    safe_count
)

col4.metric(
    "⚠️ Warning",
    warning_count
)

col5.metric(
    "🛑 Blocked",
    block_count
)


st.divider()


# ==========================================================
# DECISION DISTRIBUTION
# ==========================================================

st.subheader(
    "Release Decision Distribution"
)

decision_counts = (
    df["risk_decision"]
    .value_counts()
)

st.bar_chart(
    decision_counts
)


# ==========================================================
# RISK SCORE
# ==========================================================

st.subheader(
    "Risk Score Distribution"
)

st.line_chart(
    df["risk_score"]
    .head(100)
)


# ==========================================================
# RELEASE TABLE
# ==========================================================

st.subheader(
    "Release Monitoring"
)

columns = [
    "release_id",
    "hospital_id",
    "version",
    "cpu_usage",
    "memory_usage",
    "error_rate",
    "latency_ms",
    "error_budget_remaining",
    "canary_risk",
    "risk_score",
    "risk_decision"
]

available_columns = [
    column
    for column in columns
    if column in df.columns
]

# st.dataframe(
#     df[
#         available_columns
#     ].sort_values(
#         "risk_score",
#         ascending=False
#     ),
#     use_container_width=True,
#     height=450
# )


# ==========================================================
# ADMIN CONFIGURATION
# ==========================================================

if role == "operations_admin":

    st.divider()

    st.subheader(
        "⚙️ Risk Configuration"
    )

    config = load_config()

    thresholds = config.get(
        "thresholds",
        {}
    )

    st.write(
        "Current configurable thresholds"
    )

    config_df = pd.DataFrame(
        list(
            thresholds.items()
        ),
        columns=[
            "Rule",
            "Value"
        ]
    )

    st.dataframe(
        config_df,
        use_container_width=True
    )

    st.info(
        "Operations Admin can review the configured rules. "
        "Rule changes are intentionally restricted to the "
        "configuration layer."
    )


# ==========================================================
# AUDIT LOG
# ==========================================================

if has_permission(
    role,
    "view_audit_logs"
):

    st.divider()

    st.subheader(
        "🔐 Audit Logs"
    )

    logs = read_audit_logs()

    if logs:

        audit_df = pd.DataFrame(
            logs
        )

        st.dataframe(
            audit_df,
            use_container_width=True
        )

    else:

        st.info(
            "No audit events available."
        )


# ==========================================================
# SYSTEM INFORMATION
# ==========================================================

st.divider()

st.subheader(
    "System Status"
)

status_col1, status_col2 = st.columns(2)


status_col1.metric(
    "Deployment Events",
    len(events)
)

status_col2.metric(
    "Audit Events",
    len(read_audit_logs())
)


st.success("LIVE EVALUATION SECTION IS WORKING")
# ==========================================================
# LIVE RELEASE EVALUATION
# ==========================================================

st.divider()

st.subheader("🚀 Live Release Evaluation")

release_ids = df["release_id"].tolist()

selected_release = st.selectbox(
    "Select a release",
    release_ids
)

selected_row = df[
    df["release_id"] == selected_release
].iloc[0]



# ==========================================================
# PROGRESSIVE ROLLOUT MONITOR
# ==========================================================

st.divider()

st.subheader("📈 Progressive Rollout Monitor")

st.write(
    "This simulates how the selected release moves "
    "through controlled rollout stages."
)


# Generate rollout events for selected release
rollout_events = simulate_progressive_rollout(
    selected_row
)


if len(rollout_events) == 0:

    st.info(
        "No rollout events available."
    )

else:

    rollout_df = pd.DataFrame(
        rollout_events
    )

    # ------------------------------------------------------
# Determine rollout status
# ------------------------------------------------------

completed_stages = rollout_df[
    rollout_df["action"] == "CONTINUE"
]["rollout_percentage"].tolist()

stop_stages = rollout_df[
    rollout_df["action"] == "STOP"
]["rollout_percentage"].tolist()

hold_stages = rollout_df[
    rollout_df["action"] == "HOLD"
]["rollout_percentage"].tolist()


if completed_stages:

    current_stage = max(completed_stages)

elif stop_stages:

    current_stage = stop_stages[0]

elif hold_stages:

    current_stage = hold_stages[0]

else:

    current_stage = 0


st.metric(
    "Current Rollout",
    f"{current_stage}%"
)


# ------------------------------------------------------
# Overall rollout status
# ------------------------------------------------------

if stop_stages:

    st.error(
        f"🛑 Rollout stopped at {stop_stages[0]}%"
    )

elif hold_stages:

    st.warning(
        f"⏸️ Rollout held at {hold_stages[0]}%"
    )

elif 100 in completed_stages:

    st.success(
        "✅ Rollout completed successfully at 100%"
    )

else:

    st.info(
        f"🚀 Rollout can proceed from {current_stage}%"
    )


    # ------------------------------------------------------
    # Stage Table
    # ------------------------------------------------------

    st.dataframe(
        rollout_df,
        use_container_width=True,
        hide_index=True
    )


    # ------------------------------------------------------
    # Visual Rollout Pipeline
    # ------------------------------------------------------

    st.write("### Rollout Pipeline")


    stages = [
        5,
        25,
        50,
        100
    ]


    cols = st.columns(4)


    for i, stage in enumerate(stages):

        with cols[i]:

            stage_data = rollout_df[
                rollout_df[
                    "rollout_percentage"
                ] == stage
            ]


            if stage_data.empty:

                st.metric(
                    f"{stage}%",
                    "NOT REACHED"
                )

            else:

                action = stage_data.iloc[0]["action"]

                if action == "CONTINUE":

                    st.success(
                        f"{stage}%\n\nCONTINUE"
                    )

                elif action == "HOLD":

                    st.warning(
                        f"{stage}%\n\nHOLD"
                    )

                elif action == "STOP":

                    st.error(
                        f"{stage}%\n\nSTOP"
                    )

# ----------------------------------------------------------
# Release Information
# ----------------------------------------------------------

st.write(
    f"### Release {selected_row['release_id']}"
)

info1, info2, info3 = st.columns(3)

info1.metric(
    "Hospital",
    selected_row["hospital_id"]
)

info2.metric(
    "Version",
    selected_row["version"]
)

info3.metric(
    "Deployment",
    selected_row["deployment_status"]
)


# ----------------------------------------------------------
# Health Metrics
# ----------------------------------------------------------

st.subheader("Health Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "CPU",
    f"{selected_row['cpu_usage']:.2f}%"
)

col2.metric(
    "Memory",
    f"{selected_row['memory_usage']:.2f}%"
)

col3.metric(
    "Error Rate",
    f"{selected_row['error_rate']:.2f}%"
)

col4.metric(
    "Latency",
    f"{selected_row['latency_ms']:.0f} ms"
)


# ----------------------------------------------------------
# Progressive Delivery Signals
# ----------------------------------------------------------

st.subheader("Progressive Delivery Signals")

col5, col6, col7 = st.columns(3)

col5.metric(
    "Error Budget",
    f"{selected_row['error_budget_remaining']:.1f}%"
)

col6.metric(
    "Canary Risk",
    selected_row["canary_risk"]
)

col7.metric(
    "Risk Score",
    f"{selected_row['risk_score']:.0f}"
)


# ----------------------------------------------------------
# Final Decision
# ----------------------------------------------------------

decision = selected_row["risk_decision"]

st.subheader("Final Release Decision")


if decision == "SAFE":

    st.success(
        "✅ SAFE — Release can proceed"
    )

elif decision == "WARNING":

    st.warning(
        "⚠️ WARNING — Release requires review"
    )

elif decision == "BLOCK":

    st.error(
        "🛑 BLOCK — Release must not proceed"
    )

else:

    st.warning(
        "⏸️ HOLD — Monitoring data is insufficient"
    )


# ----------------------------------------------------------
# Rollout Action
# ----------------------------------------------------------

st.subheader("Rollout Action")

if decision == "SAFE":

    if has_permission(
        role,
        "start_rollout"
    ):

        if st.button(
            "🚀 Start Canary Rollout"
        ):

            write_audit_log(
                username,
                role,
                "START_ROLLOUT",
                selected_release,
                "ALLOWED"
            )

            st.success(
                f"Canary rollout started for "
                f"{selected_release}"
            )

else:

    st.info(
        "Rollout is disabled because this release "
        "is not SAFE."
    )


if has_permission(
    role,
    "stop_rollout"
):

    if st.button(
        "🛑 Stop Rollout"
    ):

        write_audit_log(
            username,
            role,
            "STOP_ROLLOUT",
            selected_release,
            "EXECUTED"
        )

        st.warning(
            f"Rollout stopped for {selected_release}"
        )
import hashlib
import pandas as pd
import streamlit as st

from core.data_validator import validate_dataset
from core.noise_handler import clean_dataset
from core.error_budget import calculate_error_budget_risk
from core.canary import calculate_canary_risk
from core.fallback import apply_fallback
from core.risk_engine import evaluate_dataset
from core.auth import authenticate, has_permission


# ==========================================================
# CONFIGURATION
# ==========================================================

DATA_PATH = "data/releases_raw.csv"
ROLLOUT_STAGES = [5, 25, 50, 100]


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Healthcare Release Risk Monitor",
    page_icon="🏥",
    layout="wide"
)


# ==========================================================
# AUTHENTICATION
# ==========================================================

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None
if "monitoring_observation" not in st.session_state:
    st.session_state.monitoring_observation = None    


def show_login_page():
    st.title("🔐 Healthcare Release Risk Monitor")
    st.subheader("Secure Login")

    st.write("Please sign in to access the monitoring dashboard.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input(
            "Password",
            type="password"
        )

        submitted = st.form_submit_button(
            "Login",
            use_container_width=True
        )

        if submitted:
            user = authenticate(username, password)

            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.rerun()

            else:
                st.error("❌ Invalid username or password")


if not st.session_state.authenticated:
    show_login_page()
    st.stop()



  # ==========================================================
# ACCOUNT + LOGOUT
# ==========================================================

with st.sidebar:

    st.write(
        f"👤 **{st.session_state.user['username']}**"
    )

    st.caption(
        f"Role: {st.session_state.user['role']}"
    )

    st.divider()

    with st.expander("⚙️ Account Settings"):

        new_username = st.text_input(
            "New Username",
            value=st.session_state.user["username"],
            key="new_username"
        )

        current_password = st.text_input(
            "Current Password",
            type="password",
            key="current_password"
        )

        new_password = st.text_input(
            "New Password",
            type="password",
            key="new_password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "💾 Save Changes",
            use_container_width=True
        ):

            if not current_password:
                st.error("Enter your current password.")

            elif new_password and new_password != confirm_password:
                st.error("New passwords do not match.")

            elif new_password and len(new_password) < 6:
                st.error(
                    "New password must contain at least 6 characters."
                )

            else:
                from core.auth import change_credentials

                success, result = change_credentials(
                    current_username=st.session_state.user["username"],
                    current_password=current_password,
                    new_username=new_username,
                    new_password=new_password
                )

                if success:
                    st.session_state.user["username"] = result

                    st.success(
                        "Account details updated successfully."
                    )

                    st.rerun()

                else:
                    st.error(result)

    st.divider()

    if st.button(
        "🚪 Logout",
        use_container_width=True
    ):
        st.session_state.authenticated = False
        st.session_state.user = None

        st.session_state.pop(
            "monitoring_observation",
            None
        )

        st.rerun()

# ==========================================================
# COMMON RISK PIPELINE
# ==========================================================

def run_risk_pipeline(data):
    """Run the same validation/risk pipeline everywhere."""
    data = data.copy()

    data = clean_dataset(data)
    data = calculate_error_budget_risk(data)
    data = calculate_canary_risk(data)
    data = apply_fallback(data)
    data = evaluate_dataset(data)

    return data


# ==========================================================
# LOAD + EVALUATE DATASET
# ==========================================================

@st.cache_data
def load_evaluated_data():

    df = pd.read_csv(DATA_PATH)

    validation = validate_dataset(df)

    if not validation["valid_columns"]:
        raise ValueError(
            f"Missing required columns: "
            f"{validation['missing_columns']}"
        )

    df = run_risk_pipeline(df)

    # One unique key per hospital deployment.
    df["release_key"] = (
        df["release_id"].astype(str)
        + " | "
        + df["hospital_id"].astype(str)
        + " | "
        + df["version"].astype(str)
    )

    return df


# ==========================================================
# EXACT DEPLOYMENT LOOKUP
# ==========================================================

def get_exact_deployment(release_id, hospital_id, version):

    raw_df = pd.read_csv(DATA_PATH)

    release = raw_df[
        (raw_df["release_id"].astype(str) == str(release_id))
        & (raw_df["hospital_id"].astype(str) == str(hospital_id))
        & (raw_df["version"].astype(str) == str(version))
    ].copy()

    if release.empty:
        raise ValueError(
            f"Deployment not found: "
            f"{release_id} | {hospital_id} | {version}"
        )

    return release


# ==========================================================
# MONITORING OBSERVATION SIMULATOR
# ==========================================================

def deployment_scenario(release_key):
    """
    Give each deployment a deterministic monitoring scenario.

    The scenario changes telemetry only.
    The risk engine still decides SAFE/WARNING/HOLD/BLOCK.
    """

    value = int(
        hashlib.sha256(
            release_key.encode("utf-8")
        ).hexdigest()[:8],
        16
    )

    scenarios = [
        "RECOVERY",
        "STABLE",
        "DEGRADATION"
    ]

    return scenarios[value % len(scenarios)]


def simulate_monitoring_observation(
    release,
    release_key,
    stage
):
    """
    Create a new telemetry observation for the current rollout stage.

    This is explicitly a DEMO monitoring simulator.
    It never sets risk_decision directly.
    """

    observation = release.copy()

    scenario = deployment_scenario(release_key)

    # Base values from the selected deployment.
    cpu = float(observation.iloc[0]["cpu_usage"])
    memory = float(observation.iloc[0]["memory_usage"])
    error_rate = float(observation.iloc[0]["error_rate"])
    latency = float(observation.iloc[0]["latency_ms"])
    error_budget = float(
        observation.iloc[0]["error_budget_remaining"]
    )
    stable_error = float(
        observation.iloc[0]["stable_error_rate"]
    )
    canary_error = float(
        observation.iloc[0]["canary_error_rate"]
    )

    # ------------------------------------------------------
    # Monitoring evolution by scenario
    #
    # These are TELEMETRY values only.
    # evaluate_dataset() decides the final risk.
    # ------------------------------------------------------

    if scenario == "RECOVERY":

        if stage == 5:
            factor = 1.00
        elif stage == 25:
            factor = 0.92
        elif stage == 50:
            factor = 0.78
        else:
            factor = 0.65

        cpu *= factor
        memory *= factor
        error_rate *= factor
        latency *= factor
        stable_error *= factor
        canary_error *= factor
        error_budget = min(100.0, error_budget + (100 - error_budget) * (1 - factor))

    elif scenario == "STABLE":

        # Small observation noise, not a forced decision.
        offsets = {
            5: 1.00,
            25: 1.02,
            50: 0.98,
            100: 1.01
        }

        factor = offsets[stage]

        cpu *= factor
        memory *= factor
        error_rate *= factor
        latency *= factor
        stable_error *= factor
        canary_error *= factor

        error_budget = max(
            0.0,
            error_budget - stage * 0.03
        )

    else:
        # DEGRADATION
        factors = {
            5: 1.00,
            25: 1.10,
            50: 1.22,
            100: 1.35
        }

        factor = factors[stage]

        cpu *= factor
        memory *= factor
        error_rate *= factor
        latency *= factor
        stable_error *= factor
        canary_error *= factor

        error_budget = max(
            0.0,
            error_budget - stage * 0.18
        )

    observation["cpu_usage"] = min(100.0, cpu)
    observation["memory_usage"] = min(100.0, memory)
    observation["error_rate"] = max(0.0, error_rate)
    observation["latency_ms"] = max(0.0, latency)
    observation["error_budget_remaining"] = max(
        0.0,
        min(100.0, error_budget)
    )
    observation["stable_error_rate"] = max(
        0.0,
        stable_error
    )
    observation["canary_error_rate"] = max(
        0.0,
        canary_error
    )

    if "noisy_metric" in observation.columns:
        # Preserve the source monitoring-quality flag.
        observation["noisy_metric"] = observation["noisy_metric"]

    if "missing_metric" in observation.columns:
        observation["missing_metric"] = observation["missing_metric"]

    return observation


def recheck_release(
    release_id,
    hospital_id,
    version,
    stage=None,
    use_simulator=False
):
    """
    Re-check one exact deployment.

    If use_simulator=True, a new telemetry observation is generated.
    The final decision ALWAYS comes from the existing risk pipeline.
    """

    release = get_exact_deployment(
        release_id,
        hospital_id,
        version
    )

    if use_simulator:

        release_key = (
            f"{release_id} | "
            f"{hospital_id} | "
            f"{version}"
        )

        release = simulate_monitoring_observation(
            release,
            release_key,
            stage
        )

    validation = validate_dataset(release)

    if not validation["valid_columns"]:
        raise ValueError(
            f"Missing required columns: "
            f"{validation['missing_columns']}"
        )

    release = run_risk_pipeline(release)

    return release.iloc[0]


# ==========================================================
# STAGE VALIDATION DISPLAY
# ==========================================================

def show_stage_validation(row):

    st.subheader("🔍 Stage Validation")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "CPU",
            f"{float(row['cpu_usage']):.2f}%"
        )

    with col2:
        st.metric(
            "Memory",
            f"{float(row['memory_usage']):.2f}%"
        )

    with col3:
        st.metric(
            "Error Rate",
            f"{float(row['error_rate']):.2f}%"
        )

    with col4:
        st.metric(
            "Latency",
            f"{float(row['latency_ms']):.0f} ms"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Error Budget",
            f"{float(row['error_budget_remaining']):.2f}%"
        )

    with col2:
        st.metric(
            "Stable Error Rate",
            f"{float(row['stable_error_rate']):.2f}%"
        )

    with col3:
        st.metric(
            "Canary Error Rate",
            f"{float(row['canary_error_rate']):.2f}%"
        )

    st.write(
        f"**Canary Risk:** "
        f"`{row.get('canary_risk', 'N/A')}`"
    )

    missing = bool(
        row.get("missing_metric", False)
    )

    noisy = bool(
        row.get("noisy_metric", False)
    )

    if missing:
        st.warning(
            "⚠️ Missing monitoring observation detected."
        )
    else:
        st.success(
            "✅ Required monitoring observations available."
        )

    if noisy:
        st.warning(
            "⚠️ Noisy monitoring observation detected."
        )
    else:
        st.success(
            "✅ Monitoring observations are stable."
        )

    final_decision = str(
        row["risk_decision"]
    )

    st.write(
        f"### Final Stage Decision: `{final_decision}`"
    )

    return final_decision


# ==========================================================
# INITIALIZE DATA
# ==========================================================

try:
    df = load_evaluated_data()

except Exception as error:
    st.error(
        f"Application error: {error}"
    )
    st.stop()


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("📊 System Overview")

    st.metric(
        "Total Deployments",
        len(df)
    )

    st.metric(
        "Harmful Deployments",
        int(df["harmful"].sum())
    )

    st.divider()

    st.write("### Risk Distribution")

    risk_counts = (
        df["risk_decision"]
        .value_counts()
    )

    st.write(
        f"🟢 SAFE: "
        f"{risk_counts.get('SAFE', 0)}"
    )

    st.write(
        f"🟡 WARNING: "
        f"{risk_counts.get('WARNING', 0)}"
    )

    st.write(
        f"🟠 HOLD: "
        f"{risk_counts.get('HOLD', 0)}"
    )

    st.write(
        f"🔴 BLOCK: "
        f"{risk_counts.get('BLOCK', 0)}"
    )


# ==========================================================
# DEPLOYMENT SELECTION
# ==========================================================

st.header("🚀 Live Release Evaluation")

selected_key = st.selectbox(
    "Select deployment",
    df["release_key"].tolist()
)

selected = df[
    df["release_key"] == selected_key
].iloc[0]

selected_release = str(
    selected["release_id"]
)

selected_hospital = str(
    selected["hospital_id"]
)

selected_version = str(
    selected["version"]
)

base_decision = str(
    selected["risk_decision"]
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "active_release_key" not in st.session_state:

    st.session_state.active_release_key = selected_key
    st.session_state.rollout_stage = 0
    st.session_state.rollout_decision = base_decision
    st.session_state.rollout_history = []
    st.session_state.monitoring_observation = None


# ==========================================================
# RESET WHEN DEPLOYMENT CHANGES
# ==========================================================

if (
    st.session_state.active_release_key
    != selected_key
):

    st.session_state.active_release_key = selected_key
    st.session_state.rollout_stage = 0
    st.session_state.rollout_decision = base_decision
    st.session_state.rollout_history = []
    st.session_state.monitoring_observation = None


# ==========================================================
# INITIAL ROLLOUT STAGE
# ==========================================================

if st.session_state.rollout_stage == 0:

    if base_decision in ["SAFE", "HOLD"]:
        st.session_state.rollout_stage = 5
    else:
        st.session_state.rollout_stage = 0


current_stage = (
    st.session_state.rollout_stage
)

rollout_decision = (
    st.session_state.rollout_decision
)


# ==========================================================
# RELEASE INFORMATION
# ==========================================================

st.subheader(
    f"Deployment: {selected_key}"
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Release ID",
        selected_release
    )

with col2:
    st.metric(
        "Hospital",
        selected_hospital
    )

with col3:
    st.metric(
        "Version",
        selected_version
    )

with col4:
    st.metric(
        "Risk Score",
        selected["risk_score"]
    )


# ==========================================================
# CURRENT RISK DECISION
# ==========================================================

st.subheader("⚠️ Risk Decision")

if base_decision == "SAFE":

    st.success(
        "🟢 SAFE — Release can proceed."
    )

elif base_decision == "WARNING":

    st.warning(
        "🟡 WARNING — Manual review required."
    )

elif base_decision == "HOLD":

    st.warning(
        "🟠 HOLD — Rollout is paused for safety."
    )

elif base_decision == "BLOCK":

    st.error(
        "🔴 BLOCK — Release must not proceed."
    )


# ==========================================================
# CURRENT DATA HEALTH METRICS
# ==========================================================

st.subheader("📈 Health Metrics")

display_row = (
    st.session_state.monitoring_observation
    if st.session_state.get("monitoring_observation") is not None
    else selected
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "CPU",
        f"{float(display_row['cpu_usage']):.2f}%"
    )

with col2:
    st.metric(
        "Memory",
        f"{float(display_row['memory_usage']):.2f}%"
    )

with col3:
    st.metric(
        "Error Rate",
        f"{float(display_row['error_rate']):.2f}%"
    )

with col4:
    st.metric(
        "Latency",
        f"{float(display_row['latency_ms']):.0f} ms"
    )


# ==========================================================
# RELIABILITY + CANARY
# ==========================================================

st.subheader(
    "🛡️ Reliability & Canary Checks"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Error Budget",
        f"{float(display_row['error_budget_remaining']):.2f}%"
    )

with col2:
    st.metric(
        "Stable Error Rate",
        f"{float(display_row['stable_error_rate']):.2f}%"
    )

with col3:
    st.metric(
        "Canary Error Rate",
        f"{float(display_row['canary_error_rate']):.2f}%"
    )

st.write(
    f"**Canary Risk:** "
    f"`{display_row.get('canary_risk', 'N/A')}`"
)


# ==========================================================
# MONITORING QUALITY
# ==========================================================

st.subheader(
    "🔍 Monitoring Quality"
)

col1, col2 = st.columns(2)

with col1:

    if bool(
        display_row.get("missing_metric", False)
    ):
        st.warning(
            "⚠️ Missing monitoring metric detected."
        )
    else:
        st.success(
            "✅ Required monitoring observations available."
        )

with col2:

    if bool(
        display_row.get("noisy_metric", False)
    ):
        st.warning(
            "⚠️ Noisy monitoring observation detected."
        )
    else:
        st.success(
            "✅ Monitoring observations are stable."
        )


# ==========================================================
# PROGRESSIVE ROLLOUT
# ==========================================================

st.divider()

st.header(
    "📊 Progressive Rollout Monitor"
)

st.write(
    "**5% → 25% → 50% → 100%**"
)

st.progress(
    current_stage / 100
)

st.metric(
    "Current Rollout",
    f"{current_stage}%"
)


# ==========================================================
# BLOCKED
# ==========================================================

if rollout_decision == "BLOCK":

    st.error(
        "🛑 BLOCK — Rollout stopped."
    )

    st.caption(
        "No further rollout is permitted."
    )


# ==========================================================
# WARNING
# ==========================================================

elif rollout_decision == "WARNING":

    st.warning(
        "🟡 WARNING — Rollout requires manual review."
    )

    st.caption(
        "Resolve the warning before continuing."
    )


# ==========================================================
# HOLD
# ==========================================================

elif rollout_decision == "HOLD":

    st.warning(
        f"⏸️ HOLD — Rollout is paused at "
        f"{current_stage}%."
    )

    # ------------------------------------------------------
    # ONE-STAGE ROLLBACK
    # ------------------------------------------------------

    if current_stage > 5:

        current_index = ROLLOUT_STAGES.index(
            current_stage
        )

        previous_stage = ROLLOUT_STAGES[
            current_index - 1
        ]

        st.info(
            f"Safety rollback available: "
            f"**{current_stage}% → {previous_stage}%**"
        )

        if st.button(
            f"↩️ Rollback to {previous_stage}%",
            use_container_width=True
        ):

            st.session_state.rollout_stage = previous_stage
            st.session_state.rollout_decision = "HOLD"
            st.session_state.monitoring_observation = None

            st.session_state.rollout_history.append({
                "release_id": selected_release,
                "hospital_id": selected_hospital,
                "version": selected_version,
                "stage": current_stage,
                "decision": "HOLD",
                "action": f"ROLLBACK → {previous_stage}%"
            })

            st.success(
                f"↩️ Rollback completed. "
                f"Rollout returned to "
                f"{previous_stage}%."
            )

            st.rerun()

    else:

        st.info(
            "ℹ️ Rollout is already at the minimum "
            "5% stage. No rollback is possible."
        )

    # ------------------------------------------------------
    # NEW MONITORING OBSERVATION
    # ------------------------------------------------------

    st.info(
        "Get a new monitoring observation for this stage. "
        "The risk engine will determine the result."
    )

    if st.button(
        f"📡 Get New Monitoring Observation ({current_stage}%)",
        use_container_width=True
    ):

        with st.spinner(
            "Collecting new monitoring observation..."
        ):

            rechecked = recheck_release(
                selected_release,
                selected_hospital,
                selected_version,
                stage=current_stage,
                use_simulator=True
            )

        st.session_state.monitoring_observation = rechecked

        final_decision = show_stage_validation(
            rechecked
        )

        if final_decision == "SAFE":

            st.session_state.rollout_decision = "SAFE"

            st.session_state.rollout_history.append({
                "release_id": selected_release,
                "hospital_id": selected_hospital,
                "version": selected_version,
                "stage": current_stage,
                "decision": "SAFE",
                "action": "NEW OBSERVATION → SAFE"
            })

            st.success(
                "✅ New monitoring data passed the risk engine."
            )

            st.rerun()

        elif final_decision == "BLOCK":

            st.session_state.rollout_decision = "BLOCK"

            st.session_state.rollout_history.append({
                "release_id": selected_release,
                "hospital_id": selected_hospital,
                "version": selected_version,
                "stage": current_stage,
                "decision": "BLOCK",
                "action": "NEW OBSERVATION → STOP"
            })

            st.error(
                "🛑 New monitoring data triggered BLOCK."
            )

        else:

            st.session_state.rollout_decision = final_decision

            st.session_state.rollout_history.append({
                "release_id": selected_release,
                "hospital_id": selected_hospital,
                "version": selected_version,
                "stage": current_stage,
                "decision": final_decision,
                "action": "NEW OBSERVATION → PAUSE"
            })

            st.warning(
                f"⏸️ New monitoring data resulted in "
                f"{final_decision}. Rollout remains paused."
            )


# ==========================================================
# SAFE ROLLOUT
# ==========================================================

elif rollout_decision == "SAFE":

    st.success(
        "🚀 SAFE — Rollout is permitted."
    )

    # ------------------------------------------------------
    # 100% COMPLETE
    # ------------------------------------------------------

    if current_stage >= 100:

        st.success(
            "🎉 Rollout completed successfully at 100%."
        )

    # ------------------------------------------------------
    # NEXT STAGE
    # ------------------------------------------------------

    else:

        current_index = ROLLOUT_STAGES.index(
            current_stage
        )

        next_stage = ROLLOUT_STAGES[
            current_index + 1
        ]

        st.info(
            f"Next rollout stage: "
            f"**{next_stage}%**"
        )

        if st.button(
            f"🚀 Advance to {next_stage}%",
            use_container_width=True
        ):

            with st.spinner(
                "Collecting new monitoring observation..."
            ):

                rechecked = recheck_release(
                    selected_release,
                    selected_hospital,
                    selected_version,
                    stage=next_stage,
                    use_simulator=True
                )

            st.session_state.monitoring_observation = rechecked

            final_decision = show_stage_validation(
                rechecked
            )

            # ----------------------------------------------
            # SAFE → ADVANCE
            # ----------------------------------------------

            if final_decision == "SAFE":

                st.session_state.rollout_stage = next_stage
                st.session_state.rollout_decision = "SAFE"

                st.session_state.rollout_history.append({
                    "release_id": selected_release,
                    "hospital_id": selected_hospital,
                    "version": selected_version,
                    "stage": next_stage,
                    "decision": "SAFE",
                    "action": "CONTINUE"
                })

                st.success(
                    f"✅ New monitoring observation passed. "
                    f"Rollout advanced to {next_stage}%."
                )

                st.rerun()

            # ----------------------------------------------
            # BLOCK → STOP
            # ----------------------------------------------

            elif final_decision == "BLOCK":

                st.session_state.rollout_decision = "BLOCK"

                st.session_state.rollout_history.append({
                    "release_id": selected_release,
                    "hospital_id": selected_hospital,
                    "version": selected_version,
                    "stage": current_stage,
                    "decision": "BLOCK",
                    "action": "STOP"
                })

                st.error(
                    f"🛑 BLOCK detected. "
                    f"Rollout stopped at {current_stage}%."
                )

            # ----------------------------------------------
            # HOLD → PAUSE
            # ----------------------------------------------

            elif final_decision == "HOLD":

                st.session_state.rollout_decision = "HOLD"

                st.session_state.rollout_history.append({
                    "release_id": selected_release,
                    "hospital_id": selected_hospital,
                    "version": selected_version,
                    "stage": next_stage,
                    "decision": "HOLD",
                    "action": "HOLD"
                })

                st.warning(
                    f"⏸️ HOLD detected. "
                    f"Rollout paused at {next_stage}%."
                )

            # ----------------------------------------------
            # WARNING → PAUSE
            # ----------------------------------------------

            else:

                st.session_state.rollout_decision = "WARNING"

                st.session_state.rollout_history.append({
                    "release_id": selected_release,
                    "hospital_id": selected_hospital,
                    "version": selected_version,
                    "stage": current_stage,
                    "decision": "WARNING",
                    "action": "PAUSE"
                })

                st.warning(
                    "⚠️ WARNING detected. "
                    "Manual review required."
                )


# ==========================================================
# ROLLOUT HISTORY
# ==========================================================

if st.session_state.rollout_history:

    st.divider()

    st.subheader(
        "📜 Rollout History"
    )

    history_df = pd.DataFrame(
        st.session_state.rollout_history
    )

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )


# ==========================================================
# HIGHEST RISK DEPLOYMENTS
# ==========================================================

st.divider()

st.header(
    "📋 Highest Risk Deployments"
)

top_risk = (
    df.sort_values(
        "risk_score",
        ascending=False
    )
    .head(10)
)

display_columns = [
    "release_key",
    "release_id",
    "hospital_id",
    "version",
    "risk_score",
    "risk_decision",
    "canary_risk",
    "error_budget_remaining"
]

available_columns = [
    column
    for column in display_columns
    if column in top_risk.columns
]

st.dataframe(
    top_risk[available_columns],
    use_container_width=True,
    hide_index=True
)


# ==========================================================
# EVALUATION SUMMARY
# ==========================================================

st.divider()

st.header(
    "📊 Evaluation Summary"
)

total = len(df)

harmful = int(
    df["harmful"].sum()
)

harmful_blocked = len(
    df[
        (df["harmful"] == True)
        &
        (df["risk_decision"] == "BLOCK")
    ]
)

harmful_hold = len(
    df[
        (df["harmful"] == True)
        &
        (df["risk_decision"] == "HOLD")
    ]
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Deployments",
        total
    )

with col2:
    st.metric(
        "Harmful Deployments",
        harmful
    )

with col3:
    st.metric(
        "Harmful BLOCKED",
        harmful_blocked
    )

with col4:

    direct_block_rate = (
        harmful_blocked / harmful * 100
        if harmful > 0
        else 0
    )

    st.metric(
        "Direct BLOCK Rate",
        f"{direct_block_rate:.2f}%"
    )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "Prototype only — synthetic evaluation data. "
    "Monitoring observations are simulated for demonstration. "
    "Not a clinical decision-making system."
)
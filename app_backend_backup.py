import pandas as pd

from core.data_validator import validate_dataset
from core.noise_handler import clean_dataset
from core.error_budget import calculate_error_budget_risk
from core.canary import calculate_canary_risk
from core.fallback import apply_fallback
from core.risk_engine import evaluate_dataset


DATA_PATH = "data/releases_raw.csv"


def main():

    print("=" * 70)
    print("HEALTHCARE RELEASE RISK MONITOR")
    print("=" * 70)

    # --------------------------------------------------
    # STEP 1 — Load dataset
    # --------------------------------------------------

    print("\n[1/6] Loading deployment data...")

    df = pd.read_csv(DATA_PATH)

    print(f"Loaded {len(df)} release records")


    # --------------------------------------------------
    # STEP 2 — Validate dataset
    # --------------------------------------------------

    print("\n[2/6] Validating data...")

    validation = validate_dataset(df)

    if not validation["valid_columns"]:
        print("ERROR: Required columns are missing.")
        print(validation["missing_columns"])
        return

    print("Dataset structure: VALID")


    # --------------------------------------------------
    # STEP 3 — Missing + noisy observations
    # --------------------------------------------------

    print("\n[3/6] Checking monitoring quality...")

    df = clean_dataset(df)

    missing_count = int(df["missing_metric"].sum())
    noisy_count = int(df["noisy_metric"].sum())

    print(f"Rows with missing metrics: {missing_count}")
    print(f"Rows with noisy metrics: {noisy_count}")


    # --------------------------------------------------
    # STEP 4 — Error budget + Canary
    # --------------------------------------------------

    print("\n[4/6] Running progressive-delivery checks...")

    df = calculate_error_budget_risk(df)

    df = calculate_canary_risk(df)

    print("Error budget analysis: DONE")
    print("Canary comparison: DONE")


    # --------------------------------------------------
    # STEP 5 — Fallback behaviour
    # --------------------------------------------------

    print("\n[5/6] Applying fallback policy...")

    df = apply_fallback(df)

    hold_count = int(
        (df["fallback_action"] == "HOLD").sum()
    )

    print(f"Releases requiring HOLD: {hold_count}")


    # --------------------------------------------------
    # STEP 6 — Final risk engine
    # --------------------------------------------------

    print("\n[6/6] Calculating release risk...")

    df = evaluate_dataset(df)

    print("\n" + "=" * 70)
    print("FINAL RELEASE DECISIONS")
    print("=" * 70)

    print(
        df["risk_decision"].value_counts()
    )


    # --------------------------------------------------
    # Show highest-risk releases
    # --------------------------------------------------

    print("\nTOP 10 HIGHEST-RISK RELEASES")

    top_risk = df.sort_values(
        "risk_score",
        ascending=False
    ).head(10)

    print(
        top_risk[
            [
                "release_id",
                "hospital_id",
                "version",
                "risk_score",
                "risk_decision",
                "canary_risk",
                "error_budget_remaining"
            ]
        ].to_string(index=False)
    )


    # --------------------------------------------------
    # Save processed results
    # --------------------------------------------------

    output_path = "data/releases_evaluated.csv"

    df.to_csv(
        output_path,
        index=False
    )

    print("\nResults saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
import pandas as pd


FILE = "data/releases_evaluated.csv"


def main():
    df = pd.read_csv(FILE)

    total = len(df)
    harmful = int(df["harmful"].sum())

    print("=" * 60)
    print("HEALTHCARE RELEASE RISK MONITOR - EVALUATION")
    print("=" * 60)

    print(f"\nTotal releases/deployments : {total}")
    print(f"Harmful deployments        : {harmful}")
    print(f"Safe deployments           : {total - harmful}")

    print("\n--- Risk Decision Distribution ---")
    decision_counts = df["risk_decision"].value_counts()

    for decision in ["SAFE", "WARNING", "HOLD", "BLOCK"]:
        count = int(decision_counts.get(decision, 0))
        percentage = (count / total) * 100 if total else 0
        print(f"{decision:<10}: {count:4d} ({percentage:6.2f}%)")

    # Harmful deployment detection
    harmful_df = df[df["harmful"] == True]

    harmful_block = int(
        ((df["harmful"] == True) & (df["risk_decision"] == "BLOCK")).sum()
    )

    harmful_hold = int(
        ((df["harmful"] == True) & (df["risk_decision"] == "HOLD")).sum()
    )

    harmful_safe = int(
        ((df["harmful"] == True) & (df["risk_decision"] == "SAFE")).sum()
    )

    print("\n--- Harmful Deployment Detection ---")
    print(f"Harmful + BLOCK : {harmful_block}")
    print(f"Harmful + HOLD  : {harmful_hold}")
    print(f"Harmful + SAFE  : {harmful_safe}")

    if harmful:
        block_rate = (harmful_block / harmful) * 100
        prevention_rate = ((harmful_block + harmful_hold) / harmful) * 100
    else:
        block_rate = 0
        prevention_rate = 0

    print(f"\nDirect BLOCK rate       : {block_rate:.2f}%")
    print(f"BLOCK + HOLD prevention : {prevention_rate:.2f}%")

    # Confusion matrix for strict BLOCK detection
    tp = int(
        ((df["harmful"] == True) & (df["risk_decision"] == "BLOCK")).sum()
    )

    fp = int(
        ((df["harmful"] == False) & (df["risk_decision"] == "BLOCK")).sum()
    )

    tn = int(
        ((df["harmful"] == False) & (df["risk_decision"] != "BLOCK")).sum()
    )

    fn = int(
        ((df["harmful"] == True) & (df["risk_decision"] != "BLOCK")).sum()
    )

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    fpr = fp / (fp + tn) if (fp + tn) else 0

    print("\n--- Strict BLOCK Confusion Matrix ---")
    print(f"True Positive  (TP) : {tp}")
    print(f"False Positive (FP) : {fp}")
    print(f"True Negative  (TN) : {tn}")
    print(f"False Negative (FN) : {fn}")

    print("\n--- Detection Metrics ---")
    print(f"Precision : {precision * 100:.2f}%")
    print(f"Recall    : {recall * 100:.2f}%")
    print(f"FPR       : {fpr * 100:.2f}%")

    print("\n" + "=" * 60)
    print("Evaluation completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
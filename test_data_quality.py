import pandas as pd

from core.noise_handler import (
    clean_dataset,
    get_data_quality_summary
)


df = pd.read_csv("data/releases_raw.csv")

cleaned_df = clean_dataset(df)

summary = get_data_quality_summary(cleaned_df)


print("=" * 50)
print("DATA QUALITY REPORT")
print("=" * 50)

print("\nTotal rows:")
print(summary["total_rows"])

print("\nRows with missing metrics:")
print(summary["rows_with_missing_metrics"])

print("\nRows with noisy metrics:")
print(summary["rows_with_noisy_metrics"])

print("\nSample:")
print(
    cleaned_df[
        [
            "release_id",
            "hospital_id",
            "missing_metric",
            "noisy_metric"
        ]
    ].head(10)
)
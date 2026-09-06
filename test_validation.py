import pandas as pd

from core.data_validator import validate_dataset


df = pd.read_csv("data/releases_raw.csv")

results = validate_dataset(df)

print("=" * 50)
print("DATASET VALIDATION REPORT")
print("=" * 50)

print("\nColumns valid:")
print(results["valid_columns"])

print("\nMissing columns:")
print(results["missing_columns"])

print("\nRange problems:")
print(results["range_problems"])

print("\nMissing values:")
print(results["missing_values"])
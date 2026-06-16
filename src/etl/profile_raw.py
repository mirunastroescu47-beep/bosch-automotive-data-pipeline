from pathlib import Path

import pandas as pd

from src.config.settings import RAW_PATH


# Raw profiling layer.
# This step gives a quick overview of the ingested files before any cleaning is applied.
# It helps identify missing values, unexpected columns and potential data quality issues.

def profile_raw_data():
    parquet_files = list(Path(RAW_PATH).glob("*.parquet"))

    if not parquet_files:
        print("No parquet files found in the raw layer.")
        return

    for file_path in parquet_files:
        print("\n" + "=" * 80)
        print(f"Dataset: {file_path.name}")
        print("=" * 80)

        df = pd.read_parquet(file_path)

        print(f"Rows: {df.shape[0]}")
        print(f"Columns: {df.shape[1]}")

        print("\nColumn Names:")
        print(df.columns.tolist())

        print("\nData Types:")
        print(df.dtypes)

        print("\nTop Missing Values:")
        print(
            df.isna()
              .sum()
              .sort_values(ascending=False)
              .head(10)
        )

        print("\nDuplicate Rows:")

        # Some raw datasets may contain nested objects or array-like values.
        # In those cases, duplicate detection can fail because Pandas cannot hash the values.
        # The profiling step should not stop the pipeline because of that.

        try:
            duplicate_count = df.duplicated().sum()
            print(duplicate_count)

        except TypeError:
            print("Duplicate check skipped because the dataset contains unhashable values.")
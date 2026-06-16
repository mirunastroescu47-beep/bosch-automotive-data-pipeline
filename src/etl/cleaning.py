from pathlib import Path

import pandas as pd

from src.config.settings import RAW_PATH, PROCESSED_PATH
from src.modules.file_handler import save_processed


# Cleaning layer.
# This step applies generic cleaning rules and a few dataset-specific adjustments.
# The goal is not to create final analytical tables yet, but to standardize the data
# so it can be safely transformed in the curated layer.

def standardize_column_names(df):
    df = df.copy()

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )

    return df


def convert_unhashable_columns(df):
    # Some API responses may contain lists or dictionaries.
    # These values are converted to strings so operations like duplicate detection
    # can run without errors.

    df = df.copy()

    for column in df.columns:
        if df[column].apply(lambda value: isinstance(value, (list, dict, set))).any():
            df[column] = df[column].astype(str)

    return df


def clean_text_columns(df):
    df = df.copy()

    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].astype(str).str.strip()

        df[column] = df[column].replace(
            {
                "nan": None,
                "None": None,
                "": None
            }
        )

    return df


def clean_generic_dataset(df):
    # Generic cleaning applied to every source.
    # Source-specific transformations are handled separately below.

    df = df.copy()

    df = standardize_column_names(df)
    df = convert_unhashable_columns(df)
    df = clean_text_columns(df)
    df = df.drop_duplicates()

    return df


def clean_nhtsa(df):
    df = clean_generic_dataset(df)

    # NHTSA source has no headers, so the columns are initially numeric.
    # At this stage we keep the raw structure, but clean it enough for profiling
    # and future mapping to named columns.

    return df


def clean_doe(df):
    df = clean_generic_dataset(df)

    text_columns = [
        "station_name",
        "fuel_type_code",
        "city",
        "state",
        "status_code",
        "access_code"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].str.upper().str.strip()

    numeric_columns = [
        "latitude",
        "longitude"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


def clean_epa(df):
    df = clean_generic_dataset(df)

    text_columns = [
        "make",
        "model",
        "fueltype",
        "trany",
        "drive"
    ]

    for column in text_columns:
        if column in df.columns:
            df[column] = df[column].str.upper().str.strip()

    numeric_columns = [
        "year",
        "city08",
        "highway08",
        "comb08",
        "co2",
        "fuelcost08"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    if "comb08" in df.columns:
        df = df[
            (df["comb08"].isna()) |
            (df["comb08"] >= 0)
        ]

    return df


def run_cleaning():
    raw_files = list(Path(RAW_PATH).glob("*.parquet"))

    if not raw_files:
        print("No raw files found.")
        return

    for file_path in raw_files:
        print(f"Cleaning dataset: {file_path.name}")

        df = pd.read_parquet(file_path)

        if "nhtsa" in file_path.name:
            clean_df = clean_nhtsa(df)

        elif "doe" in file_path.name:
            clean_df = clean_doe(df)

        elif "epa" in file_path.name:
            clean_df = clean_epa(df)

        else:
            clean_df = clean_generic_dataset(df)

        output_name = file_path.name.replace(
            ".parquet",
            "_processed.parquet"
        )

        save_processed(
            df=clean_df,
            processed_path=PROCESSED_PATH,
            output_name=output_name
        )

        print(f"Saved processed dataset: {output_name}")
        print(f"Rows after cleaning: {len(clean_df)}")
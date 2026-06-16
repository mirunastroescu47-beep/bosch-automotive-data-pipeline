# File handling utilities.
# Keeping storage logic in one place makes it easier to change formats or paths later.

def save_raw(df, raw_path, output_name):
    # Raw datasets are stored as Parquet files.
    # This gives all sources a common format after ingestion, while still preserving
    # the source data before business cleaning or transformations.

    raw_path.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = raw_path / output_name

    df.to_parquet(
        output_file,
        index=False
    )


def save_processed(df, processed_path, output_name):
    # Processed datasets contain cleaned and standardized data.
    # They are also stored as Parquet to keep the pipeline consistent.

    processed_path.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = processed_path / output_name

    df.to_parquet(
        output_file,
        index=False
    )


def save_curated(df, curated_path, output_name):
    # Curated datasets are the final analytical outputs used for reporting.
    # These files are the main candidates for Power BI consumption.

    curated_path.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = curated_path / output_name

    df.to_parquet(
        output_file,
        index=False
    )
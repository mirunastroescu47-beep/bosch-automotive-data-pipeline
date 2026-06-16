from src.etl.ingest import run_ingestion
from src.etl.profile_raw import profile_raw_data
from src.etl.cleaning import run_cleaning


# Local script entry point.
# This is useful for running the pipeline directly from Python without Papermill.
# Papermill remains the preferred orchestration option for the final project delivery.

def main():
    print("=" * 80)
    print("STARTING AUTOMOTIVE DATA PIPELINE")
    print("=" * 80)

    print("\n[STEP 1] INGESTION")
    run_ingestion()

    print("\n[STEP 2] RAW DATA PROFILING")
    profile_raw_data()

    print("\n[STEP 3] CLEANING")
    run_cleaning()

    print("\nPIPELINE COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
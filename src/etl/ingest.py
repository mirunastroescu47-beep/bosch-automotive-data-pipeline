from src.config.settings import DATA_SOURCES, RAW_PATH
from src.modules.data_reader import read_source
from src.modules.file_handler import save_raw


# Ingestion layer.
# This stage reads all configured public sources and stores them in the raw layer.
# No business cleaning is applied here, because raw data should remain close to the original source.

def run_ingestion():
    print("Starting ingestion...")

    for dataset_name, source_config in DATA_SOURCES.items():
        print("=" * 80)
        print(f"Dataset key: {dataset_name}")

        # The reader is selected dynamically based on the source type.
        # This keeps ingestion generic even when sources have different formats.

        df = read_source(source_config)

        save_raw(
            df=df,
            raw_path=RAW_PATH,
            output_name=source_config["output_name"]
        )

        print(f"Saved raw dataset: {source_config['output_name']}")
        print(f"Rows loaded: {len(df)}")

    print("Ingestion completed.")
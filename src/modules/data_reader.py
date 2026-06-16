from io import BytesIO
from zipfile import ZipFile

import pandas as pd
import requests


# Main entry point used by the ingestion layer.
# The source configuration decides which reader is used, so the pipeline can handle
# CSV, TXT, ZIP and JSON API sources without changing the orchestration logic.

def read_source(source_config):
    source_type = source_config["type"]

    print_source_metadata(source_config)

    if source_type == "csv":
        return read_delimited_file(source_config)

    if source_type == "txt":
        return read_delimited_file(source_config)

    if source_type == "zip_txt":
        return read_zip_delimited_file(source_config)

    if source_type == "zip_csv":
        return read_zip_delimited_file(source_config)

    if source_type == "json_api":
        return read_json_api(source_config)

    if source_type == "xml":
        return read_xml(source_config)

    raise ValueError(f"Unsupported source type: {source_type}")


def print_source_metadata(source_config):
    # Printing metadata during ingestion makes it clear which public source is being used.
    # This is useful for debugging and also helps document data lineage.

    print(f"Source name: {source_config.get('source_name')}")
    print(f"Provider: {source_config.get('source_provider')}")
    print(f"Source file: {source_config.get('source_file')}")
    print(f"Source format: {source_config.get('source_format')}")
    print(f"Description: {source_config.get('description')}")
    print(f"URL: {source_config.get('url')}")


def get_header_value(source_config):
    # Some files include column headers, while others do not.
    # This is controlled from settings.py instead of being hardcoded here.

    has_header = source_config.get("has_header", True)

    if has_header:
        return 0

    return None


def get_delimiter(source_config):
    # The delimiter is also configurable because the sources do not use the same format.
    # For example, EPA uses comma-separated CSV, while NHTSA uses tab-separated TXT.

    return source_config.get("delimiter", ",")


def get_encoding(source_config):
    return source_config.get("encoding", "utf-8")


def read_delimited_file(source_config):
    # Generic reader for simple CSV or TXT files.
    # Header handling, separator and encoding are defined per source in the catalog.

    url = source_config["url"]
    delimiter = get_delimiter(source_config)
    header_value = get_header_value(source_config)
    encoding = get_encoding(source_config)

    return pd.read_csv(
        url,
        sep=delimiter,
        header=header_value,
        encoding=encoding,
        low_memory=False,
        on_bad_lines="skip"
    )


def read_zip_delimited_file(source_config):
    # Some public datasets are distributed as compressed ZIP archives.
    # The file is downloaded in memory and read directly, without creating temporary files.

    url = source_config["url"]
    delimiter = get_delimiter(source_config)
    header_value = get_header_value(source_config)
    encoding = get_encoding(source_config)
    inner_file = source_config.get("inner_file")

    response = requests.get(url, timeout=120)
    response.raise_for_status()

    zip_file = ZipFile(BytesIO(response.content))

    data_files = [
        file_name
        for file_name in zip_file.namelist()
        if file_name.lower().endswith((".txt", ".csv"))
    ]

    if not data_files:
        raise ValueError("No TXT/CSV file found inside ZIP.")

    selected_file = data_files[0]

    # If the expected inner file is configured, we select it explicitly.
    # This avoids accidentally reading documentation files from the archive.

    if inner_file:
        for file_name in data_files:
            if inner_file in file_name:
                selected_file = file_name
                break

    print(f"Selected file inside ZIP: {selected_file}")
    print(f"Delimiter used: {repr(delimiter)}")
    print(f"Header available: {source_config.get('has_header', True)}")

    with zip_file.open(selected_file) as file:
        return pd.read_csv(
            file,
            sep=delimiter,
            header=header_value,
            encoding=encoding,
            low_memory=False,
            on_bad_lines="skip"
        )


def read_json_api(source_config):
    # Generic reader for JSON APIs.
    # API responses are normalized into tabular data so they can be saved and processed
    # in the same way as CSV or TXT datasets.

    url = source_config["url"]
    record_path = source_config.get("json_record_path")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    data = response.json()

    if record_path:
        return pd.json_normalize(data[record_path])

    return pd.json_normalize(data)


def read_xml(source_config):
    # XML support is included to keep the ingestion framework extensible.
    # It is not currently used by the selected datasets, but it can support future sources.

    url = source_config["url"]

    return pd.read_xml(url)
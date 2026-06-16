from pathlib import Path

# ------------------------------------------------------------------
# Project Configuration
# ------------------------------------------------------------------
# This file contains all configurable elements used throughout the
# pipeline:
#
# - storage locations
# - notebook locations
# - local database configuration
# - public data source definitions
#
# Keeping configuration in a single place makes the project easier
# to maintain and avoids hardcoded values across the codebase.
# ------------------------------------------------------------------


BASE_DIR = Path(__file__).resolve().parents[2]


# ------------------------------------------------------------------
# Data Lake Structure
# ------------------------------------------------------------------
# Raw Layer
# Stores source data as received from external providers.
#
# Processed Layer
# Stores cleaned and standardized datasets.
#
# Curated Layer
# Stores business-ready datasets used for analytics and reporting.
# ------------------------------------------------------------------

RAW_PATH = BASE_DIR / "data_storage" / "raw"

PROCESSED_PATH = BASE_DIR / "data_storage" / "processed"

CURATED_PATH = BASE_DIR / "data_storage" / "curated"


# ------------------------------------------------------------------
# Notebook Configuration
# ------------------------------------------------------------------
# notebooks/
#     Contains source notebooks executed by Papermill.
#
# executed_notebooks/
#     Stores executed notebook outputs and execution logs.
# ------------------------------------------------------------------

NOTEBOOKS_PATH = BASE_DIR / "notebooks"

EXECUTED_NOTEBOOKS_PATH = BASE_DIR / "executed_notebooks"


# ------------------------------------------------------------------
# Export Configuration
# ------------------------------------------------------------------
# CSV exports are generated for reporting purposes and can be
# consumed directly by Power BI.
#
# SQL exports contain DDL scripts that simulate the loading phase
# into a relational database platform.
# ------------------------------------------------------------------

EXPORTS_PATH = BASE_DIR / "exports"

CSV_EXPORT_PATH = EXPORTS_PATH / "csv"

SQL_EXPORT_PATH = EXPORTS_PATH / "sql"


# ------------------------------------------------------------------
# Local Database Configuration
# ------------------------------------------------------------------
# SQLite is used as a lightweight local replacement for Azure SQL.
#
# This allows the project to demonstrate the loading phase without
# requiring cloud infrastructure.
#
# The Azure SQL implementation is provided separately as a
# documented reference in the export layer.
# ------------------------------------------------------------------

LOCAL_DATABASE_PATH = (
    BASE_DIR
    / "local_database"
    / "automotive_dw.db"
)


# ------------------------------------------------------------------
# Source Catalog
# ------------------------------------------------------------------
# Each entry describes:
#
# - source provider
# - source file or endpoint
# - original format
# - parsing rules
# - output dataset name
#
# The ingestion layer reads these definitions and dynamically
# selects the appropriate reader implementation.
#
# This approach allows new sources to be added with minimal code
# changes.
# ------------------------------------------------------------------

DATA_SOURCES = {

    # --------------------------------------------------------------
    # NHTSA Vehicle Complaints
    # --------------------------------------------------------------
    # Source Type:
    #     ZIP archive containing a TXT file
    #
    # Format Characteristics:
    #     - tab-separated values
    #     - no header row
    #     - one row per complaint
    #
    # Raw Conversion:
    #     TXT -> Parquet
    # --------------------------------------------------------------

    "nhtsa_vehicle_complaints": {

        "source_name":
            "NHTSA Vehicle Complaints",

        "source_provider":
            "National Highway Traffic Safety Administration",

        "source_file":
            "COMPLAINTS_RECEIVED_2020-2024.zip",

        "inner_file":
            "COMPLAINTS_RECEIVED_2020-2024.txt",

        "source_format":
            "TXT inside ZIP",

        "description":
            "Vehicle complaints received between 2020 and 2024.",

        "type":
            "zip_txt",

        "delimiter":
            "\t",

        "has_header":
            False,

        "encoding":
            "latin1",

        "url":
            "https://static.nhtsa.gov/odi/ffdd/cmpl/COMPLAINTS_RECEIVED_2020-2024.zip",

        "output_name":
            "nhtsa_vehicle_complaints.parquet"
    },


    # --------------------------------------------------------------
    # DOE Alternative Fuel Stations
    # --------------------------------------------------------------
    # Source Type:
    #     Public REST API
    #
    # Format Characteristics:
    #     - JSON response
    #     - one object per fuel station
    #
    # Raw Conversion:
    #     JSON -> Parquet
    # --------------------------------------------------------------

    "doe_alternative_fuel_stations": {

        "source_name":
            "DOE Alternative Fuel Stations",

        "source_provider":
            "U.S. Department of Energy - Alternative Fuel Data Center",

        "source_file":
            "Alternative Fuel Stations API",

        "source_format":
            "JSON API",

        "description":
            "Alternative fuel station information from the AFDC API.",

        "type":
            "json_api",

        "json_record_path":
            "fuel_stations",

        "url":
            "https://developer.nlr.gov/api/alt-fuel-stations/v1.json?api_key=DEMO_KEY&country=US&status=E",

        "output_name":
            "doe_alternative_fuel_stations.parquet"
    },


    # --------------------------------------------------------------
    # EPA Vehicle Fuel Economy
    # --------------------------------------------------------------
    # Source Type:
    #     CSV file
    #
    # Format Characteristics:
    #     - comma-separated values
    #     - header row available
    #     - one row per vehicle model
    #
    # Raw Conversion:
    #     CSV -> Parquet
    # --------------------------------------------------------------

    "epa_vehicle_fuel_economy": {

        "source_name":
            "EPA Vehicle Fuel Economy",

        "source_provider":
            "U.S. Environmental Protection Agency",

        "source_file":
            "vehicles.csv",

        "source_format":
            "CSV",

        "description":
            "Vehicle fuel economy and emissions information.",

        "type":
            "csv",

        "delimiter":
            ",",

        "has_header":
            True,

        "encoding":
            "utf-8",

        "url":
            "https://www.fueleconomy.gov/feg/epadata/vehicles.csv",

        "output_name":
            "epa_vehicle_fuel_economy.parquet"
    }
}
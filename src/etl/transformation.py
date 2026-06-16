import pandas as pd

from src.config.settings import PROCESSED_PATH, CURATED_PATH
from src.modules.file_handler import save_curated


# Transformation layer.
# This step builds a small star schema from the cleaned datasets.
# The curated layer is designed as a local analytical model that can be loaded
# into SQLite and later consumed by Power BI.


def read_processed_file(file_name):
    return pd.read_parquet(PROCESSED_PATH / file_name)


def clean_key_columns(df, columns):
    # Standardize join keys before building dimensions and facts.
    # This improves matching between datasets that come from different public sources.

    df = df.copy()

    for column in columns:
        if column in df.columns:
            df[column] = df[column].astype(str).str.upper().str.strip()
            df[column] = df[column].replace(
                {
                    "NAN": None,
                    "NONE": None,
                    "": None
                }
            )

    return df


def prepare_nhtsa_complaints():
    df = read_processed_file("nhtsa_vehicle_complaints_processed.parquet")

    # NHTSA complaints file has no headers in the original TXT file.
    # Column positions are mapped based on the raw file structure inspected during exploration.
    # The selected fields are the ones needed for the dimensional model.

    complaints = df.rename(
        columns={
            "0": "record_id",
            "1": "complaint_id",
            "2": "manufacturer",
            "3": "make",
            "4": "model",
            "5": "model_year",
            "6": "crash_flag",
            "7": "failure_date",
            "8": "fire_flag",
            "9": "injuries",
            "10": "deaths",
            "11": "component",
            "12": "city",
            "13": "state",
            "14": "vin",
            "15": "date_received",
            "17": "mileage",
            "19": "complaint_description"
        }
    )

    selected_columns = [
        "complaint_id",
        "make",
        "model",
        "model_year",
        "component",
        "city",
        "state",
        "injuries",
        "deaths"
    ]

    complaints = complaints[
        [column for column in selected_columns if column in complaints.columns]
    ].copy()

    complaints = clean_key_columns(
        complaints,
        ["make", "model", "component", "city", "state"]
    )

    complaints["model_year"] = pd.to_numeric(
        complaints["model_year"],
        errors="coerce"
    )

    complaints["injuries"] = pd.to_numeric(
        complaints["injuries"],
        errors="coerce"
    ).fillna(0)

    complaints["deaths"] = pd.to_numeric(
        complaints["deaths"],
        errors="coerce"
    ).fillna(0)

    return complaints


def prepare_epa_fuel_economy():
    df = read_processed_file("epa_vehicle_fuel_economy_processed.parquet")

    selected_columns = [
        "make",
        "model",
        "year",
        "fueltype",
        "city08",
        "highway08",
        "comb08",
        "co2",
        "fuelcost08"
    ]

    fuel = df[
        [column for column in selected_columns if column in df.columns]
    ].copy()

    fuel = fuel.rename(
        columns={
            "year": "model_year",
            "fueltype": "fuel_type"
        }
    )

    fuel = clean_key_columns(
        fuel,
        ["make", "model", "fuel_type"]
    )

    numeric_columns = [
        "model_year",
        "city08",
        "highway08",
        "comb08",
        "co2",
        "fuelcost08"
    ]

    for column in numeric_columns:
        if column in fuel.columns:
            fuel[column] = pd.to_numeric(
                fuel[column],
                errors="coerce"
            )

    return fuel


def prepare_doe_fuel_stations():
    df = read_processed_file("doe_alternative_fuel_stations_processed.parquet")

    selected_columns = [
        "station_name",
        "fuel_type_code",
        "city",
        "state",
        "status_code",
        "latitude",
        "longitude"
    ]

    stations = df[
        [column for column in selected_columns if column in df.columns]
    ].copy()

    stations = stations.rename(
        columns={
            "fuel_type_code": "fuel_type"
        }
    )

    stations = clean_key_columns(
        stations,
        ["station_name", "fuel_type", "city", "state", "status_code"]
    )

    numeric_columns = [
        "latitude",
        "longitude"
    ]

    for column in numeric_columns:
        if column in stations.columns:
            stations[column] = pd.to_numeric(
                stations[column],
                errors="coerce"
            )

    return stations


def build_dim_vehicle(complaints, fuel):
    # Vehicle dimension is shared by NHTSA complaints and EPA fuel economy data.
    # The common business key is make, model and model year.

    complaints_vehicles = complaints[
        ["make", "model", "model_year"]
    ].copy()

    fuel_vehicles = fuel[
        ["make", "model", "model_year"]
    ].copy()

    dim_vehicle = pd.concat(
        [complaints_vehicles, fuel_vehicles],
        ignore_index=True
    )

    dim_vehicle = dim_vehicle.drop_duplicates()
    dim_vehicle = dim_vehicle.dropna(
        subset=["make", "model", "model_year"]
    )

    dim_vehicle = dim_vehicle.sort_values(
        ["make", "model", "model_year"]
    ).reset_index(drop=True)

    dim_vehicle.insert(
        0,
        "vehicle_key",
        range(1, len(dim_vehicle) + 1)
    )

    return dim_vehicle


def build_dim_location(complaints, stations):
    # Location dimension is shared by NHTSA complaints and DOE fuel stations.
    # For complaints, city may sometimes be missing, but state is still useful for reporting.

    complaints_locations = complaints[
        ["state", "city"]
    ].copy()

    station_locations = stations[
        ["state", "city"]
    ].copy()

    dim_location = pd.concat(
        [complaints_locations, station_locations],
        ignore_index=True
    )

    dim_location = dim_location.drop_duplicates()
    dim_location = dim_location.dropna(
        subset=["state"]
    )

    dim_location = dim_location.sort_values(
        ["state", "city"]
    ).reset_index(drop=True)

    dim_location.insert(
        0,
        "location_key",
        range(1, len(dim_location) + 1)
    )

    return dim_location


def build_dim_fuel_type(fuel, stations):
    # Fuel type dimension combines values from EPA and DOE.
    # This enables reporting across both vehicle efficiency and fuel infrastructure.

    epa_fuels = fuel[
        ["fuel_type"]
    ].copy()

    doe_fuels = stations[
        ["fuel_type"]
    ].copy()

    dim_fuel_type = pd.concat(
        [epa_fuels, doe_fuels],
        ignore_index=True
    )

    dim_fuel_type = dim_fuel_type.drop_duplicates()
    dim_fuel_type = dim_fuel_type.dropna(
        subset=["fuel_type"]
    )

    dim_fuel_type = dim_fuel_type.sort_values(
        ["fuel_type"]
    ).reset_index(drop=True)

    dim_fuel_type.insert(
        0,
        "fuel_type_key",
        range(1, len(dim_fuel_type) + 1)
    )

    return dim_fuel_type


def build_fact_complaints(complaints, dim_vehicle, dim_location):
    # Complaint facts describe reliability and safety signals reported by consumers.
    # Component is kept as a descriptive attribute directly in the fact table.

    fact = complaints.merge(
        dim_vehicle,
        on=["make", "model", "model_year"],
        how="left"
    )

    fact = fact.merge(
        dim_location,
        on=["state", "city"],
        how="left"
    )

    fact = (
        fact
        .groupby(
            ["vehicle_key", "location_key", "component"],
            dropna=False
        )
        .agg(
            complaint_count=("complaint_id", "count"),
            total_injuries=("injuries", "sum"),
            total_deaths=("deaths", "sum")
        )
        .reset_index()
    )

    fact.insert(
        0,
        "complaint_fact_key",
        range(1, len(fact) + 1)
    )

    return fact


def build_fact_fuel_economy(fuel, dim_vehicle, dim_fuel_type):
    # Fuel economy facts contain average efficiency and emissions indicators
    # by vehicle and fuel type.

    fact = fuel.merge(
        dim_vehicle,
        on=["make", "model", "model_year"],
        how="left"
    )

    fact = fact.merge(
        dim_fuel_type,
        on=["fuel_type"],
        how="left"
    )

    fact = (
        fact
        .groupby(
            ["vehicle_key", "fuel_type_key"],
            dropna=False
        )
        .agg(
            avg_city_mpg=("city08", "mean"),
            avg_highway_mpg=("highway08", "mean"),
            avg_combined_mpg=("comb08", "mean"),
            avg_co2_emissions=("co2", "mean"),
            avg_fuel_cost=("fuelcost08", "mean")
        )
        .reset_index()
    )

    fact.insert(
        0,
        "fuel_economy_fact_key",
        range(1, len(fact) + 1)
    )

    return fact


def build_fact_fuel_stations(stations, dim_location, dim_fuel_type):
    # Fuel station facts summarize alternative fuel infrastructure
    # by location and fuel type.

    fact = stations.merge(
        dim_location,
        on=["state", "city"],
        how="left"
    )

    fact = fact.merge(
        dim_fuel_type,
        on=["fuel_type"],
        how="left"
    )

    fact = (
        fact
        .groupby(
            ["location_key", "fuel_type_key", "status_code"],
            dropna=False
        )
        .agg(
            station_count=("station_name", "count"),
            avg_latitude=("latitude", "mean"),
            avg_longitude=("longitude", "mean")
        )
        .reset_index()
    )

    fact.insert(
        0,
        "fuel_station_fact_key",
        range(1, len(fact) + 1)
    )

    return fact


def run_transformation():
    print("Starting star schema transformation...")

    complaints = prepare_nhtsa_complaints()
    fuel = prepare_epa_fuel_economy()
    stations = prepare_doe_fuel_stations()

    dim_vehicle = build_dim_vehicle(
        complaints,
        fuel
    )

    dim_location = build_dim_location(
        complaints,
        stations
    )

    dim_fuel_type = build_dim_fuel_type(
        fuel,
        stations
    )

    fact_complaints = build_fact_complaints(
        complaints,
        dim_vehicle,
        dim_location
    )

    fact_fuel_economy = build_fact_fuel_economy(
        fuel,
        dim_vehicle,
        dim_fuel_type
    )

    fact_fuel_stations = build_fact_fuel_stations(
        stations,
        dim_location,
        dim_fuel_type
    )

    save_curated(
        df=dim_vehicle,
        curated_path=CURATED_PATH,
        output_name="dim_vehicle.parquet"
    )

    save_curated(
        df=dim_location,
        curated_path=CURATED_PATH,
        output_name="dim_location.parquet"
    )

    save_curated(
        df=dim_fuel_type,
        curated_path=CURATED_PATH,
        output_name="dim_fuel_type.parquet"
    )

    save_curated(
        df=fact_complaints,
        curated_path=CURATED_PATH,
        output_name="fact_complaints.parquet"
    )

    save_curated(
        df=fact_fuel_economy,
        curated_path=CURATED_PATH,
        output_name="fact_fuel_economy.parquet"
    )

    save_curated(
        df=fact_fuel_stations,
        curated_path=CURATED_PATH,
        output_name="fact_fuel_stations.parquet"
    )

    print("Star schema transformation completed.")
    print("Curated dimension and fact tables created successfully.")
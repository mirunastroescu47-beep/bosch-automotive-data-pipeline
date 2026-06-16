# Automotive Data Pipeline

## Overview

This project implements an end-to-end ETL pipeline that acquires, processes, transforms and loads automotive data from multiple public sources.

The solution integrates vehicle safety, fuel economy and alternative fuel infrastructure datasets and prepares them for analytical reporting using Power BI.

---

## Data Sources

### NHTSA – Vehicle Complaints

* Dataset: COMPLAINTS_RECEIVED_2020-2024.zip
* Format: ZIP → TXT (tab-separated, no header)
* Description: Vehicle safety complaints, affected components, injuries and fatalities.

### DOE – Alternative Fuel Stations

* Dataset: Alternative Fuel Stations API
* Format: JSON API
* Description: Alternative fuel station locations, fuel types and operational status.

### EPA – Vehicle Fuel Economy

* Dataset: vehicles.csv
* Format: CSV (comma-separated, with header)
* Description: Fuel economy metrics, emissions and fuel costs.

---

## Solution Architecture

The pipeline follows a layered ETL architecture:

Sources → Raw Layer → Processed Layer → Curated Layer → SQLite → Power BI

Main technologies:

* Python
* Pandas
* Parquet
* Papermill
* SQLite
* Power BI

---


## Pipeline Stages

### 1. Ingestion

* Downloads data from public sources
* Converts datasets into Pandas DataFrames
* Stores raw data as Parquet files

### 2. Profiling

* Analyzes dataset structure
* Detects missing values and duplicates
* Generates basic statistics

### 3. Cleaning

* Removes duplicate records
* Standardizes data types
* Handles missing values

### 4. Transformation

* Creates analytical dimension tables:

  * dim_vehicle
  * dim_location
  * dim_fuel_type

* Creates analytical fact tables:

  * fact_complaints
  * fact_fuel_economy
  * fact_fuel_stations

### 5. Export

* Loads curated data into SQLite
* Generates CSV exports
* Generates SQL DDL scripts

---

## Running the Pipeline

Activate the virtual environment and run:

```bash
python -m src.papermill_orchestrator
```

This command executes all pipeline stages sequentially using Papermill.

---

## Output

### Raw Layer

```text
data_storage/raw/
```

### Processed Layer

```text
data_storage/processed/
```

### Curated Layer

```text
data_storage/curated/
```

### SQLite Database

```text
local_database/automotive_dw.db
```

### Power BI Files

```text
exports/csv/
```

---

## Automation Strategy

The pipeline is orchestrated using Papermill.

Each ETL stage is implemented as an individual notebook and executed sequentially through a central orchestrator.

Recommended refresh schedule: Weekly.

---

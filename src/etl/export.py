from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src.config.settings import (
    CURATED_PATH,
    CSV_EXPORT_PATH,
    SQL_EXPORT_PATH,
    LOCAL_DATABASE_PATH
)


# Export and load simulation layer.
# This step simulates the final loading phase of the pipeline.
# SQLite is used locally as a lightweight replacement for Azure SQL Database.
# The same curated datasets are also exported as CSV files for Power BI reporting.


def get_curated_files():
    return list(Path(CURATED_PATH).glob("*.parquet"))


def create_sqlite_engine():
    # SQLite is used here only as a local simulation.
    # In a production environment, this connection would be replaced
    # by an Azure SQL Database connection string.

    LOCAL_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection_string = f"sqlite:///{LOCAL_DATABASE_PATH}"

    return create_engine(connection_string)


def export_to_csv(df, table_name):
    # CSV exports are useful for Power BI because they are easy to inspect
    # and can be loaded without requiring a database connection.

    CSV_EXPORT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = CSV_EXPORT_PATH / f"{table_name}.csv"

    df.to_csv(
        output_file,
        index=False
    )

    print(f"CSV exported: {output_file}")


def load_to_sqlite(df, table_name, engine):
    # This simulates the loading step into a relational database.
    # The table is replaced on each run to keep the pipeline idempotent.

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False
    )

    print(f"Loaded into SQLite table: {table_name}")


def map_pandas_type_to_sql(dtype):
    dtype_text = str(dtype).lower()

    if "int" in dtype_text:
        return "INT"

    if "float" in dtype_text:
        return "FLOAT"

    if "datetime" in dtype_text:
        return "DATETIME"

    if "bool" in dtype_text:
        return "BIT"

    return "VARCHAR(255)"


def generate_create_table_sql(df, table_name):
    # The generated DDL shows how the curated datasets could be created
    # in a SQL database. It is saved as a reference artifact for the project.

    columns_sql = []

    for column_name, dtype in df.dtypes.items():
        sql_type = map_pandas_type_to_sql(dtype)

        safe_column_name = str(column_name).replace(" ", "_")

        columns_sql.append(
            f"    {safe_column_name} {sql_type}"
        )

    columns_block = ",\n".join(columns_sql)

    sql_script = f"""CREATE TABLE {table_name} (
{columns_block}
);
"""

    return sql_script


def save_sql_script(sql_script, table_name):
    SQL_EXPORT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = SQL_EXPORT_PATH / f"{table_name}.sql"

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(sql_script)

    print(f"SQL script generated: {output_file}")


def export_azure_sql_reference():
    # This section is intentionally saved as a commented reference.
    # It shows how the same loading logic could be adapted for Azure SQL Database
    # without requiring an Azure subscription for this project.

    SQL_EXPORT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    reference_file = SQL_EXPORT_PATH / "azure_sql_reference.py"

    reference_code = '''
# Azure SQL Database loading reference
# This code is not executed in the local project.
# It documents how the local SQLite load could be replaced by Azure SQL.

# from sqlalchemy import create_engine
#
# azure_connection_string = (
#     "mssql+pyodbc://<username>:<password>@<server>.database.windows.net:1433/"
#     "<database>?driver=ODBC+Driver+18+for+SQL+Server"
# )
#
# azure_engine = create_engine(azure_connection_string)
#
# df.to_sql(
#     table_name,
#     azure_engine,
#     if_exists="replace",
#     index=False
# )
'''
    with open(reference_file, "w", encoding="utf-8") as file:
        file.write(reference_code)

    print(f"Azure SQL reference generated: {reference_file}")


def run_export():
    print("Starting export and load simulation...")

    curated_files = get_curated_files()

    if not curated_files:
        print("No curated files found.")
        return

    engine = create_sqlite_engine()

    for file_path in curated_files:
        table_name = file_path.stem

        print("=" * 80)
        print(f"Processing curated dataset: {file_path.name}")

        df = pd.read_parquet(file_path)

        export_to_csv(
            df=df,
            table_name=table_name
        )

        load_to_sqlite(
            df=df,
            table_name=table_name,
            engine=engine
        )

        sql_script = generate_create_table_sql(
            df=df,
            table_name=table_name
        )

        save_sql_script(
            sql_script=sql_script,
            table_name=table_name
        )

    export_azure_sql_reference()

    print("Export and load simulation completed.")

# if __name__ == "__main__":
#     run_export()

# ------------------------------------------------------------------------------
# Azure SQL Database Integration (Reference Only)
#
# SQLite is used as the active local implementation for this project.
#
# In a production environment, the same curated dimension and fact tables
# could be loaded into Azure SQL Database by replacing the SQLite SQLAlchemy
# engine with an Azure SQL connection engine.
#
# Example:
#
# from sqlalchemy import create_engine
#
# azure_connection_string = (
#     "mssql+pyodbc://<username>:<password>"
#     "@<server>.database.windows.net:1433/<database>"
#     "?driver=ODBC+Driver+18+for+SQL+Server"
# )
#
# azure_engine = create_engine(azure_connection_string)
#
# df.to_sql(
#     table_name,
#     azure_engine,
#     if_exists="replace",
#     index=False
# )
#
# This logic is intentionally kept as documentation only because the project
# requirements specify a simulation rather than an actual Azure deployment.

import papermill as pm

from src.config.settings import NOTEBOOKS_PATH, EXECUTED_NOTEBOOKS_PATH


# Papermill orchestration.
# Each notebook represents one pipeline stage, while the reusable ETL logic
# remains in the src/ package. This keeps notebooks lightweight and easy to audit.

PIPELINE_NOTEBOOKS = [
    "01_ingestion.ipynb",
    "02_profiling.ipynb",
    "03_cleaning.ipynb",
    "04_transformation.ipynb",
    "05_export.ipynb"
]


def run_notebook(notebook_name):
    input_path = NOTEBOOKS_PATH / notebook_name
    output_path = EXECUTED_NOTEBOOKS_PATH / notebook_name

    EXECUTED_NOTEBOOKS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    print("=" * 80)
    print(f"Running notebook: {notebook_name}")

    pm.execute_notebook(
        input_path=str(input_path),
        output_path=str(output_path),
        kernel_name="python3"
    )

    print(f"Finished notebook: {notebook_name}")


def run_pipeline():
    for notebook_name in PIPELINE_NOTEBOOKS:
        run_notebook(notebook_name)


if __name__ == "__main__":
    run_pipeline()

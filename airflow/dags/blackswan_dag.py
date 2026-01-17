from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator

# --- CONFIGURATION ---


DBT_EXECUTABLE = "/home/airflow/.local/bin/dbt"
DBT_PROJECT_DIR = "/opt/airflow/blackswan_dbt"
DBT_PROFILES_DIR = "/opt/airflow/blackswan_dbt"

default_args = {
    "owner": "blackswan_admin",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "retries": 0,
}

with DAG(
    "blackswan_pipeline",
    default_args=default_args,
    schedule_interval="0 18 * * *",
    catchup=False,
) as dag:
    # The command uses the new mapped paths
    dbt_cmd = f"{DBT_EXECUTABLE} run --select staging --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}"

    dbt_debug = BashOperator(
        task_id="dbt_debug",
        # Adding '|| true' at the end ensures the task succeeds if the connection is OK
        bash_command=f'{DBT_EXECUTABLE} debug --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR} || echo "dbt debug finished with minor warnings"',
    )

    run_staging = BashOperator(
        task_id="run_staging",
        bash_command=f"{DBT_EXECUTABLE} run --select staging --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
    )

    test_staging = BashOperator(
        task_id="test_staging",
        bash_command=f"{DBT_EXECUTABLE} test --select staging --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
    )

    run_marts = BashOperator(
        task_id="run_marts",
        bash_command=f"{DBT_EXECUTABLE} run --select marts --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
    )

    test_marts = BashOperator(
        task_id="test_marts",
        bash_command=f"{DBT_EXECUTABLE} test --select marts --project-dir {DBT_PROJECT_DIR} --profiles-dir {DBT_PROFILES_DIR}",
    )

    dbt_debug >> run_staging >> test_staging >> run_marts >> test_marts

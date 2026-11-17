from airflow.sdk import DAG, Param
from airflow.providers.standard.operators.bash import BashOperator

with DAG(
    dag_id="olist_backfill",
    schedule=None,
    max_active_runs=1,
    is_paused_upon_creation=True,
    params={
        "month": Param("2018-01", type="string", pattern=r"^\d{4}-(0[1-9]|1[0-2])$")
    },
) as dag:
    BashOperator(
        task_id="backfill_month",
        bash_command='python run.py "$OLIST_MONTH"',
        env={"OLIST_MONTH": "{{ params.month }}"},
        append_env=True,
        cwd="/app",
    )
from datetime import timedelta
from pathlib import Path

from airflow.sdk import DAG, Param, get_current_context, task
from airflow.sdk.exceptions import AirflowSkipException
from airflow.providers.standard.operators.bash import BashOperator
from pendulum import datetime

MONTH_PATTERN = r"^[0-9]{4}-(0[1-9]|1[0-2])$"
COMPLETED_DIR = Path("/app/data/.scheduled_backfills")

with DAG(
    dag_id="olist_backfill",
    schedule="*/5 * * * *",
    start_date=datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    max_active_runs=1,
    is_paused_upon_creation=True,
    params={
        "month": Param("2018-01", type="string", pattern=MONTH_PATTERN),
        "scheduled_months": Param(
            ["2018-01", "2018-02", "2018-03"],
            type="array",
            items={"type": "string", "pattern": MONTH_PATTERN},
            uniqueItems=True,
        ),
    },
) as dag:

    @task
    def select_month():
        context = get_current_context()
        if context["dag_run"].run_type != "scheduled":
            return context["params"]["month"]

        for month in context["params"]["scheduled_months"]:
            if not (COMPLETED_DIR / month).exists():
                return month

        raise AirflowSkipException("All scheduled purchase months are complete.")

    BashOperator(
        task_id="backfill_month",
        bash_command="""
            set -e
            echo "Processing purchase month $OLIST_MONTH"
            python run.py "$OLIST_MONTH"
            if [ "$OLIST_RUN_TYPE" = scheduled ]; then
                mkdir -p "$OLIST_COMPLETED_DIR"
                touch "$OLIST_COMPLETED_DIR/$OLIST_MONTH"
            fi
        """,
        env={
            "OLIST_MONTH": select_month(),
            "OLIST_RUN_TYPE": "{{ dag_run.run_type.value }}",
            "OLIST_COMPLETED_DIR": str(COMPLETED_DIR),
        },
        append_env=True,
        cwd="/app",
        retries=1,
        retry_delay=timedelta(seconds=30),
    )
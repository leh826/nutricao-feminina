from __future__ import annotations

import pendulum

try:
    from airflow.sdk import DAG
except ImportError:
    from airflow import DAG

from airflow.providers.standard.operators.bash import BashOperator


DBT_PROJECT_DIR = "/opt/airflow/dbt_projeto"


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": pendulum.duration(minutes=2),
}


with DAG(
    dag_id="nutricao_feminina_medalhao",
    description="Pipeline Bronze, Silver e Gold para recomendacoes nutricionais por fase do ciclo menstrual.",
    default_args=default_args,
    start_date=pendulum.datetime(2026, 6, 1, tz="America/Sao_Paulo"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["nutricao", "medalhao", "dbt", "minio"],
) as dag:
    extract_bronze = BashOperator(
        task_id="extract_edamam_to_bronze",
        bash_command="python /opt/airflow/src/apify_extract.py",
    )

    process_silver = BashOperator(
        task_id="process_bronze_to_silver",
        bash_command="python /opt/airflow/src/apify_silver.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run_silver_to_gold",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run --profiles-dir .",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt test --profiles-dir .",
    )

    export_gold = BashOperator(
        task_id="export_gold_to_minio",
        bash_command=f"cd {DBT_PROJECT_DIR} && dbt run-operation export_gold_recomendacoes --profiles-dir .",
    )

    extract_bronze >> process_silver >> dbt_run >> dbt_test >> export_gold

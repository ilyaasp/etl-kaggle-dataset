from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

def_args = {
    'owner': 'ilyas',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'vehicle_data_etl_DAG',
    default_args=def_args,
    description='ETL of events table',
    schedule_interval=timedelta(days=1),
)

run_etl_task = BashOperator(
    task_id='run_events_etl',
    bash_command="cd /opt/airflow/etl/vehicle_data && python3 main.py",
    dag=dag,
)

run_etl_task
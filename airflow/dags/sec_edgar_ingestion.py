from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingest import download_sec_filing
from vectorize import process_and_vectorize

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

# Define the DAG
with DAG(
    'sec_edgar_ingestion',
    default_args=default_args,
    description="Download and Vectorize Apple SEC 10-K Filings",
    schedule_interval=timedelta(days=7),
    catchup=False
) as dag:
    # Ingest
    task_ingest = PythonOperator(
        task_id='download_sec_filings',
        python_callable=download_sec_filing
    )

    # Parse and Vectorize
    task_vectorize = PythonOperator(
        task_id='download_sec_vectorize',
        python_callable=process_and_vectorize
    )

    task_ingest >> task_vectorize

from airflow import DAG
from airflow.models.param import Param
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime, timedelta
from ingest import download_filings
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
    description="Download and Vectorize SEC 10-K Filings",
    schedule=timedelta(days=7),
    catchup=False,
    # Param ticker
    params={
        "ticker": Param("AAPL", type="string", description="The stock ticker to download (e.g. AAPL, TSLA, MSFT)")
        }
) as dag:
    # Ingest
    task_ingest = PythonOperator(
        task_id='download_sec_filings',
        python_callable=download_filings,
        op_kwargs={'ticker': "{{ params.ticker }}"}
    )

    # Parse and Vectorize
    task_vectorize = PythonOperator(
        task_id='download_sec_vectorize',
        python_callable=process_and_vectorize
    )

    task_ingest >> task_vectorize

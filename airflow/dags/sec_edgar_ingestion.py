from datetime import UTC, datetime, timedelta

from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import Param
from src.evaluation.evaluate_task import evaluate_pipeline
from src.pipeline.ingest import download_filings
from src.pipeline.vectorize import process_and_vectorize
from src.rag.generate_ground_truth import generate_dynamic_dataset

default_args = {
    'owner': 'data_engineer',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1, tzinfo=UTC),
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
    is_paused_upon_creation=False,
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
        python_callable=process_and_vectorize,
            op_kwargs={"ticker": "{{ params.ticker }}"}
    )

    task_evaluate = PythonOperator(
        task_id='run_continuous_evaluation',
        python_callable=evaluate_pipeline,
        op_kwargs={'ticker': "{{ params.ticker }}"}
    )

    task_generate_ground_truth = PythonOperator(
        task_id='generate_dynamic_dataset',
        python_callable=generate_dynamic_dataset,
        op_kwargs={'ticker': "{{ params.ticker }}"}
    )

    task_ingest >> task_vectorize >> task_generate_ground_truth >> task_evaluate

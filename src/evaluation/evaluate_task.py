import psycopg2

from src.evaluation.evaluate import run_vector_evaluation
from src.evaluation.evaluate_keyword import run_keyword_evaluation
from src.evaluation.evaluate_llm import run_llm_evaluation
from src.evaluation.evaluate_mmr import run_mmr_evaluation


def evaluate_pipeline(ticker: str):
    print(f"Running automated evaluations for {ticker}")

    hit_rate = run_vector_evaluation(ticker)
    mmr_hit_rate = run_mmr_evaluation(ticker)
    llm_accuracy = run_llm_evaluation(ticker)
    keyword_hit_rate = run_keyword_evaluation(ticker)

    conn = psycopg2.connect("postgresql://airflow:airflow@postgres:5432/airflow")
    cursor = conn.cursor()
    
    # PostgreSQL syntax for auto-increment is SERIAL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT,
            hit_rate REAL,
            mmr_hit_rate REAL,
            llm_accuracy REAL,
            keyword_hit_rate REAL
        )
    """)
    # PostgreSQL uses %s for placeholders, not ?
    cursor.execute(
        "INSERT INTO evaluations (ticker, hit_rate, mmr_hit_rate, llm_accuracy, keyword_hit_rate) VALUES (%s, %s, %s, %s, %s)",
        (ticker, hit_rate, mmr_hit_rate, llm_accuracy, keyword_hit_rate)
    )
    conn.commit()
    conn.close()

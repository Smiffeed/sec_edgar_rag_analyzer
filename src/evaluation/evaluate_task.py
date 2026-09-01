import sqlite3

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

    conn = sqlite3.connect('/opt/airflow/data/telemetry.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT,
            hit_rate REAL,
            mmr_hit_rate REAL,
            llm_accuracy REAL,
            keyword_hit_rate REAL
        )
    """)
    cursor.execute(
        "INSERT INTO evaluations (ticker, hit_rate, mmr_hit_rate, llm_accuracy, keyword_hit_rate) VALUES (?, ?, ?, ?, ?)",
        (ticker, hit_rate, mmr_hit_rate, llm_accuracy, keyword_hit_rate)
    )
    conn.commit()
    conn.close()

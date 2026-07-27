import sqlite3
from evaluate import run_vector_evaluation
from evaluate_llm import run_llm_evaluation
from evaluate_keyword import run_keyword_evaluation

def evaluate_pipeline(ticker: str):
    print(f"Running automated evaluations for {ticker}")

    hit_rate = run_vector_evaluation()
    llm_accuracy = run_llm_evaluation()
    keyword_hit_rate = run_keyword_evaluation()

    conn = sqlite3.connect('/opt/airflow/data/telemetry.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO evaluations (ticker, hit_rate) VALUES (?, ?, ?, ?)",
        (ticker, hit_rate, llm_accuracy, keyword_hit_rate)
    )
    conn.commit()
    conn.close()

import sqlite3
from evaluate import run_vector_evaluation

def evaluate_pipeline(ticker: str):
    print(f"Running automated evaluations for {ticker}")

    hit_rate = run_vector_evaluation()

    conn = sqlite3.connect('/opt/airflow/data/telemetry.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO evaluations (ticker, hit_rate) VALUES (?, ?)",
        (ticker, hit_rate)
    )
    conn.commit()
    conn.close()

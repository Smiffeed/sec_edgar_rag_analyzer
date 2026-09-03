import logging

import pandas as pd
import psycopg2
import streamlit as st
from pandas.errors import DatabaseError

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
st.title("📊 Telemetry Dashboard")

try:
    conn = psycopg2.connect("postgresql://airflow:airflow@postgres:5432/airflow")
    df = pd.read_sql_query("SELECT * FROM queries", conn)
    conn.close()
except DatabaseError as e:
    logger.error(f"Error occurred while reading telemetry data: {e}")
    df = pd.DataFrame()  # Create an empty DataFrame if the table doesn't exist

try:
    conn_airflow = psycopg2.connect("postgresql://airflow:airflow@postgres:5432/airflow")
    df_evals = pd.read_sql_query("SELECT * FROM evaluations", conn_airflow)
    conn_airflow.close()
except DatabaseError as e:
    logger.error(f"Error occurred while reading evaluation data: {e}")
    df_evals = pd.DataFrame()  # Create an empty DataFrame if the table doesn't exist

if df.empty and df_evals.empty:
    st.info("👋 Welcome! No telemetry data is available yet. Ask a question first!")
    st.stop()  # This magically stops the rest of the script from running!
else:
    # Convert timestamp to datetime for charting
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # High-level Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Queries", len(df))
    col2.metric("Average Latency (s)", round(df['latency_seconds'].mean(), 2))
    col3.metric("Net Feedback Score", df['feedback'].sum())

    st.markdown("---")

    # Chart 1 & 2
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Chart 1: latency Over Time")
        st.line_chart(df.set_index('timestamp')['latency_seconds'])
    with col_b:
        st.subheader("Chart 2: Feedback Distribution")
        feedback_counts = df['feedback'].value_counts().rename(index={1: "Positive", 0: 'Neutral', -1: 'Negative'})
        st.bar_chart(feedback_counts)
    
    # Chart 3 & 4
    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Chart 3: Cumulative Queries")
        df['cumulative_queries'] = range(1, len(df) + 1)
        st.area_chart(df.set_index('timestamp')['cumulative_queries'])
    with col_d:
        st.subheader("Chart 4: Query Lengths")
        df['query_length'] = df['user_question'].apply(len)
        st.bar_chart(df['query_length'])

    # Chart 5
    st.subheader("Chart 5: Raw Telemetry Data")
    st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)
    
    st.markdown("---")
    
    # Chart 6
    st.subheader("Chart 6: LLM Evaluation (Hit Rate %)")

    if not df_evals.empty:
        # Timestamp to datetime object
        df_evals['timestamp'] = pd.to_datetime(df_evals['timestamp'])
        df_evals['overall_mean'] = df_evals[['hit_rate', 'llm_accuracy', 'keyword_hit_rate', 'mmr_hit_rate']].mean(axis=1)

        latest_health = df_evals.iloc[-1]['overall_mean']
        st.line_chart(df_evals.set_index('timestamp')[['hit_rate', 'llm_accuracy', 'keyword_hit_rate', 'mmr_hit_rate', 'overall_mean']])
        st.metric("Latest System Health Score", f"{round(latest_health, 2)}%")
    else:
        st.metric("Latest System Health Score", "N/A")
        st.info("No evaluation data found. Run the Airflow DAG to generate MLOps metrics")


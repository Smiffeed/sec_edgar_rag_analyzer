import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(layout="wide")
st.title("📊 Telemetry Dashboard")

conn = sqlite3.connect("telemetry.db")
df = pd.read_sql_query("SELECT * FROM queries", conn)
conn.close()

if df.empty:
    st.warning("No data available yet. Ask a question first!")
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

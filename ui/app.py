import streamlit as st
import datetime
import os
import requests
from requests.auth import HTTPBasicAuth
from src.generate import ask_question

def get_available_tickers():
    base_path ="airflow/data/sec-edgar-filings/"
    if os.path.exists(base_path):
        return [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]
    return []

available_tickers = get_available_tickers()

# UI Setup
# Titile of Web Page
st.title("📈 SEC Edgar RAG Analyzer")
st.markdown("Ask questions about latest 10-K filing!")

with st.sidebar:
    st.header("1. Select Existing Data")
    if not available_tickers:
        st.warning("No data found! Please download a ticker below.")
        selected_ticker = None
    else:
        selected_ticker = st.selectbox("Choose a company to query:", 
                                       available_tickers,
                                       index=None,
                                       placeholder="Select a company...")

    st.divider()

    st.header("2. Download new Data")
    new_ticker = st.text_input("Enter Ticker (e.g., NVDA):").upper()
    if st.button("Trigger Airflow Pipeline"):
        if new_ticker:
            # Trigger API
            st.info(f"Triggering Airflow for {new_ticker}")
            try:
                auth_response = requests.post(
                    "http://airflow-apiserver:8080/auth/token",
                    json={"username": "airflow", "password": "airflow"}
                )
                token = auth_response.json().get("access_token")

                response = requests.post(
                    "http://airflow-apiserver:8080/api/v2/dags/sec_edgar_ingestion/dagRuns",
                    json={
                        "conf": {"ticker": new_ticker},
                        "logical_date": datetime.datetime.utcnow().isoformat() + "Z"
                      }, # Pass parameter
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    st.success(f"Successfully triggered DAG for {new_ticker}! Check airflow UI (localhost:8080) for progress.")
                else:
                    st.error(f"Failed to trigger DAG. Airflow returned: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Could not connect to Airflow: {e}")

# Chat input box
user_input = st.chat_input("E.g., What are the main risk factors?")

# If user hits enter
if user_input:
    if not selected_ticker:
        st.error("Please download and select a company from the sidebar first")
    else:
        # Display question on the screen
        with st.chat_message("user"):
            st.write(user_input)

        # Loading Spineer while LLM thinks
        with st.spinner("Analyzing SEC filings..."):
            answer = ask_question(user_input, selected_ticker)

            # Display AI answer
            with st.chat_message("assistant"):
                st.write(answer)

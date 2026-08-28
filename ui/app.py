import datetime
import os
import time

import requests
import streamlit as st

from src.generate import add_feedback, ask_question


def get_available_tickers():
    base_path ="airflow/data/sec-edgar-filings/"
    if os.path.exists(base_path):
        return [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]
    return []

def wait_for_pipeline(run_id, token):
    with st.spinner("Pipeline is running..."):
        while True:
            response = requests.get(
                f"http://airflow-apiserver:8080/api/v2/dags/sec_edgar_ingestion/dagRuns/{run_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            state = response.json().get("state")

            if state == "success":
                st.success("Pipeline finished successfully")
                break
            elif state == "failed":
                st.error("Pipeline failed")
                break
            time.sleep(3)

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
    if st.button("Trigger Airflow Pipeline") and new_ticker:
        # Trigger API
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
                    "logical_date": datetime.datetime.now(tz=datetime.UTC).isoformat() + "Z"
                    }, # Pass parameter
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                run_id = response.json().get("dag_run_id")
                wait_for_pipeline(run_id, token)
            else:
                st.error(f"Failed to trigger DAG. Airflow returned: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to Airflow: {e}")


# Initialize chat history and track the active ticker
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = None

# If the user switches the ticker in the sidebar, clear the chat history
if selected_ticker != st.session_state.current_ticker:
    st.session_state.messages = []
    st.session_state.current_ticker = selected_ticker

# Render the persistent chat history
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        # Render a unique feedback button for each AI answer
        if msg["role"] == "assistant":
            feedback = st.feedback("thumbs", key=f"fb_{i}")
            
            # If the user clicks a feedback button and we haven't submitted it yet
            if feedback is not None and not msg.get("feedback_submitted"):
                score = 1 if feedback == 1 else -1
                # The user's question is always the message right before the AI's answer
                user_question = st.session_state.messages[i-1]["content"]
                
                add_feedback(user_question, score)
                msg["feedback_submitted"] = True
                st.toast("Feedback recorded! Thanks.")

# Chat input box
user_input = st.chat_input("E.g., What are the main risk factors?")

if user_input:
    if not selected_ticker:
        st.error("Please download and select a company from the sidebar first")
    else:
        # 1. Append and display user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # 2. Get AI answer
        with st.spinner("Analyzing SEC filings..."):
            answer = ask_question(user_input, selected_ticker)

        # 3. Append AI answer to state and force a UI refresh
        st.session_state.messages.append({"role": "assistant", "content": answer, "feedback_submitted": False})
        st.rerun()

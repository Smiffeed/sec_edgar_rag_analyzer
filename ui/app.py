import datetime
import os
import time

import requests
import streamlit as st

from src.rag.generate import add_feedback, ask_question


def get_available_tickers():
    base_path ="airflow/data/sec-edgar-filings/"
    if os.path.exists(base_path):
        return [folder for folder in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, folder))]
    return []

def wait_for_pipeline(run_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    with st.status("Initializing Airflow Pipeline...", expanded=True) as status:
        while True:
            # 1. Check overall DAG state
            dag_resp = requests.get(
                f"http://airflow-apiserver:8080/api/v2/dags/sec_edgar_ingestion/dagRuns/{run_id}",
                headers=headers
            )
            state = dag_resp.json().get("state")

            # 2. Check individual task states
            ti_resp = requests.get(
                f"http://airflow-apiserver:8080/api/v2/dags/sec_edgar_ingestion/dagRuns/{run_id}/taskInstances",
                headers=headers
            )
            
            tasks = ti_resp.json().get("task_instances", [])
            
            running_tasks = [t["task_id"] for t in tasks if t.get("state") == "running"]
            
            if running_tasks:
                status.update(label=f"⚙️ Airflow is running: {running_tasks[0]}...", state="running")
            elif state == "queued":
                status.update(label="⏳ Pipeline is queued in Airflow... waiting to start.", state="running")
            else:
                success_tasks = [t["task_id"] for t in tasks if t.get("state") == "success"]
                if success_tasks:
                    status.update(label=f"✅ Completed: {success_tasks[-1]}... waiting for next step.", state="running")

            if state == "success":
                status.update(label="🎉 Pipeline finished successfully!", state="complete", expanded=False)
                break
            elif state == "failed":
                status.update(label="❌ Pipeline failed! Check Airflow logs.", state="error", expanded=True)
                break
            
            time.sleep(2)
        
        # After completion, refresh page to update tickers list
        time.sleep(2)
        st.rerun()

def check_active_pipeline():
    try:
        # Get Token
        auth_resp = requests.post(
            "http://airflow-apiserver:8080/auth/token",
            json={"username": "airflow", "password": "airflow"},
            timeout=2
        )
        if auth_resp.status_code == 200:
            token = auth_resp.json().get("access_token")
            # Fetch ALL runs and filter
            runs_resp = requests.get(
                "http://airflow-apiserver:8080/api/v2/dags/sec_edgar_ingestion/dagRuns",
                headers={"Authorization": f"Bearer " + token},
                timeout=2
            )
            runs = runs_resp.json().get("dag_runs", [])
            active_runs = [r for r in runs if r.get("state") in ("running", "queued")]
            
            if active_runs:
                return active_runs[0].get("dag_run_id"), token
    except Exception:
        pass
    return None, None

available_tickers = get_available_tickers()

# UI Setup
st.title("📊 SEC Edgar RAG Analyzer")
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
        if selected_ticker:
            if st.button(f"🗑️ Delete {selected_ticker}", use_container_width=True):
                with st.spinner(f"Deleting {selected_ticker} data..."):
                    import shutil
                    import chromadb
                    
                    try:
                        client = chromadb.HttpClient(host="chroma", port=8000)
                        collection = client.get_collection(name="sec_filings")
                        collection.delete(where={"ticker": selected_ticker})
                    except Exception:
                        pass
                        
                    base_path = f"airflow/data/sec-edgar-filings/{selected_ticker}"
                    if os.path.exists(base_path):
                        shutil.rmtree(base_path)
                        
                    st.success(f"Successfully deleted {selected_ticker}!")
                    time.sleep(1)
                    st.rerun()

    st.divider()

    st.header("2. Download new Data")
    
    active_run_id, active_token = check_active_pipeline()
    
    if active_run_id:
        st.info("⚠️ A pipeline is currently running in the background.")
        wait_for_pipeline(active_run_id, active_token)
    else:
        new_ticker = st.text_input("Enter Ticker (e.g., NVDA):").upper()
        if st.button("Trigger Airflow Pipeline") and new_ticker:
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
                        "logical_date": datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
                    },
                    headers={"Authorization": f"Bearer {token}"}
                )

                if response.status_code == 200:
                    run_id = response.json().get("dag_run_id")
                    wait_for_pipeline(run_id, token)
                else:
                    st.error(f"Failed to trigger DAG. Airflow returned: {response.status_code} - {response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to Airflow: {e}")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_ticker" not in st.session_state:
    st.session_state.current_ticker = None

if selected_ticker != st.session_state.current_ticker:
    st.session_state.messages = []
    st.session_state.current_ticker = selected_ticker

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        
        if msg["role"] == "assistant":
            feedback = st.feedback("thumbs", key=f"fb_{i}")
            if feedback is not None and not msg.get("feedback_submitted"):
                score = 1 if feedback == 1 else -1
                user_question = st.session_state.messages[i-1]["content"]
                add_feedback(user_question, score)
                msg["feedback_submitted"] = True
                st.toast("Feedback recorded! Thanks.")

user_input = st.chat_input("E.g., What are the main risk factors?")

if user_input:
    if not selected_ticker:
        st.error("Please download and select a company from the sidebar first")
    else:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Analyzing SEC filings..."):
            answer = ask_question(user_input, selected_ticker)

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)
            st.rerun()
# SEC Filing RAG Analyzer - TO-DO List

## Completed
- [x] Data Ingestion (`ingest.py` with sec-edgar-downloader)
- [x] Parsing & Chunking (`parse.py` and `vectorize.py` using Unstructured)
- [x] Vector Database Setup (ChromaDB `PersistentClient`)
- [x] Retrieval Logic (`retrieve.py`)
- [x] LLM Integration (`generate.py` with OpenRouter API)
- [x] Web Interface (`app.py` with Streamlit)
- [x] **RAG Evaluation:** Evaluated Keyword Search (TF-IDF) vs Vector Search (ChromaDB). Vector search won (50% vs 25%).
- [x] **LLM Evaluation:** Created LLM-as-a-judge pipeline (`evaluate_llm.py`). Tuned model to hit 75% accuracy.

## Upcoming Features / Backlog
- [x] **Orchestration (Airflow):** Fix the typos in `airflow/dags/sec_edgar_ingestion.py`. Add volume mapping and PYTHONPATH to `docker-compose.yaml` to support the enterprise `scripts/` folder architecture.
- [x] **Containerize Streamlit:** Add `app.py` as a new service in `docker-compose.yaml` so the frontend spins up alongside Airflow.
- [ ] **Prompt Engineering:** Update the prompt template in `generate.py` to enforce strict formatting rules (e.g., "Provide the answer as a clean, bulleted list. Do not use tables.") to prevent empty markdown tables in the Streamlit UI.
- [ ] **Data Cleaning:** Update `parse.py` to strip out Javascript/HTML artifacts (like `$("products)`) from the raw SEC text before it is embedded into ChromaDB.
- [ ] **Alternate Embedding Model:** Swap ChromaDB's default `all-MiniLM-L6-v2` with a stronger HuggingFace or OpenAI embedding model to compare hit rates.

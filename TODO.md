# SEC Filing RAG Analyzer - TO-DO List

## Completed
- [x] Data Ingestion (`ingest.py` with sec-edgar-downloader)
- [x] Parsing & Chunking (`parse.py` and `vectorize.py` using Unstructured)
- [x] Vector Database Setup (ChromaDB `PersistentClient`)
- [x] Retrieval Logic (`retrieve.py`)
- [x] LLM Integration (`generate.py` with OpenRouter API)
- [x] Web Interface (`app.py` with Streamlit)

## Upcoming Features / Backlog
- [ ] **Prompt Engineering (Priority):** Update the prompt template in `generate.py` to enforce strict formatting rules (e.g., "Provide the answer as a clean, bulleted list. Do not use tables.") to prevent empty markdown tables in the Streamlit UI.
- [ ] **Data Cleaning:** Update `parse.py` to strip out Javascript/HTML artifacts (like `$("products)`) from the raw SEC text before it is embedded into ChromaDB.
- [ ] **Orchestration:** Containerize the ingestion scripts and schedule them using Airflow (as per the original Architecture diagram).
- [ ] **RAG Evaluation:** Implement evaluation metrics to score the retrieval accuracy (required for max points in project criteria).

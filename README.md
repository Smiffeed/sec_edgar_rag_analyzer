# SEC EDGAR Financial RAG Analyzer

An end-to-end Retrieval-Augmented Generation (RAG) system built to analyze unstructured SEC 10-K financial filings. This project was built as the capstone for the **DataTalksClub LLM Zoomcamp**.

## 📊 Problem Statement
Financial analysts and quants spend countless hours manually reading hundreds of pages of complex SEC filings (like 10-Ks) to extract sentiment, risk factors, and forward-looking guidance. The sheer volume and density of these documents make it incredibly difficult to quickly find specific financial information or context across multiple years and companies.

## 🚀 Solution Architecture
This project solves this by building an Enterprise-grade RAG system tailored specifically for SEC EDGAR documents. It programmatically downloads, parses, and intelligently chunks 10-K SEC filings, storing their embeddings in a Vector Database. 

Through a Streamlit interface, users can ask questions in natural language. The system retrieves the most relevant document chunks and passes them to an LLM to generate an accurate, highly contextualized answer.

### Key Technologies & Zoomcamp Criteria Met:
- **Data Ingestion (Airflow):** Automated orchestration using Apache Airflow. DAGs are parameterized to allow dynamic ticker downloads (e.g., AAPL, TSLA) via `sec-edgar-downloader`.
- **Advanced Data Scrubbing:** Custom Regex pipelines to sanitize raw HTML and JavaScript artifacts from SEC documents before ingestion.
- **Knowledge Base (ChromaDB):** Isolated containerized Vector Database for semantic search.
- **LLM Integration:** Connected to OpenRouter (`nvidia/nemotron-3-super-120b-a12b:free`) for high-quality financial reasoning.
- **Retrieval Evaluation:** Ground truth testing mathematically comparing Keyword Search (TF-IDF) vs Vector Search (ChromaDB).
- **RAG Evaluation:** Implemented an automated "LLM-as-a-Judge" evaluation pipeline.
- **Interface & Observability:** Streamlit Web UI equipped with a SQLite Telemetry database that logs user questions, LLM answers, and API latency for production monitoring.
- **Containerization:** Fully dockerized environment (`docker-compose.yaml`) managing Airflow, Postgres, and Streamlit microservices.

---

## 🛠️ Project Structure
```text
├── airflow/
│   ├── dags/                  # Airflow orchestration DAGs
│   └── scripts/               # Business logic (Ingestion, Parsing, Vectorization)
├── Dockerfile                 # Custom Airflow image (pre-installs NLP models)
├── Dockerfile.streamlit       # Custom Streamlit image
├── docker-compose.yaml        # Multi-container cluster orchestration
├── app.py                     # Streamlit frontend application
├── generate.py                # Core LLM generation and SQLite Telemetry logic
├── evaluate_llm.py            # LLM-as-a-judge evaluation script
└── evaluate_keyword.py        # Retrieval algorithm evaluation
```

---

## 💻 Setup & Execution Instructions

### 1. Prerequisites
- Docker & Docker Compose
- An API Key from [OpenRouter](https://openrouter.ai/)

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_api_key_here
EMAIL=your_email@example.com
COMPANY=YourCompanyName
AIRFLOW_UID=1000
```

### 3. Build and Start the Cluster
Bring up the entire microservices architecture (Airflow, Postgres, Streamlit):
```bash
docker compose up -d --build
```

### 4. Run the Data Pipeline (Airflow)
1. Navigate to the Airflow UI at **http://localhost:8080** (Login: `airflow` / `airflow`)
2. Find the `sec_edgar_ingestion` DAG.
3. Click the Play button -> **"Trigger DAG w/ config"**.
4. Enter a stock ticker (e.g., `AAPL`) and run the pipeline. Airflow will download the 10-K, scrub the Javascript, chunk the text, and vectorize it into ChromaDB.

### 5. Access the Web App (Streamlit)
Once the Airflow pipeline successfully finishes, navigate to **http://localhost:8501**.
Ask questions like: *"What are the key risk factors facing the company?"*

Check your terminal logs to see the SQLite Telemetry database tracking your exact API latency and responses!

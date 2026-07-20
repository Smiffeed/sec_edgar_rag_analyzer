# SEC Filing RAG Analyzer

## Problem Statement
Financial analysts and quants spend countless hours manually reading hundreds of pages of complex SEC filings (like 10-Ks) to extract sentiment, risk factors, and forward-looking guidance. The sheer volume and density of these documents make it incredibly difficult to quickly find specific financial information or context across multiple years and companies.

## Solution
This project solves this by building an end-to-end Retrieval-Augmented Generation (RAG) system tailored specifically for SEC EDGAR documents. 

The system programmatically downloads, parses, and intelligently chunks 10-K SEC filings, storing their embeddings in a Vector Database. Through a Streamlit interface, users can ask questions in natural language. The system retrieves the most relevant document chunks and passes them to an LLM to generate an accurate, highly contextualized answer, complete with source citations.

In accordance with the DataTalksClub LLM Zoomcamp project criteria, this application features:
- **Data Ingestion:** Fetching SEC data via `sec-edgar-downloader` / `edgartools`.
- **Knowledge Base:** Building and connecting to a local Vector Database (ChromaDB).
- **Application Flow:** Implementing hybrid search for context retrieval and dynamic prompt construction.
- **RAG Evaluation:** (Upcoming) Ground truth testing for retrieval accuracy.
- **Interface & Monitoring:** (Upcoming) Streamlit UI and user feedback collection.

## Project Structure
- `data/` (Ignored): Will store the downloaded SEC filings.
- `chroma_db/` (Ignored): Will store the vector embeddings.

## Setup Instructions
1. Initialize the virtual environment:
   ```bash
   uv venv
   ```
2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```
*(We will add dependency installation instructions in the next steps!)*

## Next Steps
- Implement script to download 10-K SEC filings.
- Parse and chunk the text.
- Set up a Vector Database and create embeddings.
- Implement retrieval logic.
- Connect to an LLM.
- Build the Streamlit UI.

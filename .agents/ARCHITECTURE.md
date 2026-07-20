# Project: SEC Filing RAG Analyzer

## The Idea
We are building an end-to-end Retrieval-Augmented Generation (RAG) system to query financial documents (like 10-K SEC filings). This allows Quants and Data Analysts to quickly extract sentiment, risk factors, and forward-looking guidance without manually reading hundreds of pages.

## Learning Objectives
1. **Data Ingestion:** Learn how to programmatically fetch unstructured data (SEC filings via `sec-edgar-downloader`).
2. **Vectorization:** Understand how to chunk text and create vector embeddings.
3. **Knowledge Base:** Learn to store and query embeddings in a Vector Database.
4. **LLM Integration:** Understand how to construct prompts dynamically using retrieved context.
5. **Orchestration & UI:** Tie it all together with Airflow (orchestration) and Streamlit (UI).

## Architecture Flow

1. **Data Source:** SEC EDGAR database.
2. **Ingestion Pipeline:** Python script (later orchestrated by Airflow) downloads filings and chunks the text.
3. **Embedding:** Chunks are passed through an embedding model (e.g., HuggingFace or OpenAI).
4. **Storage:** Vectors are saved in a Vector Database (e.g., ChromaDB, FAISS, or Pinecone).
5. **Retrieval:** Streamlit UI takes a user query, embeds it, and searches the Vector DB for the Top-K most relevant chunks.
6. **Generation:** The retrieved chunks and the user query are sent to an LLM (e.g., OpenAI, Groq, Ollama) to generate a grounded answer.

## Next Steps (To be driven by the user)
- Step 1: Set up the Python environment (virtual environment, dependencies).
- Step 2: Write a simple script to download a single 10-K filing.
- Step 3: Parse and chunk the text.
- Step 4: Set up the Vector Database and embed the chunks.
- Step 5: Write the retrieval logic.
- Step 6: Connect to the LLM to generate answers.
- Step 7: Build the Streamlit UI.

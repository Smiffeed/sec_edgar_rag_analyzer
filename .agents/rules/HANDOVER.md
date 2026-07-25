# 📝 Session Handover & To-Do List

**Date/Time of Handover:** 2026-07-25 (End of Day)
**Current Status:** We successfully refactored the pipeline to be dynamic. We completed Ticket RAG-101 (Dynamic LLM provider via `.env`) and Ticket RAG-102 Task A (Dynamic Airflow Ingestion & Vectorization using `glob` and adding the `ticker` to Chroma metadata).

### 🚀 Upcoming Tasks (For Next Session)

When you resume this session, ask the AI to help you execute the remainder of Ticket RAG-102:

#### Ticket RAG-102: Dynamic Stock Data Ingestion (Task B - Streamlit UI)
- [ ] **Dynamic UI (Streamlit):** Update `app.py` to scan the `data/sec-edgar-filings/` folder for downloaded tickers, and populate a dynamic dropdown menu (`st.selectbox`). This allows the reviewer to query against any stock that Airflow has ingested.
- [ ] **Metadata Filtering:** Update `generate.py`'s `ask_question()` signature to accept a `ticker` parameter. Add `where={"ticker": ticker}` to the `collection.query()` so ChromaDB only searches that company's chunks.

---
*Note to next AI Agent: Read this file carefully upon startup. The user is acting as a Junior Engineer and prefers to be mentored (Senior Tech Lead persona). Do not dump full code solutions; provide Jira tickets and isolated snippets.*

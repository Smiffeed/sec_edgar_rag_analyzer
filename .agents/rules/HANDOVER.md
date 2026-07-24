# 📝 Session Handover & To-Do List

**Date/Time of Handover:** 2026-07-24 (Leaving Office)
**Current Status:** The core pipeline is 100% complete and working beautifully. The UI has session-state chat memory, the SQLite telemetry dashboard is live with 5 charts, the README is fully rewritten to match a professional Data Engineering pipeline, and the project is technically ready for submission.

### 🚀 Upcoming Tasks (For Home Session)

When you resume this session, ask the AI to help you execute the following To-Do list:

#### 1. Dynamic LLM Provider Configuration
To ensure peer reviewers (who might not have OpenRouter) can easily grade the project, we need to make the LLM provider dynamic.
- [ ] **Update `generate.py`**: Refactor the OpenAI client to pull `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` from the `.env` file instead of hardcoding OpenRouter.
- [ ] **Update `README.md`**: Provide two `.env` templates in the setup instructions (one for standard OpenAI, one for OpenRouter).

#### 2. Dynamic Stock Data Ingestion
- [ ] **Update Pipeline / UI**: Currently, the system might be heavily skewed towards Apple (AAPL). We need to ensure the Airflow pipeline can dynamically fetch and process different stock tickers based on user input, and that the Streamlit UI can query against specific companies if multiple 10-Ks are in the database.

---
*Note to next AI Agent: Read this file carefully upon startup. The user is acting as a Junior Engineer and prefers to be mentored (Senior Tech Lead persona). Do not dump full code solutions; provide Jira tickets and isolated snippets.*

# SEC Filing RAG Analyzer - TO-DO List

## Upcoming Features
- [ ] **Enhance LLM Prompt with Context:** Create a Prompt Template that dynamically injects the user's question alongside the retrieved context from ChromaDB before sending it to the LLM (OpenRouter).

*Example Format:*
```text
Question:
{user_question}

Context:
{retrieved_chunks}
```

# LLM Zoomcamp Project Plan: MLOps Evaluation 📈

This document tracks the steps needed to achieve full points (2/2) for both the Retrieval and LLM Evaluation criteria in the LLM Zoomcamp project.

## 1. Retrieval Evaluation (Target: 2 Points)
**Criteria:** Multiple retrieval approaches must be evaluated, and the best one is used.
* **Approach A (Baseline):** Standard Vector Similarity Search using Cosine Distance.
* **Approach B (Preferred):** Vector Similarity Search + MMR (Maximal Marginal Relevance) to increase the diversity of retrieved context.

**Implementation Plan:**
- [ ] Create a retrieval evaluation script that takes a ground truth dataset (questions + document IDs).
- [ ] Run the dataset against Approach A and record the Hit Rate / MRR.
- [ ] Run the dataset against Approach B and record the Hit Rate / MRR.
- [ ] Document the results and officially configure the main Streamlit/RAG pipeline to use Approach B (MMR).

## 2. LLM Evaluation (Target: 2 Points)
**Criteria:** Multiple approaches (e.g., prompts) are evaluated, and the best one is used.
* **Approach A (Baseline):** Standard prompt (e.g., `"Answer the question using the context:"`).
* **Approach B (Preferred):** Chain-of-Thought (CoT) prompt forcing the LLM to reason step-by-step before answering.

**Implementation Plan:**
- [ ] Update `evaluate_llm.py` to loop over the two different prompt templates.
- [ ] Use the LLM Judge to score the factual accuracy of Approach A vs Approach B.
- [ ] Document the results and officially update `src/generate.py` to use Approach B (Chain-of-Thought) in the production app.

## 3. Dynamic Ground Truth (Optional / Best Practice)
- [ ] Refactor the static `ground_truth.json` (currently hardcoded to AAPL) into a dynamic structure, or use reference-free evaluation to properly support dynamic SEC ticker ingestion.
- [ ] Backlog: Deep-dive into how the MMR algorithm actually works line-by-line (Post-Project)

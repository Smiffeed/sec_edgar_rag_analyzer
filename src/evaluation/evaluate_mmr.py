import json
import logging

import chromadb
import numpy as np
from chromadb.utils import embedding_functions
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def calculate_mmr(query_embedding, doc_embeddings, top_k=3, labda_multy=0.5):
    # Calculate similarity every document is to the question
    sim_to_query = cosine_similarity([query_embedding], doc_embeddings)[0]

    selected_indices = []
    unselected_indices = list(range(len(doc_embeddings)))

    # Pick the absolute best document first (Pure similarity)
    best_idx = np.argmax(sim_to_query)
    selected_indices.append(best_idx)
    unselected_indices.remove(best_idx)

    # Applying the diversity penalty
    while len(selected_indices) < top_k and unselected_indices:
        best_score = -float('inf')
        best_idx_to_add = -1

        for idx in unselected_indices:
            # How similar is it to the question
            relevance = sim_to_query[idx]
            
            # how similar is it to the documents we already picked
            selected_docs = [doc_embeddings[i] for i in selected_indices]
            sim_to_selected = cosine_similarity([doc_embeddings[idx]], selected_docs)[0]
            redundancy = np.max(sim_to_selected) # Grab the highest similarity to any selected document

            # MMR score calculation
            mmr_score = (labda_multy * relevance) - ((1 - labda_multy) * redundancy)

            if mmr_score > best_score:
                best_score = mmr_score
                best_idx_to_add = idx

        selected_indices.append(best_idx_to_add)
        unselected_indices.remove(best_idx_to_add)
    return selected_indices

def run_mmr_evaluation(ticker: str) -> float:
    # ChromaDB
    client = chromadb.HttpClient(host="chroma", port=8000)
    collection = client.get_or_create_collection(name="sec_filings")
    bge_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")

    # Load Ground Truth
    with open("/opt/airflow/data/ground_truth.json", "r") as f:
        ground_truth = json.load(f)

    hits = 0
    total_questions = len(ground_truth)
    logger.info(f"Starting MMR Evaluation for {total_questions} questions\n")

    for item in ground_truth:
        question = item["question"]
        correct_doc_id = item["document_id"]

        # Get the embedding for the question
        query_embedding = bge_embeddings([question])
        result = collection.query(
            query_embeddings=query_embedding,
            n_results=10,  # Retrieve top 10 documents for MMR evaluation
            where={"ticker": ticker},
            include=["embeddings", "documents"]
        )

        retrieved_ids = result['ids'][0]
        retrieved_docs = result['embeddings'][0]

        # Pass the embeddings to the MMR function
        # it will look at the embeddings and return the top 3 document indices (e.g. [0, 2, 5]) based on MMR
        # Calculate MMR to get top 3 documents
        best_indices = calculate_mmr(
            query_embedding[0],
            retrieved_docs,
            top_k=3, labda_multy=0.5
        )

        final_3_ids = [retrieved_ids[i] for i in best_indices]
        if correct_doc_id in final_3_ids:
            hits += 1
            logger.info(f"Question: {question} | Correct Document ID: {correct_doc_id} | Retrieved IDs: {final_3_ids} | HIT")
        else:
            logger.info(f"Question: {question} | Correct Document ID: {correct_doc_id} | Retrieved IDs: {final_3_ids} | MISS")

    hit_rate = hits / total_questions * 100
    logger.info(f"Current Hit Rate: {hit_rate:.2f}%\n")
    return hit_rate
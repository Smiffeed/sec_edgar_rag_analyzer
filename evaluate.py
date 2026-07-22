import chromadb
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

# Connect to Database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="sec_filings")

# Load the Ground Truth dataset
with open("ground_truth.json", "r") as f:
    ground_truth = json.load(f)

hits = 0
total_questions = len(ground_truth)

logging.info(f"Evaluating {total_questions} questions...")

# Loop through the test questions
for item in ground_truth:
    question = item["question"]
    correct_doc_id = item["document_id"]

    # Ask ChromaDB the question
    results = collection.query(
        query_texts=[question],
        n_results=3 # top 3 chunks
    )

    # Check if the correct chunk ID is in ther results
    retrieved_ids = results["ids"][0]

    if correct_doc_id in retrieved_ids:
        hits += 1
        logging.info(f"HIT: {question[:50]}...")
    else:
        logging.info(f"MISS: {question[:50]}...")
    
# Calculate the final correct_doc_id
hit_rate = (hits / total_questions) * 100
logging.info(f"\nFINAL HIT RATE: {hit_rate}%")

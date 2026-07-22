import chromadb
import json
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

# Connect to Database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="sec_filings")

db_data = collection.get()
all_documents = db_data['documents']
all_ids = db_data['ids']

# Build the Keyword Search Engine (TF-IDF)
logging.info("Building keyword Search Engine...")
vectorizer = TfidfVectorizer(stop_words='english')
doc_matrix = vectorizer.fit_transform(all_documents)

with open("ground_truth.json", "r") as f:
    ground_truth = json.load(f)

hits = 0
total_questions = len(ground_truth)

logging.info(f"Evaluating {total_questions} questions using keyword Search")

# Evaluate
for item in ground_truth:
    question = item["question"]
    correct_doc_id = item["document_id"]

    # Transform the question into a keyword vector
    question_vector = vectorizer.transform([question])

    # Calculate similarity scores against all documents
    scores = cosine_similarity(question_vector, doc_matrix).flatten()

    # Get the indices of the top 3 highest scoring documents
    top_3_indices = scores.argsort()[-3:][::-1]

    # Get actual chunk IDs
    retrieved_ids = [all_ids[i] for i in top_3_indices]

    if correct_doc_id in retrieved_ids:
        hits += 1
        logging.info(f"HIT: {question[:50]}")
    else:
        logging.info(f"MISS: {question[:50]}")

hit_rate = (hits / total_questions) * 100
logging.info(f"\nFINAL KEYWORD HIT RATE: {hit_rate}%")

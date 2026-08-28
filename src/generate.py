import logging
import os
import sqlite3
import time

import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from openai import OpenAI
from sentence_transformers import CrossEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Telemetry Database Setup
def setup_telemetry():
    conn = sqlite3.connect("telemetry.db", check_same_thread=False)
    cursor = conn.cursor()
    # Create a table to log our LLm data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            user_question TEXT,
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            llm_answer TEXT,
            latency_seconds REAL,
            feedback INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT,
            hit_rate REAL,
            llm_accuracy REAL
        )
    """)
    # Try to alter table just in case it already exists without feedback column
    try:
        cursor.execute("ALTER TABLE queries ADD COLUMN feedback INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    return conn

logger.info("Setting up telemetry")
# Initialize telemetry when app start
telemetry_conn = setup_telemetry()
logger.info("Telemetry setup done")

# Initialize ChromaDB via HTTP Client (Client/Server mode avoids Docker permission issues)
client = chromadb.HttpClient(host="chroma", port=8000)
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
bde_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")
collection = client.get_or_create_collection(name="sec_filings")


# Initialize The OpenAI Client
llm_client = OpenAI(
    base_url=os.getenv("LLM_URL"),
    api_key=os.getenv("LLM_API_KEY")
)

def ask_question(user_question: str, ticker: str):
    logger.info("Rewriting user query")
    rewrite_response = llm_client.chat.completions.create(
        model=os.getenv("LLM_MODEL"),
        messages=[
            {"role": "system", "content": "you are a search query rewriter. Rewrite the user query into a eighly formal, descriptive question optimized for a semantic vector database search, and to be more specific and relevant to the context of SEC filings. Return ONLY the rewritten question."},
            {"role": "user", "content": user_question}
        ],
        temperature=0.1  # Keep it deterministic
    )
    user_question = rewrite_response.choices[0].message.content
    logger.info("Building Keyword Serach Engine")
    all_docs = collection.get(where={"ticker": ticker})
    all_texts = all_docs['documents']

    if not all_texts:
        return f" The data for **{ticker}** has been downloaded, but it hasn't been processed into the database yet. Please click 'Trigger Airflow Pipeline' to process it!"

    logger.info("Asking LLM question")

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    logger.info("keyword Engine Ready")

    # Query the Vector Database
    query_embeddings = bde_embeddings([user_question])
    vector_results = collection.query(
        query_embeddings=query_embeddings,
        n_results=5, # Top 5 most relevant chunks
        where={"ticker": ticker}
    )
    vector_top_docs = vector_results['documents'][0]

    # Keyword Search
    query_vec = vectorizer.transform([user_question])
    similarities = cosine_similarity(query_vec, tfidf_matrix).flatten()
    # Get top 5 highest scores
    top_indices = similarities.argsort()[-5:][::-1]
    keyword_top_docs = [all_texts[i] for i in top_indices]
    
    # Reciprocal Rank Fusion
    # Remove Duplicate and keep the absolute best 3 chunks
    combined_docs = list(set(vector_top_docs + keyword_top_docs))
    pairs = [[user_question, i] for i in combined_docs]
    result = reranker.predict(pairs)
    top_indices = result.argsort()[-3:][::-1]
    best_3_docs = [combined_docs[i] for i in top_indices]

    context_text = "\n\n".join(best_3_docs)

    prompt = f"""
        Context:
        {context_text}

        Question:
        {user_question}
        """

    print("Sending to LLM.")

    start_time = time.time()

    # Call LLM
    try:
        response = llm_client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            # model="openai/gpt-oss-20b:free",
            messages=[
                {"role": "system", "content": "You are a financial analyst. Answer the question using ONLY the provided context."},
                {"role": "user", "content": prompt}
            ]
        )
        draft_answer = response.choices[0].message.content
        auditor_prompt = f"""
            Context:
            {context_text}

            Question:
            {user_question}
            
            Draft Answer:
            {draft_answer}

            - Please check draft answer and combine the best answer result. Moreover, don't tell me whether draft answer is correct or not.
            - DO not use markdown tables under any circumstances.
            - Format the final answer as a clean, easy-to-read bulleted list.
            - Ensure all numbers are clearly labeled.
            """

        response = llm_client.chat.completions.create(
            model=os.getenv("LLM_JUDGE_MODEL"),
            messages=[
                {"role": "system", "content": "You are a strict SEC auditor. Fact check the provided draft against the context."},
                {"role": "user", "content": auditor_prompt}
            ]
        )

        final_answer = response.choices[0].message.content
    except OpenAI.APIError as e:
        logger.error(f"Sorry, the LLM failed: {e}")
        return f"Sorry, the LLM failed: {e}"

    latency = round(time.time() - start_time, 2)

    # Log everything to the database
    try:
        cursor = telemetry_conn.cursor()
        cursor.execute(
            "INSERT INTO queries (user_question, llm_answer, latency_seconds) VALUES (?, ?, ?)",
            (user_question, final_answer, latency)
        )
        telemetry_conn.commit()
        logger.info(f"Telemetry Logged! Latency: {latency}s")
    except sqlite3.Error as e:
        logger.error(f"Failed to log telemetry: {e}")
        return f"Failed to log telemetry: {e}"

    return final_answer

def add_feedback(user_question: str, score: int):
    cursor = telemetry_conn.cursor()
    cursor.execute("""
        UPDATE queries 
        SET feedback = ? 
        WHERE id = (SELECT id FROM queries WHERE user_question = ? ORDER BY timestamp DESC LIMIT 1)
    """, (score, user_question))
    telemetry_conn.commit()

if __name__ == "__main__":
    ask_question("what are the key risk factors facing the company?", "")

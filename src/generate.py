import chromadb
from chromadb.utils import embedding_functions
import logging
import os
import time
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import CrossEncoder

load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

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
            latency_seconds REAL
        )
    """)
    conn.commit()
    return conn

logging.info("Setting up telemetry")
# Initialize telemetry when app start
telemetry_conn = setup_telemetry()
logging.info("Telemetry setup done")

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db/")
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
bde_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")
collection = client.get_or_create_collection(name="sec_filings", embedding_function=bde_embeddings)


# Initialize The OpenAI Client
llm_client = OpenAI(
    base_url=os.getenv("LLM_URL"),
    api_key=os.getenv("LLM_API_KEY")
)

def ask_question(user_question: str, ticker: str):
    logging.info("Building Keyword Serach Engine")
    all_docs = collection.get(where={"ticker": ticker})
    all_texts = all_docs['documents']
    all_ids = all_docs['ids']

    if not all_texts:
        return f" The data for **{ticker}** has been downloaded, but it hasn't been processed into the database yet. Please click 'Trigger Airflow Pipeline' to process it!"

    logging.info("Asking LLM question")

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    logging.info("keyword Engine Ready")

    # Query the Vector Database
    vector_results = collection.query(
        query_texts=[user_question], # Chroma automatically embeds
        n_results=5, # Top 3 most relevant chunks
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

        latency = round(time.time() - start_time, 2)

        # Log everything to the database
        cursor = telemetry_conn.cursor()
        cursor.execute(
            "INSERT INTO queries (user_question, llm_answer, latency_seconds) VALUES (?, ?, ?)",
            (user_question, final_answer, latency)
        )
        telemetry_conn.commit()
        logging.info(f"Telemetry Logged! Latency: {latency}s")
    
        return final_answer
    except Exception as e:
        logging.error(f"Sorry, the LLM failed: {e}")
        return f"Sorry, the LLM failed: {e}"

if __name__ == "__main__":
    ask_question("what are the key risk factors facing the company?", "")

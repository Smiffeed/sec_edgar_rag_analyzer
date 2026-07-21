import chromadb
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize ChromaDB
client = chromadb.PersistentClient(path="./chroma_db/")
collection = client.get_collection(name="sec_filings")

# Initialize The OpenAI Client
llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

def ask_question(user_question: str):
    # Query the Vector Database
    results = collection.query(
        query_texts=[user_question], # Chroma automatically embeds
        n_results=3 # Top 3 most relevant chunks
    )

    # Extract the paragraphs
    context_text="\n\n".join(results['documents'][0])

    prompt = f"""
    Context:
    {context_text}

    Question:
    {user_question}
    """

    print("Sending to LLM.")

    # Call LLM
    response = llm_client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        messages=[
            {"role": "system", "content": "You are a financial analyst. Answer the question using ONLY the provided context."},
            {"role": "user", "content": prompt}
        ]
    )

    print("\n--- LLM Answer ---")
    print(response.choices[0].message.content)

if __name__ == "__main__":
    ask_question("what are the key risk factors facing the company?")

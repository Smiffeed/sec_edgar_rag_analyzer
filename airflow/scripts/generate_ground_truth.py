import os
import json
import logging

from unstructured import documents
from openai import OpenAI
import chromadb

# Init OpenAI client
client = OpenAI(
    base_url=os.getenv("LLM_URL"),
    api_key=os.getenv("LLM_API_KEY")
)

def generate_dynamic_dataset(ticker: str):
    # Connect to chromadb
    chroma_client = chromadb.HttpClient(host="chroma", port=8000)
    collection = chroma_client.get_collection(name="sec_filings")
    chroma_results = collection.get(where={"ticker": ticker}, limit=5)

    # List of the dictionary
    documents = chroma_results['documents']
    ids = chroma_results['ids']

    generated_dataset = []

    # Through the chunks
    for doc, chunk_id in zip(documents, ids):
        # Generate a question for each chunk
        prompt = f"""
        You are an expert in financial filings and financial test writer. Based on the following chunk of a 10-K filing, your job 
        is to generate a relevant question that could be answered using ONLY this text.
        Then, provide the exact, short answer:

        TEXT:
        {doc}

        Return ONLY valid JSON object with the following structure:
        {{
            "question": "<generated question>",
            "answer": "<exact short answer>"
        }}
        """
        response = client.chat.completions.create(
            model=os.getenv("LLM_MODEL"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3 # Keep it strick
        )

        # Parse the JSON response
        try:
            qa_pair = json.loads(response.choices[0].message.content)
            # Add the document ID
            qa_pair["document_id"] = chunk_id
            generated_dataset.append(qa_pair)
        except Exception as e:
            logging.error(f"Failed to parse JSON for chunk {chunk_id}: {e}")

    with open("/opt/airflow/data/ground_truth.json", "w") as f:
        json.dump(generated_dataset, f, indent=4)
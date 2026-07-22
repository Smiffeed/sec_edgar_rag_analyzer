import chromadb
import logging
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG, 
    format="%(levelname)s - %(message)s"
)

# Connect to Database
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="sec_filings")
logging.info("Successfully conneted to database")

# Get 5 random chunks from database to gbenerate questions
size = 5
results = collection.get(limit=size)

# Connect to LLM
llm_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

ground_truth_dataset = []

for i in range(size):
    chunk_text = results['documents'][i]
    chunk_id = results['ids'][i]

    prompt = f"""
    You are a data generator. Look att this text from an SEC 10-K filing:

    {chunk_text}

        Generate one highly specific question that can be answered by this text. Return ONLY a valid JSON object in this format: {{"question": "your question", "answer": "your answer"}}
    """

    logging.info(f"Generating question for chunk {i}...")

    response = llm_client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        messages=[{"role": "user", "content": prompt}]
    )

    try:
        # choices exists check
        if not response.choices:
            print(f"API returned an empty response: {response}")
            continue

        # json.loads to turn the string back into a python dictionary
        llm_json = json.loads(response.choices[0].message.content)

        logging.debug(f"JSON Keys: {llm_json.keys()}")
        logging.debug(f"FULL Keys: {llm_json}")

        question_text = llm_json.get("question")
        answer_text = llm_json.get("answer")

        if question_text and answer_text:
            # Append to dataset
            ground_truth_dataset.append({
                "question": llm_json["question"],
                "answer": llm_json["answer"],
                "document_id": chunk_id
            })
        else:
            print(f"Skipping chunk {i}: Missing required keys.")
            logging.error(f"Skiping chunk {i}: Missing required keys.")

    except Exception as e:
        print(f"Failed to parse JSON for chunk {i}: {e}")
        logging.error(f"Failed to parse JSON for chunk {i}: {e}")

# Save the dataset to a file
with open("ground_truth.json", "w") as f:
    json.dump(ground_truth_dataset, f, indent=4)

logging.info("Successfully generated ground_truth.json")

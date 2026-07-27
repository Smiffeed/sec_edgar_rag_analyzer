import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="sec_filings")

# User Question
user_question = "What are the key risk factors facing the company?"

# Query the Vector Database
results = collection.query(
    query_texts=[user_question], # Chroma automatically embeds
    n_results=3 # Top 3 most relevant chunks
)

# Print the retrieved querY_texts
for i, document in enumerate(results['documents'][0]):
    print(f"\n--- Result {i+1} ---")
    print(document)

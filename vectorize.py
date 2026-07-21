import chromadb
from unstructured.chunking.title import chunk_by_title
from parse import parse_filing

# Get elements
elements = parse_filing("data/sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt")
batch_size = 5000

# Assuming 'elements' is the output from your partition() function
chunks = chunk_by_title(
    elements,
    max_characters=1500, # Max size of a chunk
    combine_text_under_n_chars=250 # Group tiny sentences together
)

# Initialize the client and where to save it
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create collection (like a table in SQL database
collection = chroma_client.get_or_create_collection(name="sec_filings")

documents = []
metadatas = []
ids = []

# Loop chunks
for chunk in chunks:
    documents.append(chunk.text)
    metadatas.append(chunk.metadata.to_dict())
    ids.append(chunk.id)

for i in range(0, len(documents), batch_size):
    batch_docs = documents[i:i+batch_size]
    batch_metas = metadatas[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    print(f"Uploading batch from index {i} to {i+len(batch_docs)}.")
    collection.add(
        documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
    )

# Add to ChromaDB collection
print("Done")

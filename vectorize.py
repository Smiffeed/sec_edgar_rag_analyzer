import chromadb
from unstructured.chunking.title import chunk_by_title
from parse import parse_filing

# Get elements
elements = parse_filing("data/sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt")

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

# Add to ChromaDB collection
print(f"Adding {len(documents)} chunks to ChromaDB...")
collection.add(
    documents=documents,
        metadatas=metadatas,
        ids=ids
)
print("Done")

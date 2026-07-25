import chromadb
from unstructured.chunking.title import chunk_by_title
from parse import parse_filing
import logging
import glob

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

def process_and_vectorize(ticker: str, **kwargs):
    logging.info(f"Starting vectorization for ticker: {ticker}")
    search_pattern = f"data/sec-edgar-filings/{ticker}/10-K/*/*.txt"
    found_files = glob.glob(search_pattern)

    if not found_files:
        raise FileNotFoundError(f"Could not find any 10-K files for {ticker}")

    target_file = found_files[0]

    # Get elements
    elements = parse_filing(target_file)
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
        ids.append(chunk.id)

        meta = chunk.metadata.to_dict()
        meta["ticker"] = ticker
        metadatas.append(meta)

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
    logging.info("Done vectorization")

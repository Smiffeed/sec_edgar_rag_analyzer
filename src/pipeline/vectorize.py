import glob
import logging

import chromadb
from chromadb.utils import embedding_functions
from unstructured.chunking.title import chunk_by_title

from src.pipeline.parse import parse_filing

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

def process_and_vectorize(ticker: str, **kwargs):
    logger.info(f"Starting vectorization for ticker: {ticker}")
    search_pattern = f"data/sec-edgar-filings/{ticker}/10-K/*/*.html"
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

    # Initialize the client via HTTP
    chroma_client = chromadb.HttpClient(host="chroma", port=8000)

    # Create the BAAI embedding model
    bge_embeddings = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="BAAI/bge-large-en-v1.5")

    # Create collection (like a table in SQL database)
    collection = chroma_client.get_or_create_collection(
        name="sec_filings"
    )

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
        batch_embeddings = bge_embeddings(batch_docs)
        collection.add(
            documents=batch_docs,
            embeddings=batch_embeddings,
            metadatas=batch_metas,
            ids=batch_ids
        )

    # Add to ChromaDB collection
    logger.info("Done vectorization")

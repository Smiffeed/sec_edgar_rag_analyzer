import logging
from unstructured.partition.auto import partition

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

def parse_filing(file_path: str):
    logging.info(f"Parsing file: {file_path}")

    # Partition the HTML document into semantic elements
    elements = partition(filename=file_path)

    logging.info(f"Successfully extracted {len(elements)} elements!")

    # sample 20 elements to see what unstructured found
    for i, element in enumerate(elements[:20]):
        print(f"[{type(element).__name__}] {element.text[:100]}...")

if __name__ == "__main__":
    target_file = "data/sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt"
    parse_filing(target_file)

import logging
import re
from unstructured.partition.auto import partition

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(message)s")

def clean_text (raw_text: str) -> str:
    cleaned_text = re.sub(r"<script.*?>.*?</script>", "", raw_text, flags=re.DOTALL | re.IGNORECASE)

    # Remove specifc SEC Edgar artifacts like $("products")
    cleaned_text = re.sub(r'\$\(.*?\)', '', cleaned_text)
    
    return cleaned_text


def parse_filing(file_path: str):
    logging.info(f"Parsing file: {file_path}")

    # Read the raw messy file into memory manually
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Use regex to scrub <script> tags and their contents
    logging.info("Scrubbing Javascript and HTML artifacts...")
    
    cleaned_text = clean_text(raw_text)
    
    # Partition the HTML document into semantic elements
    elements = partition(text=cleaned_text)

    logging.info(f"Successfully extracted {len(elements)} elements!")

    return elements

if __name__ == "__main__":
    target_file = "data/sec-edgar-filings/AAPL/10-K/0000320193-25-000079/full-submission.txt"
    parse_filing(target_file)

from sec_edgar_downloader import Downloader
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def download_filings(ticker: str):
    email = os.getenv("EMAIL")
    company = os.getenv("COMPANY")

    if not email or not company:
        logging.error("Missing EMAIL or COMPANY environment varialbes.")
        return

    logging.info(f"Starting download for {ticker}...")

    try:
        dl = Downloader(company, email, "data")
        dl.get("10-K", ticker, limit=1)
        logging.info(f"Successfully downloaded 10-K for {ticker}")
    except Exception as e:
        logging.error(f"Failed to download filings for {ticker}. Error: {e}")

if __name__ == "__main__":
    target_ticker = "AAPL"
    download_filings(target_ticker)

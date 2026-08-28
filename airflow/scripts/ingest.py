import logging
import os

from dotenv import load_dotenv
from sec_edgar_downloader import Downloader

from airflow.sdk.exceptions import AirflowFailException

load_dotenv()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def download_filings(ticker: str):
    email = os.getenv("EMAIL")
    company = os.getenv("COMPANY")

    if not email or not company:
        logger.error("Missing EMAIL or COMPANY environment varialbes.")
        return

    logger.info(f"Starting download for {ticker}...")

    try:
        dl = Downloader(company, email, "data")
        dl.get("10-K", ticker, limit=1, download_details=True)
        logger.info(f"Successfully downloaded 10-K for {ticker}")
    except Downloader.ValueError as e:
        logger.error(f"Failed to download filings for {ticker}. Error: {e}")
        raise AirflowFailException("Fatal Error: Do not retry this task.")

if __name__ == "__main__":
    os.environ["EMAIL"] = "your_email@example.com"
    os.environ["COMPANY"] = "project_test"
    target_ticker = "AAPL"
    download_filings(target_ticker)

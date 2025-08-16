import logging
from pathlib import Path

from aisstream.stream import AISStream

logging.basicConfig(level=logging.INFO)

# INSERT YOUR API KEY HERE
API_KEY = "<INSERT API KEY HERE>"

# Directory to store recorded data
DATA_DIR = Path("data-logs")
DATA_DIR.mkdir(parents=True, exist_ok=True)

VESSEL_CODES = Path(__file__).parent / "vessel-codes.txt"


def main():
    logging.info(
        f"Starting AIS stream with vessel codes from {VESSEL_CODES} and data directory {DATA_DIR}"
    )
    AISStream(API_KEY, VESSEL_CODES, DATA_DIR).run()


if __name__ == "__main__":
    main()

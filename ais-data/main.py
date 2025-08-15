import logging
from pathlib import Path

from aisstream.stream import AISStream

API_KEY = "<INSERT API KEY HERE>"

VESSEL_CODES = Path(__file__).parent / "vessel-codes.txt"

DATA_DIR = Path("/tmp/ais_data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


logging.basicConfig(level=logging.INFO)


def main():
    logging.info(
        f"Starting AIS stream with vessel codes from {VESSEL_CODES} and data directory {DATA_DIR}"
    )
    AISStream(API_KEY, VESSEL_CODES, DATA_DIR).run()


if __name__ == "__main__":
    main()

import logging
import sys

def configure_logging():
    # Example: log INFO and above to stdout, with a simple format
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(name)s [%(levelname)s] %(message)s"
    )

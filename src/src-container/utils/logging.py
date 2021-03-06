import os
import logging

logging.basicConfig(level=logging.DEBUG)

LOGGER = logging.getLogger("game-review-generator")

log_level = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}.get(os.environ.get("LOGGING_LEVEL", "DEBUG"))

LOGGER.setLevel(log_level or logging.DEBUG)
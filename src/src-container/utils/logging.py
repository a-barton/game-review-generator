import os
import logging

logging.basicConfig(level=logging.DEBUG)  # HACK: For some reason I need this??

LOGGER = logging.getLogger("corelogic")  # NOTE: Remove this after testing!

log_level = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
}.get(os.environ.get("LOGGING_LEVEL", "DEBUG"))

LOGGER.setLevel(log_level or logging.DEBUG)
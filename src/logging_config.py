"""JSON logging (Exercise 3.3.2). One line per event, machine-readable.
Log ids, codes and timings only: never names, emails, complaint text or .env values."""
import json
import logging
import sys
from datetime import datetime, timezone

LOGGER_NAME = "complaints_api"
SAFE_FIELDS = ("correlation_id", "method", "path", "status", "duration_ms", "error_code")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        line = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
                "level": record.levelname, "event": record.getMessage()}
        for field in SAFE_FIELDS:                       # only these fields can ever be logged
            if hasattr(record, field):
                line[field] = getattr(record, field)
        return json.dumps(line)

# TODO configure_logging(level="INFO"): one stdout handler with JsonFormatter on the 
#      LOGGER_NAME logger (add it only once), set the level, return the logger. 
# TODO get_logger(): the LOGGER_NAME logger. 


def configure_logging(level="INFO"):
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:                             # add the handler only once
        handler = logging.StreamHandler(sys.stdout)     # write to the terminal
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False                            # don't also print through Python's default logger
    return logger


def get_logger():
    return logging.getLogger(LOGGER_NAME)
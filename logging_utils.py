"""
logging_utils.py

Centralized logging utility for DMuffler, modeled after windsurf-project standards.
Provides log_info, log_warning, log_error, and logger configuration.
"""
import logging

logger = logging.getLogger("dmuffler")
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(levelname)s] %(asctime)s %(message)s")
handler.setFormatter(formatter)
if not logger.hasHandlers():
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

def log_info(msg):
    logger.info(msg)

def log_warning(msg):
    logger.warning(msg)

def log_error(msg):
    logger.error(msg)

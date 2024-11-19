import logging
import sys

logger = logging.getLogger("pytrnsys_process")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("pytrnsys_process.log")
file_handler.setLevel(logging.DEBUG)

console_format = logging.Formatter("%(levelname)s - %(message)s")
file_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.setLevel(logging.INFO)

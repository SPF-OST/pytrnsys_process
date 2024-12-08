import logging
import sys


class TracebackInfoFilter(logging.Filter):
    """Clear or restore the exception on log records
    Copied from, seems to be only solution that works
    https://stackoverflow.com/questions/54605699/python-logging-disable-stack-trace
    """

    # pylint: disable=protected-access

    def __init__(self, clear=True):  # pylint: disable=super-init-not-called
        self.clear = clear

    def filter(self, record):
        if self.clear:
            record._exc_info_hidden, record.exc_info = record.exc_info, None
            # clear the exception traceback text cache, if created.
            record.exc_text = None
        elif hasattr(record, "_exc_info_hidden"):
            record.exc_info = record._exc_info_hidden
            del record._exc_info_hidden
        return True


logger = logging.getLogger("pytrnsys_process")

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Regular log file without stacktrace
file_handler = logging.FileHandler("pytrnsys_process.log")
file_handler.setLevel(logging.INFO)

# Debug log file with stacktrace
debug_file_handler = logging.FileHandler("pytrnsys_process_debug.log")
debug_file_handler.setLevel(logging.DEBUG)

# configure formatters
console_format = logging.Formatter("%(levelname)s - %(message)s")
file_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# set formatters
console_handler.setFormatter(console_format)
file_handler.setFormatter(file_format)
debug_file_handler.setFormatter(file_format)

# add filters
console_handler.addFilter(TracebackInfoFilter())
file_handler.addFilter(TracebackInfoFilter())

# Add this handler first because the other handlers will modify the log record
logger.addHandler(debug_file_handler)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.setLevel(logging.DEBUG)

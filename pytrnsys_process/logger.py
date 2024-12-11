"""
Configures logging for the pytrnsys_process package with three outputs:
1. Console output (INFO level) - Shows basic messages without stacktrrace
2. Regular log file (INFO level) - Logs to pytrnsys_process.log without stacktrace
3. Debug log file (DEBUG level) - Logs to pytrnsys_process_debug.log with full stacktrace

The logging setup includes custom formatting for each handler and uses a TracebackInfoFilter
to control stacktrace visibility in different outputs. The main logger is configured at DEBUG
level to capture all logging events, while individual handlers control what gets displayed
in each output.

All handlers use the same log record.
Once the log record is modified and anything removed from it, will not be available in the other handlers.
"""

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

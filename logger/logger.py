import logging
from colorlog import ColoredFormatter
import sys
from queue import Queue
from typing import Optional

# Custom log level
PROGRESS = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(PROGRESS, "PROGRESS")

# Standard log format
STANDARD_LOG_FORMAT = (
    "%(log_color)s%(asctime)s [%(name)s] - %(levelname)s - %(message)s%(reset)s"
)
STANDARD_DATE_FORMAT = "%H:%M:%S"

# Add to Logger class for the new level
def progress(self, message, *args, **kwargs):
    if self.isEnabledFor(PROGRESS):
        self._log(PROGRESS, message, args, **kwargs)

def progress_complete(self, message, *args, **kwargs):
    if self.isEnabledFor(PROGRESS):
        self._log(PROGRESS, message + '\n', args, **kwargs)

logging.Logger.progress = progress
logging.Logger.progress_complete = progress_complete

# Colored log format
colored_formatter = ColoredFormatter(
    STANDARD_LOG_FORMAT,
    datefmt=STANDARD_DATE_FORMAT,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "PROGRESS": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    style="%",
)

# Custom StreamHandler for progress messages
class ProgressStreamHandler(logging.StreamHandler):
    """
    Custom stream handler for progress messages with line clearing capability.

    This handler provides special formatting for progress messages, including
    dynamic line clearing for updating progress indicators.
    """

    def emit(self, record):
        """
        Process and output a log record with special handling for progress messages.

        This method handles line clearing and formatting for progress messages
        while maintaining standard output for other message types.

        Args:
            record (LogRecord): The log record to process and output.

        Returns:
            None: Output is written directly to the stream.

        Raises:
            None: All exceptions are caught and handled internally.
        """
        try:
            msg = self.format(record)
            stream = self.stream
            
            if record.levelno == PROGRESS:
                clear_line = '\r' + ' ' * (len(msg) + 10) + '\r'
                stream.write(clear_line)
                stream.write(msg)
                stream.flush()
            else:
                if not msg.endswith('\n'):
                    msg += '\n'
                stream.write(msg)
                stream.flush()
        except Exception:
            self.handleError(record)

# Set up single console handler
console_handler = ProgressStreamHandler(sys.stdout)
console_handler.setFormatter(colored_formatter)

class ErrorReportHandler(logging.Handler):
    def __init__(self):
        super().__init__()
    
    def emit(self, record):
        # TODO send the error to the report object
        pass




def get_logger(name):
    """
    Create or retrieve a logger with consistent configuration.

    This function ensures all loggers have consistent handlers and
    respect the root logger's level settings.

    Args:
        name (str): Name of the logger to create or retrieve.

    Returns:
        Logger: Configured logger instance with appropriate handlers.

    Example:
        >>> logger = get_logger("my_module")
        >>> logger.info("This is a test message")
    """
    logger = logging.getLogger(name)
    root_level = logging.getLogger().getEffectiveLevel()
    logger.setLevel(root_level)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(ErrorReportHandler())
        
    console_handler.setLevel(root_level)
    return logger

def set_log_level(level):
    """
    Set the global logging level for all loggers.

    This function updates the log level for both the root logger and
    all existing logger instances.

    Args:
        level (Union[str, int]): Log level to set. Can be logging constant
            (e.g., logging.DEBUG) or string name ('DEBUG', 'INFO', etc.).

    Returns:
        None: Log levels are set directly on logger instances.

    Example:
        >>> set_log_level('DEBUG')
        >>> set_log_level(logging.INFO)
    """
    if isinstance(level, str):
        level = level.upper()
        level = getattr(logging, level)
    
    logging.getLogger().setLevel(level)
    
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(level)


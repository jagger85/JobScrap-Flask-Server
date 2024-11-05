import logging
from colorlog import ColoredFormatter
import sys
from queue import Queue

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

# Add a plain formatter for SSE messages
SSE_FORMAT = "%(message)s"  # Just the message without colors or timestamps
sse_formatter = logging.Formatter(SSE_FORMAT)

class SSELoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queue = Queue()

    def emit(self, record):
        try:
            # Map logging levels to message types
            level_to_type = {
                logging.DEBUG: "debug",
                logging.INFO: "info",
                PROGRESS: "progress",
                logging.WARNING: "warning",
                logging.ERROR: "error",
                logging.CRITICAL: "error",
            }

            # Create a clean message structure
            message = {
                "type": level_to_type.get(record.levelno, "info"),
                "message": record.getMessage()  # Get clean message without formatting
            }
            
            self.queue.put(message)
        except Exception:
            self.handleError(record)

    def get_message(self):
        """
        Retrieves the next message from the queue if available.
        
        Returns:
            dict: Message containing type and content, or None if queue is empty
        """
        if not self.queue.empty():
            return self.queue.get()
        return None

# Initialize SSE handler
sse_handler = SSELoggingHandler()
sse_handler.setFormatter(sse_formatter)  # Use plain formatter instead of colored

# Custom StreamHandler for progress messages
class ProgressStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            stream = self.stream
            # Also send to SSE handler
            sse_handler.emit(record)
            
            if record.levelno == PROGRESS:
                # Dynamically clear line based on message length
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
    Get or create a logger with consistent configuration.
    Args:
        name: Name of the logger
    Returns:
        Logger instance with proper configuration
    """
    logger = logging.getLogger(name)
    
    # Get the root logger's level (set by set_log_level)
    root_level = logging.getLogger().getEffectiveLevel()
    
    # Ensure this logger uses the root's level
    logger.setLevel(root_level)
    
    # Ensure single handler by removing any existing ones
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(sse_handler)
        logger.addHandler(ErrorReportHandler())
        
    # Make sure handler also respects the level
    console_handler.setLevel(root_level)
    
    return logger

def set_log_level(level):
    """
    Set the log level for all loggers in the application.
    Args:
        level: Can be logging.DEBUG, logging.INFO, logging.WARNING, 
              logging.ERROR, logging.CRITICAL or their string equivalents
    """
    if isinstance(level, str):
        level = level.upper()
        level = getattr(logging, level)
    
    # Set root logger level
    logging.getLogger().setLevel(level)
    
    # Set level for all existing loggers
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).setLevel(level)


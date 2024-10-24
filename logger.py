import logging
from colorlog import ColoredFormatter

# Custom log level
PROGRESS = 25  # Between INFO (20) and WARNING (30)
logging.addLevelName(PROGRESS, "PROGRESS")

# Standard log format
STANDARD_LOG_FORMAT = "%(log_color)s%(asctime)s [%(name)s]  - %(levelname)s - %(message)s%(reset)s"
STANDARD_DATE_FORMAT = "%H:%M:%S"

# Add to Logger class for the new level
def progress(self, message, *args, **kwargs):
    if self.isEnabledFor(PROGRESS):
        self._log(PROGRESS, message, args, **kwargs)

logging.Logger.progress = progress

# Colored log format
colored_formatter = ColoredFormatter(
    STANDARD_LOG_FORMAT,
    datefmt=STANDARD_DATE_FORMAT,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'PROGRESS': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Log handlers
console_handler = logging.StreamHandler()
console_handler.setFormatter(colored_formatter)

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    # Remove any existing handlers to prevent duplication
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    logger.addHandler(console_handler)
    return logger

# Logger instances
app_logger = get_logger('App')
linkedin_logger = get_logger('LinkedIn')
indeed_logger = get_logger('Indeed')
file_logger = get_logger('File handler')

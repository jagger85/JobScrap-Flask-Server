import logging
from queue import Queue

# Custom logging handler for Server-Sent Events (SSE)
# Captures log messages in a queue for later retrieval and streaming
class SSELoggingHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.queue = Queue()

    def emit(self, record):
        log_entry = f"{record.levelname}: {self.format(record)}"  # Include log level
        self.queue.put(log_entry)

    def get_message(self):
        if not self.queue.empty():
            return self.queue.get()
        return None

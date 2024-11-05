from enum import Enum

class MessageType(Enum):
    HEARTBEAT = "heartbeat" 
    PLATFORM_STATE = "platform_states"
    INFO = "info"
    WARNING = 'warning'
    ERROR = 'error'
    PROGRESS = 'progress'
    DEBUG = 'debug'
from enum import Enum

class MessageType(Enum):
    PLATFORM_STATE = "platform_states"
    LOG_MESSAGE = "message"
    INFO = "info"
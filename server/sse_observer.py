from constants.platforms import Platforms
from constants.platform_states import PlatformStates
from constants.message_type import MessageType

class SSEObserver:
    def __init__(self, sse_handler):
        self.sse_handler = sse_handler

    def notify_platform_state(self, platform: Platforms, new_state: PlatformStates):
        message = {
            "type": MessageType.PLATFORM_STATE.value,
            "platforms": {
                platform.value: new_state.value
            }
        }
        self.sse_handler.queue.put(message)

    def notify_message(self, message_text: str):
        message = {
            "type": MessageType.LOG_MESSAGE.value,
            "message": message_text
        }
        self.sse_handler.queue.put(message)

    def notify_info(self, info_text: str):
        message = {
            "type": MessageType.INFO.value,
            "message": info_text
        }
        self.sse_handler.queue.put(message) 
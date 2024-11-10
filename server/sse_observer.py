from constants.platforms import Platforms
from constants.platform_states import PlatformStates
from constants.message_type import MessageType
from logger.logger import get_logger

class SSEObserver:
    def __init__(self, sse_handler):
        self.sse_handler = sse_handler
        self.logger = get_logger("SSEObserver")

    def notify_platform_state(self, platform: Platforms, new_state: PlatformStates):
        """
        Notify clients about platform state changes.
        This is the only special case we need to handle separately from the logging system.
        """
        message = {
            "type": MessageType.PLATFORM_STATE.value,
            "platforms": {
                platform.value: new_state.value
            }
        }
        self.sse_handler.queue.put(message)
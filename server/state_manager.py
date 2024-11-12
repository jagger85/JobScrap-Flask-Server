from constants.platform_states import PlatformStates
from constants.platforms import Platforms
from .sse_observer import SSEObserver
from logger.logger import get_sse_handler
class StateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.platform_states = {}
            cls._instance.sse_observer = SSEObserver(get_sse_handler())
            cls._instance.initialize_platform_states()
        return cls._instance

    def initialize_platform_states(self):
        for platform in Platforms:
            self.platform_states[platform] = PlatformStates.IDLE
            self.sse_observer.notify_platform_state(platform,PlatformStates.IDLE)
            
    def set_platform_state(self, platform: Platforms, state: PlatformStates):
        self.platform_states[platform] = state
        self.sse_observer.notify_platform_state(platform, state)
    
    def get_all_states(self):
        return self.platform_states



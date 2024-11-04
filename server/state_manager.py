from constants.platform_states import PlatformStates
from constants.platforms import Platforms
from .sse_observer import SSEObserver

class StateManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.platform_states = {}
            cls._instance.observers = []
        return cls._instance
    
    def add_observer(self, observer):
        self.observers.append(observer)  # Method to add an observer

    def notify_observers(self, platform: Platforms, new_state: PlatformStates):
        for observer in self.observers:
            if isinstance(observer, SSEObserver):
                observer.notify_platform_state(platform, new_state)
            else:
                observer.update(platform, new_state)

    def set_platform_state(self, platform: Platforms, state: PlatformStates):
        if not isinstance(state, PlatformStates):
            raise ValueError("State must be a PlatformStates enum")
        self.platform_states[platform] = state
        self.notify_observers(platform, state)
        
    def get_platform_state(self, platform: Platforms):
        return self.platform_states.get(platform, PlatformStates.IDLE)
    
    def get_all_states(self):
        return self.platform_states

    def log_message(self, message):
        for observer in self.observers:
            if isinstance(observer, SSEObserver):
                observer.notify_message(message)
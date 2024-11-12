"""
Platform state management module for job scraping operations.

This module implements a singleton pattern to manage and coordinate
platform states across the application, with SSE notifications.

Classes:
    StateManager: Singleton manager for platform states.
"""

from constants.platform_states import PlatformStates
from constants.platforms import Platforms
from .sse_observer import SSEObserver
from logger.logger import get_sse_handler

class StateManager:
    """
    Singleton manager for platform states with SSE notifications.

    This class maintains the current state of each scraping platform and
    notifies observers of state changes through SSE. Implements the
    singleton pattern to ensure consistent state across the application.

    Attributes:
        _instance (StateManager): Singleton instance of the manager.
        platform_states (dict): Dictionary mapping Platforms to their current states.
        sse_observer (SSEObserver): Observer for SSE notifications.

    Example:
        >>> manager = StateManager()
        >>> manager.set_platform_state(Platforms.LINKEDIN, PlatformStates.RUNNING)
        >>> states = manager.get_all_states()
    """

    _instance = None
    
    def __new__(cls):
        """
        Create or return the singleton instance of StateManager.

        This method implements the singleton pattern, ensuring only one
        instance of StateManager exists throughout the application.

        Returns:
            StateManager: The singleton instance.

        Example:
            >>> manager1 = StateManager()
            >>> manager2 = StateManager()
            >>> assert manager1 is manager2  # Same instance
        """
        if cls._instance is None:
            cls._instance = super(StateManager, cls).__new__(cls)
            cls._instance.platform_states = {}
            cls._instance.sse_observer = SSEObserver(get_sse_handler())
            cls._instance.initialize_platform_states()
        return cls._instance

    def initialize_platform_states(self):
        """
        Initialize all platform states to IDLE.

        This method sets up the initial state for all platforms defined in
        the Platforms enum and notifies observers of the initial states.

        Returns:
            None: States are initialized internally.

        Example:
            >>> manager = StateManager()
            >>> manager.initialize_platform_states()
            >>> states = manager.get_all_states()
            >>> assert all(state == PlatformStates.IDLE for state in states.values())
        """
        for platform in Platforms:
            self.platform_states[platform] = PlatformStates.IDLE
            self.sse_observer.notify_platform_state(platform, PlatformStates.IDLE)
            
    def set_platform_state(self, platform: Platforms, state: PlatformStates):
        """
        Update the state of a specific platform.

        This method changes the state of a platform and notifies observers
        through SSE of the state change.

        Args:
            platform (Platforms): The platform to update.
            state (PlatformStates): The new state for the platform.

        Returns:
            None: State is updated internally and observers are notified.

        Example:
            >>> manager = StateManager()
            >>> manager.set_platform_state(Platforms.INDEED, PlatformStates.RUNNING)
            >>> states = manager.get_all_states()
            >>> assert states[Platforms.INDEED] == PlatformStates.RUNNING
        """
        self.platform_states[platform] = state
        self.sse_observer.notify_platform_state(platform, state)
    
    def get_all_states(self):
        """
        Retrieve the current states of all platforms.

        Returns:
            dict: Dictionary mapping Platforms to their current PlatformStates.

        Example:
            >>> manager = StateManager()
            >>> states = manager.get_all_states()
            >>> for platform, state in states.items():
            >>>     print(f"{platform.value}: {state.value}")
        """
        return self.platform_states



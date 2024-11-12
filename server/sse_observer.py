"""
Server-Sent Events (SSE) observer module for platform state notifications.

This module implements the observer pattern to notify clients about
platform state changes through SSE.

Classes:
    SSEObserver: Handles platform state change notifications via SSE.
"""

from constants.platforms import Platforms
from constants.platform_states import PlatformStates
from constants.message_type import MessageType
from logger.logger import get_logger

class SSEObserver:
    """
    Observer class for sending platform state updates via SSE.

    This class implements the observer pattern to notify connected clients
    about changes in platform states through Server-Sent Events.

    Args:
        sse_handler (SSELoggingHandler): Handler for SSE message queue management.

    Attributes:
        sse_handler (SSELoggingHandler): Handler for managing SSE messages.
        logger (Logger): Logger instance for tracking operations.

    Example:
        >>> from logger.logger import get_sse_handler
        >>> sse_handler = get_sse_handler()
        >>> observer = SSEObserver(sse_handler)
        >>> observer.notify_platform_state(Platforms.LINKEDIN, PlatformStates.RUNNING)
    """

    def __init__(self, sse_handler):
        """
        Initialize the SSE observer with a message handler.

        Args:
            sse_handler (SSELoggingHandler): Handler for SSE message queue management.
        """
        self.sse_handler = sse_handler
        self.logger = get_logger("SSEObserver")

    def notify_platform_state(self, platform: Platforms, new_state: PlatformStates):
        """
        Notify clients about platform state changes.

        This method queues a platform state update message to be sent via SSE
        to all connected clients. This is a special case handled separately
        from the general logging system.

        Args:
            platform (Platforms): The platform enum value that changed state.
            new_state (PlatformStates): The new state enum value for the platform.

        Returns:
            None: Message is queued for transmission via SSE.

        Example:
            >>> observer = SSEObserver(sse_handler)
            >>> observer.notify_platform_state(
            >>>     Platforms.JOBSTREET,
            >>>     PlatformStates.COMPLETED
            >>> )
        """
        message = {
            "type": MessageType.PLATFORM_STATE.value,
            "platforms": {
                platform.value: new_state.value
            }
        }
        self.sse_handler.queue.put(message)
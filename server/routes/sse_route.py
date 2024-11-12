from flask import Blueprint, Response, stream_with_context
from flask_jwt_extended import jwt_required
from logger.logger import get_logger, get_sse_handler
from constants.message_type import MessageType
from server.state_manager import StateManager
import json
import time

sse_bp = Blueprint('sse', __name__)

@sse_bp.route('/jobsweep-sse')
@jwt_required()
def sse_stream():
    """Stream server-sent events for job updates.

    This route establishes a connection for streaming events related to job updates.
    It sends an initial connection message and continues to stream messages from the
    SSE handler, including heartbeat messages at regular intervals.

    Returns:
        Response: A streaming response with content type 'text/event-stream'.
    """
    def event_stream():
        # Get the singleton SSE handler
        sse_handler = get_sse_handler()
        state_manager = StateManager()
        
        # Send initial connection message
        connection_message = {'type': MessageType.INFO.value, 'message': 'Connection established'}
        yield f"data: {json.dumps(connection_message)}\n\n"

        # Send current platform states
        platform_states = state_manager.get_all_states()
        platform_states_message = {'type': MessageType.PLATFORM_STATE.value, 'platforms': {k.value: v.value for k, v in platform_states.items()}}
        yield f"data: {json.dumps(platform_states_message)}\n\n"

        try:
            while True:
                message = sse_handler.get_message()
                
                if message:
                    # Messages are already properly formatted by the SSELoggingHandler
                    yield f"data: {json.dumps(message)}\n\n"
                else:
                    # Heartbeat message using the defined enum
                    yield f"data: {json.dumps({'type': MessageType.HEARTBEAT.value, 'heartbeat': True})}\n\n"
                    time.sleep(3)
                    pass
                    
        except GeneratorExit:
            logger = get_logger('sse_stream')
            logger.debug("SSE connection closed")
            pass

    return Response(
        stream_with_context(event_stream()), 
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

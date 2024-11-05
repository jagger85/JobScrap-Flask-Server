from flask import Blueprint, Response, stream_with_context
from logger.logger import get_logger
from constants.message_type import MessageType
import json
import time

sse_bp = Blueprint('sse', __name__)

@sse_bp.route('/jobsweep-sse')
def sse_stream():
    """Stream server-sent events for job updates.

    This route establishes a connection for streaming events related to job updates.
    It sends an initial connection message and continues to stream messages from the
    SSE handler, including heartbeat messages at regular intervals.

    Returns:
        Response: A streaming response with content type 'text/event-stream'.
    """
    def event_stream():
        # Get the logger and its SSE handler
        logger = get_logger('sse_stream')
        sse_handler = logger.handlers[1]  # SSE handler is the second handler
        
        # Send initial connection message
        yield f"data: {json.dumps({'type': MessageType.INFO.value, 'message': 'Connection established'})}\n\n"
        
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
                    
        except GeneratorExit:
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

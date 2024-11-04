from flask import Blueprint, Response, stream_with_context
from logger.logger import get_sse_logger
from server.state_manager import StateManager
from constants.platforms import Platforms
from constants.message_type import MessageType
import json
import time

sse_bp = Blueprint('sse', __name__)

@sse_bp.route('/jobsweep-sse')
def sse_stream():
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'message': 'Connection established', 'type': MessageType.INFO.value})}\n\n"
        
        sse_log = get_sse_logger('sse_logger')
        sse_handler = sse_log.handlers[0]
        
        try:
            while True:
                message = sse_handler.get_message()
                
                if message:
                    # If message is a string, it's a raw log message that needs to be formatted
                    if isinstance(message, str):
                        try:
                            # Try to parse as JSON first in case it's already formatted
                            data = json.loads(message)
                        except json.JSONDecodeError:
                            # If it's not JSON, it's a raw message
                            data = {
                                'type': MessageType.LOG_MESSAGE.value,
                                'message': message
                            }
                    else:
                        # If it's already a dict, use it as is
                        data = message
                    
                    yield f"data: {json.dumps(data)}\n\n"
                else:
                    # Simple heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat', 'heartbeat': True})}\n\n"
                    time.sleep(3)
                    
        except GeneratorExit:
            pass

    return Response(
        stream_with_context(event_stream()), 
        content_type='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

from flask import Blueprint, Response, stream_with_context
from logger.logger import get_sse_logger
import json
import time

sse_bp = Blueprint('sse', __name__)

@sse_bp.route('/jobsweep-sse')
def sse_stream():
    def event_stream():
        # Send initial connection message
        yield f"data: {json.dumps({'message': 'Connection established', 'type': 'info'})}\n\n"
        
        start_time = time.time()
        sse_log = get_sse_logger('sse_logger')
        sse_handler = sse_log.handlers[0]
        
        try:
            while True:
                message = sse_handler.get_message()
                current_time = time.time()
                connection_time = int(current_time - start_time)
                
                if message:
                    # Ensure message is not None/undefined before sending
                    data = {
                        'message': str(message),  # Convert to string to ensure valid JSON
                        'connection_time': connection_time,
                        'type': 'message'
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                else:
                    # Send heartbeat with type indicator
                    data = {
                        'connection_time': connection_time,
                        'type': 'heartbeat'
                    }
                    yield f"data: {json.dumps(data)}\n\n"
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

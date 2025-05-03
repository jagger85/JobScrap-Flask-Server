from flask import Blueprint
from flask_sock import Sock
from services import websocket_pubsub
from helpers import get_id_from_jwt
from services import user_model
import json
import threading
from simple_websocket.errors import ConnectionClosed

sock_bp = Blueprint('sock', __name__)
sock = None
pubsub = None

def init_sock(app):
    global sock
    sock = Sock(app)

    @sock.route('/api/socket')
    def connect(ws):
        pubsub = websocket_pubsub.pubsub()
        stop_thread = threading.Event()
        
        def redis_listener():
            try:
                while not stop_thread.is_set():
                    message = pubsub.get_message()
                    if message and message['type'] == 'message':
                        try:
                            ws.send(message['data'])
                        except ConnectionClosed:
                            stop_thread.set()
                            break
            except Exception as e:
                print(f'Redis listener error: {e}')
                stop_thread.set()
            finally:
                pubsub.unsubscribe()
        
        redis_thread = None
        try:
            while True:
                message = ws.receive()
                data = json.loads(message)

                message_type = data.get("type")
                if message_type == "login":
                    token = data.get("message")
                    user_id = get_id_from_jwt(token)
                    user_username = user_model.get_user_with_id(user_id)['username']
                    websocket_pubsub.set(f"client:{user_id}", "connected")
                    pubsub.subscribe(f"ws:client:{user_id}")
                    
                    # Start Redis listener in a separate thread
                    redis_thread = threading.Thread(target=redis_listener)
                    redis_thread.daemon = True
                    redis_thread.start()
                    
                    ws.send(json.dumps({"type":"login", "message": f"You are currently subscribed to the channel {user_id}"}))
                
                elif message_type == "echo":
                    ws.send(json.dumps({"type":"echo","message":"hey I received an echo message"}))
                
        except ConnectionClosed:
            # Handle normal connection closure
            pass
        except Exception as e:
            print(f'WebSocket error: {e}')
        finally:
            # Clean up resources
            if redis_thread and redis_thread.is_alive():
                stop_thread.set()
                redis_thread.join(timeout=1.0)
            if pubsub:
                pubsub.close()
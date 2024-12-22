from flask import Blueprint
from flask_sock import Sock
import uuid
from services import redis_client
from helpers import get_user
from services import user_model
import json
import threading
from flask import request

sock_bp = Blueprint('sock', __name__)
sock = None

def init_sock(app):
    global sock
    sock = Sock(app)

    @sock.route('/api/echo')
    def echo(ws):
        try:
            token = request.headers.get('Authorization')

            if not token:
                ws.send(json.dumps({
                    "type": "error",
                    "message": "No authorization token provided"
                }))
                return
            
            user_username = get_user(token)
            
            user_id = user_model.get_id_with_username(user_username)
            
            # Send immediate test message
            ws.send(json.dumps({
                "type": "connection_test",
                "message": "WebSocket connected successfully"
            }))
            
            redis_client.set(f"client:{user_id}", "connected")
            ws.send(json.dumps({
                "type" : "login",
                "message": f"Hello {user_username}"
            }))
            
            # Subscribe to a Redis channel for this client
            pubsub = redis_client.pubsub()
            pubsub.subscribe(f"ws:client:{user_id}")
            
            def redis_listener():
                for message in pubsub.listen():
                    if message['type'] == 'message':
                        data = message['data']
                        ws.send(data)
            
            # Start Redis listener in a separate thread
            redis_thread = threading.Thread(target=redis_listener)
            redis_thread.daemon = True
            redis_thread.start()
            
            try:
                while True:
                    # Handle WebSocket messages from client
                    data = ws.receive()
                    try:
                        message = json.loads(data)
                        print(f"Received from {user_id}: {message}")
                        if message['type'] == 'test':
                            print(f"the test message is: {message['content']}")
                        
                        # Send response back to client
                        response = {
                            "type": "response",
                            "content": f"Server received: {message['content']}"
                        }
                        ws.send(json.dumps(response))
                        
                    except json.JSONDecodeError:
                        print(f"Invalid JSON received from {user_id}: {data}")
                        ws.send(json.dumps({
                            "type": "error",
                            "content": "Invalid JSON format"
                        }))
                    
            except Exception as e:
                print(f"Connection error with client {user_id}: {e}")
            finally:
                print(f"Client {user_id} disconnected")
                redis_client.delete(f"client:{user_id}")
                pubsub.unsubscribe()
        except Exception as e:
            print(f"Error in echo function: {e}")
            ws.send(json.dumps({
                "type": "error",
                "message": "An error occurred"
            }))
from flask import Blueprint
from flask_sock import Sock
from services import websocket_pubsub
from helpers import get_id_from_jwt, get_user_from_jwt
from services import user_model
import json
import threading
from flask import request

sock_bp = Blueprint('sock', __name__)
sock = None
pubsub = None

def init_sock(app):
    global sock
    sock = Sock(app)


    @sock.route('/api/socket')
    def connect(ws):
        pubsub = websocket_pubsub.pubsub()
        
        def redis_listener():
            while True:
                message = pubsub.get_message()
                if message and message['type'] == 'message':
                    ws.send(message['data'])
        
        while True:
            try:
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
                    print("Echo message received: ", message)
                    ws.send(json.dumps({"type":"echo","message":"hey I received an echo message"}))
                
            except Exception as e:
                error_message = json.dumps({"type": "error", "message": str(e)})
                ws.send(error_message)
                print('An error occurred ', e )
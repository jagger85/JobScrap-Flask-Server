import redis
import json
from constants import environment, MessageType, PlatformStates

redis_client = redis.StrictRedis(
    host=environment["redis_host"],  
    port=int(environment["redis_port"]),  
    db=int(environment["redis_db"]),
    decode_responses=True,
)

def send_socket_message(user_id, messageType: str, message: str ):
    redis_client.publish(f"ws:client:{user_id}", json.dumps({
        "type": messageType,
        "message": message 
    }))

import redis
import json
from constants import environment, MessageType, PlatformStates
from datetime import datetime

redis_redbeat_client = redis.StrictRedis(
    host=environment["redis_host"],  
    port=int(environment["redis_port"]),  
    db=1,
    decode_responses=True,
)


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

def update_operation_status(user_id, task_id, message: str ):
    redis_client.publish(f"ws:client:{user_id}", json.dumps({
        "type": "operation_status_update",
        "task_id": task_id,
        "status": message 
    }))

def update_operation_listings_count(user_id, task_id, listings):
    redis_client.publish(f"ws:client:{user_id}", json.dumps({
        "type": "operation_listings_count_update",
        "task_id": task_id,
        "listings_count": listings 
    }))

def update_operation_info_message(user_id, task_id, message):
    redis_client.publish(f"ws:client:{user_id}", json.dumps({
        "type": "operation_info_message",
        "task_id": task_id,
        "message": message 
    }))




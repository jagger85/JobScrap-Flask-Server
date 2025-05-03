import redis
import json
from constants import environment as env

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class CeleryBroker(metaclass=Singleton):
    def __init__(self):
        self.redis = redis.StrictRedis(
            host=env["redis_host"],
            port=env["redis_port"],
            db=env["redis_celery_db"],
            decode_responses=True,
        )
    
    def __getattr__(self, name):
        return getattr(self.redis, name)

class RedBeatScheduler(metaclass=Singleton):
    def __init__(self):
        self.redis = redis.StrictRedis(
            host=env["redis_host"],
            port=env["redis_port"],
            db=env["redis_redbeat_db"],
            decode_responses=True,
        )

    def __getattr__(self, name):
        return getattr(self.redis, name)

class WebSocketPubSub(metaclass=Singleton):
    def __init__(self):
        self.redis = redis.StrictRedis(
            host=env["redis_host"],
            port=env["redis_port"],
            db=env["redis_websocket_db"],
            decode_responses=True,
        )

    def __getattr__(self, name):
        return getattr(self.redis, name)

    def send_socket_message(self, user_id, message_type: str, message: str):
        self.redis.publish(f"ws:client:{user_id}", json.dumps({
            "type": message_type,
            "message": message
        }))

    def update_operation_status(self, user_id, task_id, message: str):
        self.redis.publish(f"ws:client:{user_id}", json.dumps({
            "type": "operation_status_update",
            "task_id": task_id,
            "status": message
        }))

    def update_operation_listings_count(self, user_id, task_id, listings):
        self.redis.publish(f"ws:client:{user_id}", json.dumps({
            "type": "operation_listings_count_update",
            "task_id": task_id,
            "listings_count": listings
        }))

    def update_operation_info_message(self, user_id, task_id, message):
        self.redis.publish(f"ws:client:{user_id}", json.dumps({
            "type": "operation_info_message",
            "task_id": task_id,
            "message": message
        }))
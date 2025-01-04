from .mongo import user_model, operation_model
from .redis import WebSocketPubSub, RedBeatScheduler, CeleryBroker
from .celery_app import celery

# Initialize Redis clients
celery_broker = CeleryBroker()
redbeat_scheduler = RedBeatScheduler()
websocket_pubsub = WebSocketPubSub()
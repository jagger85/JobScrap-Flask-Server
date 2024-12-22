import redis
from constants import environment

redis_client = redis.StrictRedis(
    host= environment["redis_host"],
    port=int(environment["redis_port"]),
    db=int(environment["redis_db"]),
    decode_responses=True,
)
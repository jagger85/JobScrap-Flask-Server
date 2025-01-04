from celery import Celery
from constants import environment
from celery.schedules import crontab

def make_celery():
    celery = Celery(
        __name__,
        broker=environment["celery_broker_url"],
        backend=environment["celery_result_backend"],
    )
    
    # RedBeat Settings
    celery.conf.update(
        redbeat_redis_url=environment["redbeat_redis_url"],
        redbeat_lock_key='redbeat:lock',
        redbeat_lock_timeout=90,
    )
    
    print("RedBeat Redis URL:", environment["redbeat_redis_url"])
    
    return celery

celery = make_celery()
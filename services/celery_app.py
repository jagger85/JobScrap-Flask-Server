from celery import Celery
from constants import environment as env

def make_celery():
    celery = Celery(
        __name__,
        broker=env["celery_broker_url"],
        backend=env["celery_result_backend"],
    )
    
    # RedBeat Settings
    celery.conf.update(
        redbeat_redis_url=env["redis_redbeat_url"],
        redbeat_lock_key='redbeat:lock',
        redbeat_lock_timeout=90,
    )
        
    return celery

celery = make_celery()
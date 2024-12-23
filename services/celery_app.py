from celery import Celery
from constants import environment

def make_celery():
    celery = Celery(
        __name__,
        broker=environment["celery_broker_url"],
        backend=environment["celery_result_backend"]
    )
    return celery

celery = make_celery()
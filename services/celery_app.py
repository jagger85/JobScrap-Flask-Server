from celery import Celery
from constants import environment
from celery.schedules import crontab
from services import automated_scrap_operation_model
def make_celery():
    celery = Celery(
        __name__,
        broker=environment["celery_broker_url"],
        backend=environment["celery_result_backend"]
    )

    automated_ops = automated_scrap_operation_model.get_all_automated_scrap_operations()

    beat_schedule = {}

    for op in automated_ops:
        if op.get('active', False):
            beat_schedule[f'automated_scrap_{op["_id"]}'] = {
                'task': 'tasks.example_task',
                'schedule': crontab(minute=f'*/{op["frequency"]}'),
                'args': (op['_id'], op['username'], {
                    'platform': op['platform'],
                    'keywords': op['keywords'],
                    'dateRange': op['dateRange']
                })
            }

    celery.conf.beat_schedule = beat_schedule
    return celery

celery = make_celery()
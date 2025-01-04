celery -A services.celery_worker worker --loglevel=info  

celery -A services.celery_app.celery beat -S redbeat.RedBeatScheduler

redis-commander --redis-db 1
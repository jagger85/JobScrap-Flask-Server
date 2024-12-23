from services.celery_app import celery
from tasks.celery_tasks import kalibrr_scrap

if __name__ == "__main__":
    celery.start()



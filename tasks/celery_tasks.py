from flask import jsonify
from services.celery_app import celery
from scrappers import kalibrr, jobstreet
from constants import MessageType, PlatformStates
from services import operation_model, send_socket_message, update_operation_status, update_operation_info_message
from celery.schedules import crontab
from celery import shared_task

def _perform_scraping(user_id, user_username, data, task_id, platform):
    """Base function for Kalibrr scraping logic"""
    update_operation_status(user_id, task_id, 'Processing')
    operation_id = operation_model.create_operation({
        "user": user_username, 
        "platform": platform, 
        "time_range": data["days"], 
        "keywords": data["keywords"],
        "task_id": task_id
    })
    
    if platform == "kalibrr":   
        job_listings = kalibrr(data["days"], data["keywords"], user_id, task_id).start()
    elif platform == "jobstreet":
        job_listings = jobstreet(data["days"], data["keywords"], user_id, task_id).start()

    operation_model.set_listings(operation_id, [job.to_dict() for job in job_listings])
    operation_model.set_result(operation_id, True)
    update_operation_status(user_id, task_id, 'Completed')
    update_operation_info_message(user_id, task_id, "Operation completed")
    
    return {
        'status': 'ok',
        'message': 'Operation completed successfully',
        'operation_id': operation_id,
        'listings_count': len(job_listings)
    }


@celery.task
def kalibrr_scrap(user_id, user_username, data):
    """Triggered task for manual scraping"""
    task_id = kalibrr_scrap.request.id
    return _perform_scraping(user_id, user_username, data, task_id, "kalibrr")


@celery.task
def jobstreet_scrap(user_id, user_username, data):
    """Triggered task for manual scraping"""
    task_id = jobstreet_scrap.request.id
    return _perform_scraping(user_id, user_username, data, task_id, "jobstreet")


@celery.task(name='tasks.example_task')
def example_task(operation_id, username, data):
    """Automated scheduled task for scraping"""
    print(data)


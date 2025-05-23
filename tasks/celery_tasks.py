from flask import jsonify
from services.celery_app import celery
from scrappers import kalibrr, jobstreet
from constants import MessageType, PlatformStates
from services import operation_model
from services import websocket_pubsub
from celery.schedules import crontab
from celery import shared_task

def _perform_scraping(user_id, user_username, data, task_id, platform):
    """Base function for Kalibrr scraping logic"""
    websocket_pubsub.update_operation_status(user_id, task_id, PlatformStates.PROCESSING)
    websocket_pubsub.update_operation_info_message(user_id, task_id, "Processing your request, this may take a few minutes…")
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
    elif platform == "indeed":
        websocket_pubsub.update_operation_status(user_id, task_id, PlatformStates.ERROR)
        websocket_pubsub.update_operation_info_message(user_id, task_id, "Indeed is not supported yet")
        return {
            "status": "error",
            "message": "Indeed is not supported yet"
        }
       # job_listings = indeed(data["days"], data["keywords"], user_id, task_id).start()
    elif platform == "linkedin":
        websocket_pubsub.update_operation_status(user_id, task_id, PlatformStates.ERROR)
        websocket_pubsub.update_operation_info_message(user_id, task_id, "Linkedin is not supported yet")
        return {
            "status": "error",
            "message": "Linkedin is not supported yet"
        }
       # job_listings = linkedin(data["days"], data["keywords"], user_id, task_id).start()

    operation_model.set_listings(operation_id, [job.to_dict() for job in job_listings])
    operation_model.set_result(operation_id, True)
    websocket_pubsub.update_operation_status(user_id, task_id, PlatformStates.COMPLETED)
    websocket_pubsub.update_operation_info_message(user_id, task_id, "Operation completed")
    
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


@celery.task
def indeed_scrap(user_id, user_username, data):
    """Triggered task for manual scraping"""
    task_id = indeed_scrap.request.id
    return _perform_scraping(user_id, user_username, data, task_id, "indeed")


@celery.task
def linkedin_scrap(user_id, user_username, data):
    """Triggered task for manual scraping"""
    task_id = linkedin_scrap.request.id
    return _perform_scraping(user_id, user_username, data, task_id, "linkedin")


@shared_task
def example_task(**kwargs):
    """Scheduled task for scraping"""
    try:
        # Get operation data directly from kwargs
        platform = kwargs.get('platform')
        keywords = kwargs.get('keywords')
        date_range = kwargs.get('dateRange')
        username = kwargs.get('username')
        
        # Validate required fields
        required_fields = ['platform', 'keywords', 'dateRange', 'username']
        missing_fields = [field for field in required_fields if not kwargs.get(field)]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return "Success"
        
    except Exception as e:
        print(f"Error in example_task: {str(e)}")
        return f"Failed - {str(e)}"

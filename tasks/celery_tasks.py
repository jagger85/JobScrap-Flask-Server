from flask import jsonify
from services.celery_app import celery
from scrappers import kalibrr
from constants import MessageType, PlatformStates
from services import operation_model, send_socket_message

@celery.task
def kalibrr_scrap(user_id, user_username, data):

    send_socket_message(user_id, MessageType.PLATFORM_STATE, PlatformStates.PROCESSING)
    operation_id = operation_model.create_operation({"user": user_username, "platform": "kalibrr", "time_range": data["days"], "keywords": data["keywords"] })
    job_listings = kalibrr(data["days"],data["keywords"]).start()
    operation_model.set_listings(operation_id,[job.to_dict() for job in job_listings])
    operation_model.set_result(operation_id, True)

    return {
        'status': 'ok',
        'message': 'Lol is working'
    }

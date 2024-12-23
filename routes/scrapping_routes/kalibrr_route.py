from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middlewares import user_or_admin_required
from constants import environment
from scrappers import kalibrr_v2 as kalibrr_client
import jwt
from scrappers import kalibrr_v2
from helpers import get_user, get_id
from services import redis_client, operation_model
import json

kalibrr_bp = Blueprint("kalibrr", __name__)

@kalibrr_bp.route("/api/kalibrr", methods=["POST"])
@jwt_required()
def request_listings():
    try:
        #Retrieve the user from the jwt token
        token = request.headers.get("Authorization")
        
        user = get_user(token)
        user_id = get_id(token)

        # Publish a message to the Redis channel for the user
        redis_client.publish(f"ws:client:{user_id}", json.dumps({
            "type": "info",
            "message": "Scrapping operation started" 
        }))

        #Parse JSON data
        data = request.get_json(force=True)

        operation_id = operation_model.create_operation({"user": user, "platform": "kalibrr", "time_range": data["days"], "keywords": data["keywords"] })
        
        job_listings = kalibrr_client(data["days"],data["keywords"]).start()

        operation_model.set_listings(operation_id,[job.to_dict() for job in job_listings])
        
        operation_model.set_result(operation_id, True)

        return jsonify({
        'status': 'ok',
        'message': 'Lol is working'
    }), 200

    except Exception as e:

        return jsonify({"error": f"An unexpected error occurred   {e}"})
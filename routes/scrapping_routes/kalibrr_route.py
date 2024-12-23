from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middlewares import user_or_admin_required
from constants import environment, MessageType, PlatformStates
from scrappers import kalibrr as kalibrr_client
import jwt
from helpers import get_user, get_id
from services import operation_model, send_socket_message
import json
from tasks import kalibrr_scrap

kalibrr_bp = Blueprint("kalibrr", __name__)

@kalibrr_bp.route("/api/kalibrr", methods=["POST"])
@jwt_required()
def request_listings():
    try:
        #Parse JSON data
        data = request.get_json(force=True)
        #Retrieve the user from the jwt token
        token = request.headers.get("Authorization")
        user = get_user(token)
        user_id = get_id(token)

        result = kalibrr_scrap.delay(user_id, user, data).get(timeout=30)

        return result

    except Exception as e:

        return jsonify({"error": f"An unexpected error occurred   {e}"})
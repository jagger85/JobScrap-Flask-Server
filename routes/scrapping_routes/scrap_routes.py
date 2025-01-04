from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from middlewares import user_or_admin_required
from constants import environment, MessageType, PlatformStates
from scrappers import kalibrr as kalibrr_client
import jwt
from helpers import get_user_from_jwt, get_id_from_jwt
from services import operation_model
import json
from tasks import kalibrr_scrap, jobstreet_scrap

kalibrr_bp = Blueprint("kalibrr", __name__)
jobstreet_bp = Blueprint("jobstreet", __name__)

@kalibrr_bp.route("/api/Kalibrr", methods=["POST"])
@jwt_required()
def request_listings():
    try:
        data = request.get_json(force=True)
        token = request.headers.get("Authorization")
        user = get_user_from_jwt(token)
        user_id = get_id_from_jwt(token)
        task = kalibrr_scrap.delay(user_id, user, data)
        return jsonify({"task_id": task.id})

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred   {e}"})


@jobstreet_bp.route("/api/Jobstreet", methods=['POST'])
@jwt_required()
def request_listings():
    try:
        data = request.get_json(force=True)
        token = request.headers.get("Authorization")
        user = get_user_from_jwt(token)
        user_id = get_id_from_jwt(token)
        task = jobstreet_scrap.delay(user_id, user, data)
        return jsonify({"task_id": task.id})

    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred   {e}"})
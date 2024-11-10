from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv
logging_bp = Blueprint("logging", __name__)

@logging_bp.route("/login", methods=["POST"])
def login():
    # Get username and password from the JSON request body
    username = request.json.get("username")
    password = request.json.get("password")

    # Check for missing fields
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400
    load_dotenv()
    frontUser = os.getenv("FRONT_USER")
    frontPass = os.getenv("FRONT_PASSWORD")


    # Placeholder for verifying user credentials (replace with a database check)
    if username == frontUser and password == frontPass:
        # Generate a JWT access token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401
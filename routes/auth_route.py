"""
Authentication route module for handling user login operations.

This module provides endpoints for user authentication using JWT tokens
and environment-based credential verification.

Attributes:
    logging_bp (Blueprint): Flask Blueprint for authentication routes.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from constants import environment
from services import MongoClient
import bcrypt
logging_bp = Blueprint("logging", __name__)

@logging_bp.route("/api/login", methods=["POST"])
def login():
    """
    Handle user login requests and generate JWT tokens.

    This endpoint validates user credentials against environment variables
    and generates a JWT token for authenticated users.

    Request Body:
        JSON object containing:
            - username (str): User's username
            - password (str): User's password

    Returns:
        tuple: JSON response and HTTP status code.
            Success (200):
                {
                    "access_token": "jwt_token_string"
                }
            Missing Fields (400):
                {
                    "msg": "Missing username or password"
                }
            Invalid Credentials (401):
                {
                    "msg": "Invalid credentials"
                }

    Raises:
        None: All exceptions are handled internally.

    Example:
        >>> # Valid login request
        >>> response = requests.post('/login', json={
        >>>     'username': 'admin',
        >>>     'password': 'secret'
        >>> })
        >>> print(response.json())
        {'access_token': 'eyJ0eXAiOiJKV1QiLCJhbG...'}
    """
    # Get username and password from the JSON request body
    username = request.json.get("username")
    password = request.json.get("password")

    # Check for missing fields
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    db = MongoClient.get_db()
    user = db['Users'].find_one({"username": username})

    # Check if user exists before validating password
    if user is None:
        return jsonify({"msg": "Invalid credentials"}), 401

    is_valid_password = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
    

    if is_valid_password:
        role = user['role']
        # Generate a JWT access token
        access_token = create_access_token(identity=username, additional_claims={"role": role}, expires_delta=None)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401


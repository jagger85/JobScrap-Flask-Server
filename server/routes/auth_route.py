"""
Authentication route module for handling user login operations.

This module provides endpoints for user authentication using JWT tokens
and environment-based credential verification.

Attributes:
    logging_bp (Blueprint): Flask Blueprint for authentication routes.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
import os
from dotenv import load_dotenv

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

    load_dotenv()
    frontUser = os.getenv("FRONT_USER")
    frontPass = os.getenv("FRONT_PASSWORD")

    # Verify user credentials against environment variables
    if username == frontUser and password == frontPass:
        # Generate a JWT access token
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Invalid credentials"}), 401
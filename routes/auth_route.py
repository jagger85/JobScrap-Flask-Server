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
from services import user_model
import bcrypt
from services import user_model
from helpers import get_user_from_jwt, get_role_from_jwt, create_long_lived_jwt_token, create_short_lived_jwt_token, validate_token, get_id_from_jwt

login_bp = Blueprint("login", __name__)
@login_bp.route("/api/auth/login", methods=["POST"])
def login():

    # Get username and password from the JSON request body
    username = request.json.get("username")
    password = request.json.get("password")
    remember_me = request.json.get("remember_me")

    # Check for missing fields
    if not username or not password:
        return jsonify({"message": "Missing username or password"}), 401

    user = user_model.find_by_username(username)

    # Check if user exists before validating password
    if user is None:
        return jsonify({"message": "Invalid credentials"}), 401

    is_valid_password = bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8'))
    
    if is_valid_password:
        username = user['username']
        user_id = user_model.get_id_with_username(username)
        role = user_model.get_role_with_username(username)
        # Generate a JWT access token based on remember me 
        if remember_me:
            token = create_long_lived_jwt_token(username, role, user_id)
        else:
            token = create_short_lived_jwt_token(username, role, user_id)
            
        response_data = {
            "token": token, 
            "username": username, 
            "role": role, 
            "user_id": user_id
        }
        return jsonify(response_data), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


validate_jwt_token_bp = Blueprint("validate_jwt_login", __name__)
@validate_jwt_token_bp.route('/api/auth/validate-token', methods=["GET"])
def validate():
    token = request.headers.get("Authorization")
    
    if validate_token(token):
        username = get_user_from_jwt(token)
        role = get_role_from_jwt(token)
        user_id = get_id_from_jwt(token)
        response_data = {
            "token": token, 
            "username": username, 
            "role": role, 
            "user_id": user_id
        }
        return jsonify(response_data), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401
             
from datetime import timedelta
from flask import jsonify
from flask_jwt_extended import JWTManager
import os

# Initialize the JWTManager instance (don't bind it to app yet)
jwt = JWTManager()

def init_jwt(app):
    # Bind JWTManager to the Flask app
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30) 

    # JWT Error Handlers
    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        return jsonify({"msg": "Invalid token"}), 422

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        return jsonify({"msg": "Token has been revoked"}), 401
    
    jwt.init_app(app)

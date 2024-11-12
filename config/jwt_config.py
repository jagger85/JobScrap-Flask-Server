from datetime import timedelta
from flask import jsonify
from flask_jwt_extended import JWTManager
import os

# Initialize the JWTManager instance (don't bind it to app yet)
jwt = JWTManager()

def init_jwt(app):
    """
    Initialize and configure JWT authentication for the Flask application.

    This function sets up JWT authentication with custom configurations and
    error handlers for various JWT-related scenarios.

    Args:
        app (Flask): The Flask application instance to configure.

    Returns:
        None: JWT configuration is applied directly to the app instance.

    Example:
        >>> from flask import Flask
        >>> app = Flask(__name__)
        >>> init_jwt(app)
    """
    # Bind JWTManager to the Flask app
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default_secret_key")
    app.config["JWT_TOKEN_LOCATION"] = ["headers"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30) 

    @jwt.unauthorized_loader
    def unauthorized_response(callback):
        """
        Handle requests with missing JWT tokens.

        Args:
            callback: The error callback information from JWT.

        Returns:
            tuple: JSON response with 401 status code indicating missing authorization.
        """
        return jsonify({"msg": "Missing Authorization Header"}), 401

    @jwt.expired_token_loader
    def expired_token_response(jwt_header, jwt_payload):
        """
        Handle requests with expired JWT tokens.

        Args:
            jwt_header (dict): The JWT header information.
            jwt_payload (dict): The JWT payload information.

        Returns:
            tuple: JSON response with 401 status code indicating token expiration.
        """
        return jsonify({"msg": "Token has expired"}), 401

    @jwt.invalid_token_loader
    def invalid_token_response(callback):
        """
        Handle requests with invalid JWT tokens.

        Args:
            callback: The error callback information from JWT.

        Returns:
            tuple: JSON response with 422 status code indicating invalid token.
        """
        return jsonify({"msg": "Invalid token"}), 422

    @jwt.revoked_token_loader
    def revoked_token_response(jwt_header, jwt_payload):
        """
        Handle requests with revoked JWT tokens.

        Args:
            jwt_header (dict): The JWT header information.
            jwt_payload (dict): The JWT payload information.

        Returns:
            tuple: JSON response with 401 status code indicating revoked token.
        """
        return jsonify({"msg": "Token has been revoked"}), 401
    
    jwt.init_app(app)

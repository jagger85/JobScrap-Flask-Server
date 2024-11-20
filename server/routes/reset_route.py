"""
Reset route module for handling platform state reset operations.

This module provides endpoints for resetting all platform states to IDLE,
with JWT authentication and CORS support.

Attributes:
    reset_bp (Blueprint): Flask Blueprint for reset routes.
"""

from flask import Blueprint, jsonify, current_app
from server.state_manager import StateManager
from flask_jwt_extended import jwt_required

# Create a Blueprint for the fetch routes
reset_bp = Blueprint("reset", __name__)

# Route to handle preflight requests for CORS
@reset_bp.route("/api/reset", methods=["OPTIONS", "GET"])
@jwt_required()
def reset():
    """
    Handle platform state reset requests.

    This endpoint resets all platform states to IDLE and handles
    CORS preflight requests. Requires JWT authentication.

    Methods:
        OPTIONS: Handle CORS preflight requests
        GET: Reset all platform states

    Returns:
        tuple: JSON response and HTTP status code.
            Success (200):
                {
                    "status": "success",
                    "message": "All platform states reset to IDLE"
                }
            Error (500):
                {
                    "status": "error",
                    "message": "Error resetting platform states"
                }

    Raises:
        None: All exceptions are handled internally.

    Example:
        >>> # Reset request with valid JWT token
        >>> headers = {'Authorization': 'Bearer your_jwt_token'}
        >>> response = requests.get('/reset', headers=headers)
        >>> print(response.json())
        {'status': 'success', 'message': 'All platform states reset to IDLE'}
    """
    current_app.logger.debug("Received request for /reset")
    
    try:
        state_manager = StateManager()
        state_manager.initialize_platform_states()
        
        return jsonify({
            "status": "success",
            "message": "All platform states reset to IDLE",
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error during reset: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Error resetting platform states"
        }), 500
    
    
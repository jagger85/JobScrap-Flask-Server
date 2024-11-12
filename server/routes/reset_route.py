from flask import Blueprint, jsonify, current_app
from server.state_manager import StateManager
from flask_jwt_extended import jwt_required

# Create a Blueprint for the fetch routes
reset_bp = Blueprint("reset", __name__)

# Route to handle preflight requests for CORS
@reset_bp.route("/reset", methods=["OPTIONS", "GET"])
@jwt_required()
def reset():
    current_app.logger.debug("Received request for /reset")
    
    state_manager = StateManager()
    state_manager.initialize_platform_states()
    
    return jsonify({
        "status": "success",
        "message": "All platform states reset to IDLE",
    }), 200
    
    
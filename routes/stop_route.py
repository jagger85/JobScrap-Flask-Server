from flask import Blueprint, jsonify, current_app
from server.state_manager import StateManager
from flask_jwt_extended import jwt_required

# Create a Blueprint for the fetch routes
stop_bp = Blueprint("stop", __name__)

@stop_bp.route("/api/stop", methods=["OPTIONS", "GET"])
@jwt_required()
def stop():
    current_app.logger.debug("Received request to stop operations")

    # try:
    #     # state_manager = StateManager()
    #     # state_manager.initialize_platform_states()
    # except Exception as e:
    #     current_app.logger.error(f"Error during stop: {str(e)}")
    #     return jsonify({"status": "error", "message": "Error stopping platform"}), 500
    


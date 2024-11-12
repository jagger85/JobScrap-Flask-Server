from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from config.config import Config

# Create a Blueprint for the fetch routes
fetch_listings_bp = Blueprint("fetch_listings", __name__)

# Route to handle preflight requests for CORS
@fetch_listings_bp.route("/fetch-listings", methods=["OPTIONS", "GET"])
@jwt_required()
def listings_options():
    current_app.logger.debug("Received request for /fetch-listings")
    
    if request.method == "OPTIONS":
        response = jsonify({"message": "OK"})
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response
    
    # Handle GET request
    return get_listings()

# Keep this as a separate function but don't register it as a route
def get_listings():
    try:
        config = Config()
        listings = config.listings
        
        if listings is None:
            return jsonify({
                "message": "No listings available",
                "listings": []
            }), 404
        
        return jsonify({
            "message": "Job listings retrieved successfully",
            "listings": listings
        }), 200
        
    except Exception as e:
        current_app.logger.exception("Error retrieving listings:")
        return jsonify({
            "error": "An unexpected error occurred",
            "message": str(e)
        }), 
        

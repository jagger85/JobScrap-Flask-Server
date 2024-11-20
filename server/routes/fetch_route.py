"""
Job listings fetch route module for handling listing retrieval operations.

This module provides endpoints for retrieving job listings with JWT authentication
and CORS support.

Attributes:
    fetch_listings_bp (Blueprint): Flask Blueprint for fetch routes.
"""

from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required
from config.config import Config

# Create a Blueprint for the fetch routes
fetch_listings_bp = Blueprint("fetch_listings", __name__)

# Route to handle preflight requests for CORS
@fetch_listings_bp.route("/api/fetch-listings", methods=["OPTIONS", "GET"])
@jwt_required()
def listings_options():
    """
    Handle both OPTIONS and GET requests for job listings retrieval.

    This endpoint manages CORS preflight requests and returns job listings
    data for authenticated users.

    Methods:
        OPTIONS: Handle CORS preflight requests
        GET: Retrieve job listings

    Returns:
        tuple: JSON response and HTTP status code.
            OPTIONS Success (200):
                {
                    "message": "OK"
                }
            GET Success (200):
                {
                    "message": "Job listings retrieved successfully",
                    "listings": [list of job listings]
                }
            GET No Data (404):
                {
                    "message": "No listings available",
                    "listings": []
                }
            Error (500):
                {
                    "error": "An unexpected error occurred",
                    "message": "error details"
                }

    Raises:
        None: All exceptions are handled internally.

    Example:
        >>> # GET request with valid JWT token
        >>> headers = {'Authorization': 'Bearer your_jwt_token'}
        >>> response = requests.get('/fetch-listings', headers=headers)
        >>> print(response.json())
        {'message': 'Job listings retrieved successfully', 'listings': [...]}
    """
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
    """
    Retrieve job listings from the configuration.

    This helper function fetches job listings from the application configuration
    and formats them for response.

    Returns:
        tuple: JSON response and HTTP status code.
            Success (200):
                {
                    "message": "Job listings retrieved successfully",
                    "listings": [list of job listings]
                }
            No Data (404):
                {
                    "message": "No listings available",
                    "listings": []
                }
            Error (500):
                {
                    "error": "An unexpected error occurred",
                    "message": "error details"
                }

    Example:
        >>> response, status_code = get_listings()
        >>> if status_code == 200:
        >>>     listings = response.json['listings']
    """
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
        }), 500
        

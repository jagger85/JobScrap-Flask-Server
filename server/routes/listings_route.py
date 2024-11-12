"""
Job listings route module for handling scraping operations.

This module provides endpoints for initiating job listing scraping operations
with JWT authentication and CORS support.

Attributes:
    listings_bp (Blueprint): Flask Blueprint for listings routes.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from constants.date_range import DateRange
from server.operation import Operation as ops
from constants.platforms import Platforms

listings_bp = Blueprint("listings", __name__)

@listings_bp.route("/listings", methods=["OPTIONS"])
def listings_options():
    """
    Handle CORS preflight requests for the listings endpoint.

    This endpoint configures CORS headers to allow POST requests
    with authentication.

    Returns:
        Response: Flask response with CORS headers.
            Success (200):
                {
                    "message": "OK"
                }

    Example:
        >>> response = requests.options('/listings')
        >>> print(response.headers['Access-Control-Allow-Methods'])
        'POST, OPTIONS'
    """
    response = jsonify({"message": "OK"})
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@listings_bp.route("/listings", methods=["POST"])
@jwt_required()
def create_listing():
    """
    Initiate a new job listing scraping operation.

    This endpoint validates the request parameters and starts a scraping
    operation for the specified platforms and date range.

    Request Body:
        JSON object containing:
            - platforms (list): List of platform names to scrape
            - dateRange (str): Date range enum key for filtering

    Returns:
        tuple: JSON response and HTTP status code.
            Success (202):
                {
                    "message": "Scraping operation started successfully",
                    "status": "processing"
                }
            Missing Parameters (400):
                {
                    "error": "Missing required parameters"
                }
            Invalid Platform (400):
                {
                    "error": "Invalid platform value: {platform}"
                }
            Invalid Date Range (400):
                {
                    "error": "Invalid dateRange value"
                }
            Error (500):
                {
                    "error": "An unexpected error occurred"
                }

    Raises:
        None: All exceptions are handled internally.

    Example:
        >>> # Valid scraping request
        >>> headers = {'Authorization': 'Bearer your_jwt_token'}
        >>> data = {
        >>>     'platforms': ['linkedin', 'indeed'],
        >>>     'dateRange': 'PAST_WEEK'
        >>> }
        >>> response = requests.post('/listings', json=data, headers=headers)
        >>> print(response.json())
        {'message': 'Scraping operation started successfully', 'status': 'processing'}
    """
    try:
        # Debug logging
        raw_data = request.get_data().decode("utf-8")
        current_app.logger.debug("Raw data received: %s", raw_data)

        # Parse JSON data
        data = request.get_json(force=True)
        current_app.logger.debug("Parsed data: %s", data)

        # Validate required parameters
        if "platforms" not in data or "dateRange" not in data:
            return jsonify({"error": "Missing required parameters"}), 400

        platforms = data["platforms"]
        date_range_key = data["dateRange"]

        current_app.logger.debug("Date range key: %s", date_range_key)

        # Validate platforms is an array
        if not isinstance(platforms, list):
            return jsonify({"error": "Platforms must be an array"}), 400

        # Convert platform strings to Platform enum members
        try:
            platform_enums = [Platforms[platform.upper()] for platform in platforms]
        except KeyError as e:
            current_app.logger.error("Invalid platform value: %s", e)
            return jsonify({"error": f"Invalid platform value: {str(e)}"}), 400

        # Validate dateRange is a valid enum key
        try:
            date_range_enum = DateRange[date_range_key]
            current_app.logger.debug("Date range enum: %s", date_range_enum)
        except KeyError:
            return jsonify({"error": "Invalid dateRange value"}), 400

        # Start the operation with enum members
        scrapping_operation = ops(date_range_enum, platform_enums)
        scrapping_operation.scrape_all_sites()

        return jsonify({
            "message": "Scraping operation started successfully",
            "status": "processing"
        }), 202  # Return 202 Accepted to indicate the request was accepted for processing

    except Exception as e:
        current_app.logger.error("Exception details: %s", str(e))
        current_app.logger.exception("Traceback:")
        return jsonify({"error": "An unexpected error occurred"}), 500

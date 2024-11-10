from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from constants.date_range import DateRange
from server.operation import Operation as ops
from constants.platforms import Platforms

listings_bp = Blueprint("listings", __name__)

# Handle preflight requests (CORS)
@listings_bp.route("/listings", methods=["OPTIONS"])
def listings_options():
    response = jsonify({"message": "OK"})
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

@listings_bp.route("/listings", methods=["POST"])
@jwt_required()
def create_listing():
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
        scrapping_operation.scrape_all_sites()  # Just trigger the operation, don't return listings

        return jsonify({
            "message": "Scraping operation started successfully",
            "status": "processing"
        }), 202  # Return 202 Accepted to indicate the request was accepted for processing

    except Exception as e:
        current_app.logger.error("Exception details: %s", str(e))
        current_app.logger.exception("Traceback:")
        return jsonify({"error": "An unexpected error occurred"}), 500

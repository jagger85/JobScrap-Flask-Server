from flask import Blueprint, request, jsonify
from constants.date_range import DateRange
from server.operation import Operation as ops
from constants.platforms import Platforms
import json

listings_bp = Blueprint("listings", __name__)


@listings_bp.route("/listings", methods=["POST", "OPTIONS"])
def create_listing():
    # Handle preflight requests
    if request.method == "OPTIONS":
        response = jsonify({"message": "OK"})
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response

    try:
        # Debug logging
        raw_data = request.get_data().decode("utf-8")
        print("Raw data:", raw_data)

        # Parse JSON data
        data = request.get_json(force=True)
        print("Parsed data:", data)

        # Validate required parameters
        if "platforms" not in data or "dateRange" not in data:
            return jsonify({"error": "Missing required parameters"}), 400

        platforms = data["platforms"]
        date_range_key = data["dateRange"]

        print("Date range key:", date_range_key)
        print("Type of date range key:", type(date_range_key))

        # Validate platforms is an array
        if not isinstance(platforms, list):
            return jsonify({"error": "Platforms must be an array"}), 400

        # Convert platform strings to Platform enum members
        platform_enums = [Platforms[platform.upper()] for platform in platforms]

        # Validate dateRange is a valid enum key
        try:
            date_range_enum = DateRange[date_range_key]
            print("Date range enum:", date_range_enum)
            print("Type of date range enum:", type(date_range_enum))
            print("Date range enum value:", date_range_enum.value)
        except KeyError:
            return jsonify({"error": "Invalid dateRange value"}), 400

        # Start the operation with enum members
        scrapping_operation = ops(date_range_enum, platform_enums)
        listings = scrapping_operation.scrape_all_sites()

        return jsonify({
            "message": "Job listings retrieved successfully",
            "listings": listings  # listings is already a list of dicts, no need to convert
        }), 201

    except Exception as e:
        print("Exception details:", str(e))
        print("Exception type:", type(e))
        import traceback

        print("Traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

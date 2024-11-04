from flask import Blueprint, request, jsonify
import json
from models.date_range import DateRange

listings_bp = Blueprint('listings', __name__)

@listings_bp.route('/listings', methods=['POST', 'OPTIONS'])
def create_listing():
    # Handle preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'message': 'OK'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response

    try:
        # Debug logging
        raw_data = request.get_data().decode('utf-8')
        print("Raw data:", raw_data)
        
        # Parse JSON data
        data = request.get_json(force=True)
        print("Parsed data:", data)
        
        # Validate required parameters
        if 'platforms' not in data or 'dateRange' not in data:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        platforms = data['platforms']
        date_range_key = data['dateRange']
        
        # Validate platforms is an array
        if not isinstance(platforms, list):
            return jsonify({'error': 'Platforms must be an array'}), 400
            
        # Validate dateRange is a valid enum key
        try:
            date_range = DateRange[date_range_key].value
        except KeyError:
            return jsonify({'error': 'Invalid dateRange value'}), 400
        
        # Print the results
        print("Platforms:", platforms)
        print("Date Range:", date_range)
        
        return jsonify({
            'message': 'Listing created successfully',
            'platforms': platforms,
            'dateRange': date_range
        }), 201
        
    except Exception as e:
        print("Exception details:", str(e))
        return jsonify({'error': str(e)}), 500

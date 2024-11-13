from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)

@health_bp.route('/ping')
def ping():
    return jsonify({
        'status': 'success',
        'message': 'pong'
    }), 200

@health_bp.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running'
    }), 200

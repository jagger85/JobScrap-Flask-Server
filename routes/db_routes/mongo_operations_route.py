from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from services import operation_model
from middlewares import user_or_admin_required

operation_bp = Blueprint("operation", __name__)

@operation_bp.route("/api/operations", methods=["GET"])
@user_or_admin_required
def get_operations():
    limit = int(request.args.get('limit', 10))
    cursor = request.args.get('cursor', None)

    sort_order = request.args.get('sort', 'desc')  # Default to descending
    
    operations, next_cursor = operation_model.get_all_operations(
        limit=limit, 
        cursor=cursor,
        sort_order=sort_order
    )
    
    return jsonify({
        'operations': operations,
        'nextCursor': next_cursor,
        'limit': limit
    }), 200

@operation_bp.route("/api/operations/all", methods=["GET"])
@user_or_admin_required
def get_all_operations():
    operations = operation_model.get_all_operations()
    return jsonify(operations), 200

@operation_bp.route("/api/operations/<operation_id>", methods=["DELETE"])
@user_or_admin_required
def delete_operation(operation_id):
    operation_model.delete_operation(operation_id)
    return jsonify({"message": "Operation deleted successfully"}), 200

@operation_bp.route("/api/operations/task/<task_id>", methods=["GET"])
@user_or_admin_required
def get_operation_by_task_id(task_id):
    operation = operation_model.get_operation_by_task_id(task_id)
    if operation:
        operation['_id'] = str(operation['_id'])
        return jsonify(operation), 200
    return jsonify({"message": "Operation not found"}), 404
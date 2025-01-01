from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from services import operation_model
from middlewares import user_or_admin_required

operation_bp = Blueprint("operation", __name__)

@operation_bp.route("/api/operations", methods=["GET"])
@user_or_admin_required
def get_all_operations():
    operations = operation_model.get_all_operations()
    return jsonify(operations), 200

@operation_bp.route("/api/operations/<operation_id>", methods=["DELETE"])
@user_or_admin_required
def delete_operation(operation_id):
    operation_model.delete_operation(operation_id)
    return jsonify({"message": "Operation deleted successfully"}), 200
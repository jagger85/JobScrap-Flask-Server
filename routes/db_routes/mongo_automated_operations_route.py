from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from services import automated_scrap_operation_model
from middlewares import user_or_admin_required
from helpers import get_user_from_jwt


automated_scrap_operation_bp = Blueprint("automated_scrap_operation", __name__)

@automated_scrap_operation_bp.route("/api/automated_scrap_operations", methods=["GET"])
@user_or_admin_required
def get_all_automated_scrap_operations():
    operations = automated_scrap_operation_model.get_all_automated_scrap_operations()
    return jsonify(operations), 200

@automated_scrap_operation_bp.route("/api/automated_scrap_operations", methods=["POST"])
@user_or_admin_required
def create_automated_scrap_operation():
    data = request.get_json(force=True)
    token = request.headers.get("Authorization")
    username = get_user_from_jwt(token)
    automated_scrap_operation_model.create_automated_scrap_operation(data, username)
    return jsonify({"message": "Automated scrap operation created successfully"}), 200

@automated_scrap_operation_bp.route("/api/automated_scrap_operations/<id>", methods=["DELETE"])
@user_or_admin_required
def delete_automated_scrap_operation(id):
    automated_scrap_operation_model.delete_automated_scrap_operation(id)
    return jsonify({"message": "Automated scrap operation deleted successfully"}), 200

@automated_scrap_operation_bp.route("/api/automated_scrap_operations/<id>/activate", methods=["PUT"])
@user_or_admin_required
def activate_automated_scrap_operation(id):
    automated_scrap_operation_model.activate_automated_scrap_operation(id)
    return jsonify({"message": "Automated scrap operation activated successfully"}), 200

@automated_scrap_operation_bp.route("/api/automated_scrap_operations/<id>/deactivate", methods=["PUT"])
@user_or_admin_required
def deactivate_automated_scrap_operation(id):
    automated_scrap_operation_model.deactivate_automated_scrap_operation(id)
    return jsonify({"message": "Automated scrap operation deactivated successfully"}), 200



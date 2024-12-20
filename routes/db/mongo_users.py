from flask import Blueprint, request, jsonify
import bcrypt
from services import MongoClient
from datetime import datetime
from middlewares import admin_required

user_bp = Blueprint("user",__name__)

# Initialize MongoClient and get user_model at module level

@user_bp.route("/api/users", methods=["POST"])
@admin_required
def create_user():

    user_model = MongoClient.user_model

    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # Default role

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400    
    
    # Check if the user already exists
    if user_model.find_by_username(username):
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_model.create_user({
        "username": username,
        "password": hashed_password.decode('utf-8'),
        "role": role,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    return jsonify({"msg": "User created successfully"}), 201

@user_bp.route("/api/admin/users/<username>", methods=["DELETE"])
@admin_required
def delete_user_admin(username):

    user_model = MongoClient.user_model

    # Check if the user exists
    user = user_model.find_by_username(username)  # Store the result in 'user' variable
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user_model.delete_user(username)    
    return jsonify({"msg": "User deleted successfully"}), 200

@user_bp.route("/api/users", methods=["GET"])
@admin_required 
def get_all_users():

    user_model = MongoClient.user_model
    # Use user_model instead of direct db access for consistency
    users = user_model.get_all_users()
    return jsonify(users), 200
from flask import Blueprint, request, jsonify
import bcrypt
from services import MongoClient
from datetime import datetime
from middlewares import admin_required

user_bp = Blueprint("user",__name__)

@user_bp.route("/api/users", methods=["POST"])
@admin_required
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")  # Default role

    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    db = MongoClient.get_db()
    
    # Check if the user already exists
    if db['Users'].find_one({"username": username}):
        return jsonify({"msg": "Username already exists"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db['Users'].insert_one({
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
    db = MongoClient.get_db()
    
    # Check if the user exists
    user = db['Users'].find_one({"username": username})
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Delete the user
    db['Users'].delete_one({"username": username})
    
    return jsonify({"msg": "User deleted successfully"}), 200


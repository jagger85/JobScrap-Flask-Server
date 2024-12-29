from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import bcrypt
from services import user_model
from middlewares import admin_required, user_or_admin_required

user_bp = Blueprint("user",__name__)

# Initialize MongoClient and get user_model at module level

@user_bp.route("/api/users", methods=["POST"])
@admin_required
def create_user():

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
    })

    return jsonify({"msg": "User created successfully"}), 201

@user_bp.route("/api/users/<username>", methods=["DELETE", "OPTIONS"])
@cross_origin()  
@admin_required
def delete_user_admin(username):

    # Check if the user exists
    user = user_model.find_by_username(username)  # Store the result in 'user' variable
    if not user:
        return jsonify({"msg": "User not found"}), 404

    user_model.delete_user(username)    
    return jsonify({"msg": "User deleted successfully"}), 200

@user_bp.route("/api/users", methods=["GET"])
@admin_required 
def get_all_users():
    # Use user_model instead of direct db access for consistency
    users = user_model.get_all_users()
    return jsonify(users), 200

@user_bp.route("/api/users/<username>/change-password", methods=["PUT", "OPTIONS"])
@cross_origin()
@user_or_admin_required
def change_user_password(username):
    data = request.json
    new_password = data.get("newPassword")

    if not new_password:
        return jsonify({"msg": "New password is required"}), 400

    # Check if the user exists
    user = user_model.find_by_username(username)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    # Hash the new password
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    
    # Update the password in the database
    if user_model.update_password(username, hashed_password.decode('utf-8')):
        return jsonify({"msg": "Password updated successfully"}), 200
    else:
        return jsonify({"msg": "Failed to update password"}), 500


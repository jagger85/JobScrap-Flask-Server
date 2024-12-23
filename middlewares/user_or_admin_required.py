from functools import wraps
import jwt
from constants import environment
from constants import UserRole
from flask import request, jsonify
from helpers import get_role

def user_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"msg": "Missing token"}), 401
        
        try:
            role = get_role(token)
            # Decode the JWT token
            if role not in [UserRole.USER, UserRole.ADMIN]:
                return jsonify({"msg": "User or admin access required"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

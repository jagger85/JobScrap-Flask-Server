from functools import wraps
import jwt
from constants import environment
from constants import UserRole
from flask import request, jsonify

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"msg": "Missing token"}), 401
        
        try:
            # Assuming you have a secret key for decoding the JWT
            payload = jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])
            if payload.get("role") != UserRole.ADMIN.value:
                return jsonify({"msg": "Admin access required"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"msg": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"msg": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated_function
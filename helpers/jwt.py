import jwt
from constants import environment
from flask_jwt_extended import create_access_token
from datetime import timedelta

def get_user_from_jwt(token):
    return jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])['username']
    
def get_role_from_jwt(token):
    return jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])["role"]

def get_id_from_jwt(token):
    return jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])["id"]

def create_long_lived_jwt_token(username, role, user_id, days=30):
    return create_access_token(identity=username, additional_claims={"role": role, "username": username, "id": user_id}, expires_delta=timedelta(days=days))

def create_short_lived_jwt_token(username, role, user_id, minutes=180):
    return create_access_token(identity=username, additional_claims={"role": role, "username": username, "id": user_id}, expires_delta=timedelta(minutes=minutes))

def validate_token(token):
    try:
        # Remove 'Bearer ' if present and decode the token
        jwt.decode(token.split(" ")[1] if " " in token else token, 
                  environment["jwt_secret"], 
                  algorithms=["HS256"])
        return True
    except (jwt.InvalidTokenError, IndexError):
        return False


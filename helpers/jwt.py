import jwt
from constants import environment

def get_user(token):
    payload = jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])
    return payload['username']

def get_role(token):
    payload = jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])
    return payload['role']
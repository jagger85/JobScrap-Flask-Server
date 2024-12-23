import jwt
from constants import environment

def get_user(token):
    return jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])['username']
    
def get_role(token):
    return jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])["role"]

def get_id(token):
    return jwt.decode(token.split(" ")[1], environment["jwt_secret"], algorithms=["HS256"])["id"]
    
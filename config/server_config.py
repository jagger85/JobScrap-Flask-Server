import os
from dotenv import load_dotenv

load_dotenv()  

class ServerConfig:
    HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 10000))
    CORS_RESOURCES = {...}  # Common CORS settings

class DevelopmentConfig(ServerConfig):
    DEBUG = True
    ENV = 'development'
    CORS_RESOURCES = {
        r"/*": {  # Changed from /jobsweep-sse to /* to cover all routes
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://192.168.0.2:3000",
            ],
            "methods": ["GET", "POST"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 600
        }
    }
    
class ProductionConfig(ServerConfig):
    DEBUG = False
    ENV = 'production'
    CORS_RESOURCES = {
        r"/*": {
            "origins": [
                "http://127.0.0.1",     
                "https://127.0.0.1",
                f"http://{os.getenv('REMOTE_IP')}",      
                f"https://{os.getenv('REMOTE_IP')}",
                       
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    }
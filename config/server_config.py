from typing import Dict, Any
from constants import environment

class BaseConfig:
    """Base configuration class with common settings"""
    HOST = environment['backend_host']
    PORT = int(environment['backend_port'])
    
    # Common CORS base configuration
    CORS_BASE_CONFIG = {
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True,
    }

class DevelopmentConfig(BaseConfig):
    """Development-specific configuration"""
    DEBUG = True
    ENV = 'development'
    LOG_LEVEL = 'DEBUG'
    
    @property
    def CORS_RESOURCES(self) -> Dict[str, Any]:
        return {
            r"/*": {
                **self.CORS_BASE_CONFIG,
                "origins": [
                    "http://localhost:3000",
                    "http://127.0.0.1:3000",
                    "http://192.168.0.2:3000",
                ],
                "max_age": 600
            }
        }

class ProductionConfig(BaseConfig):
    """Production-specific configuration"""
    DEBUG = False
    ENV = 'production'
    LOG_LEVEL = 'INFO'
    
    @property
    def CORS_RESOURCES(self) -> Dict[str, Any]:
        return {
            r"/*": {
                **self.CORS_BASE_CONFIG,
                "origins": [
                    "https://127.0.0.1",
                    f"https://{environment['remote_ip']}",
                ]
            }
        }
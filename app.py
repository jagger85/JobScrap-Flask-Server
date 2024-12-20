from flask import Flask
from logger import get_logger, set_log_level
import logging
from config.jwt_config import init_jwt
from config.server_config import BaseConfig, DevelopmentConfig, ProductionConfig
from routes import register_blueprints
from flask_cors import CORS
from constants import environment
from typing import Type

def create_app() -> Flask:
    """Factory pattern for Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config_class: Type[BaseConfig] = ProductionConfig if environment['environment'] == 'production' else DevelopmentConfig
    app.config.from_object(config_class())
    
    # Initialize extensions
    CORS(app, resources=app.config['CORS_RESOURCES'])
    init_jwt(app)
    
    # Setup logging
    log = get_logger('Server')
    set_log_level(getattr(logging, app.config['LOG_LEVEL']))
    
    # Register routes and error handlers
    register_blueprints(app)
    register_error_handlers(app)
    
    return app

def register_error_handlers(app: Flask) -> None:
    """Register error handlers for the application"""
    @app.errorhandler(404)
    def page_not_found(e):
        return {"error": "Resource not found", "code": 404}, 404

    @app.errorhandler(500)
    def internal_server_error(e):
        log.error(f"Internal server error: {str(e)}")
        return {"error": "Internal server error", "code": 500}, 500

app = create_app()

if __name__ == '__main__':
    if environment['environment'] == 'development':
        app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])
    else:
        print("🚀 Production mode detected. Please use Gunicorn to run this application.")
        raise RuntimeError("Use gunicorn to run in production")

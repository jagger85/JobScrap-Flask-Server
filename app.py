from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from logger import get_logger, set_log_level
from server import sse_bp, listings_bp, logging_bp, fetch_listings_bp, health_bp
import logging
from config.jwt_config import init_jwt

# Load environment variables
load_dotenv()

# Force production mode on Render
ENV = 'production' if os.getenv('RENDER') else os.getenv('FLASK_ENV', 'development')

# Initialize logging
log = get_logger('Server')
log_level = logging.DEBUG if ENV == 'development' else logging.INFO
set_log_level(log_level)

# Flask application setup
app = Flask(__name__)

# Config class to organize settings
class Config:
    HOST = os.getenv('BACKEND_HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 10000))
    DEBUG = ENV == 'development'
    ENV = ENV
    CORS_RESOURCES = {
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    }

app.config.from_object(Config)

# Configure CORS
CORS(app, resources=app.config['CORS_RESOURCES'])

# Initialize JWT
init_jwt(app)

# Register blueprints
app.register_blueprint(health_bp)
app.register_blueprint(fetch_listings_bp)
app.register_blueprint(logging_bp)
app.register_blueprint(listings_bp)
app.register_blueprint(sse_bp)

# Error handling for common errors
@app.errorhandler(404)
def page_not_found(e):
    return {"error": "Resource not found"}, 404

@app.errorhandler(500)
def internal_server_error(e):
    return {"error": "Internal server error"}, 500

# Log registered routes in development
if ENV == 'development':
    def log_routes():
        log.debug("Registered routes:")
        for rule in app.url_map.iter_rules():
            log.debug(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")
    log_routes()

if __name__ == '__main__':
    if ENV == 'development':
        app.run(host=Config.HOST, port=Config.PORT, debug=True)
    else:
        print("🚀 Production mode detected. Please use Gunicorn to run this application.")
        raise RuntimeError("Use gunicorn to run in production")

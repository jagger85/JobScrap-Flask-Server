from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from logger import get_logger, set_log_level
from server import sse_bp,listings_bp,logging_bp,fetch_listings_bp,health_bp
import logging
from config.jwt_config import init_jwt

log = get_logger('Server')
set_log_level(logging.DEBUG)
load_dotenv()

# Force production mode when on Render
ENV = 'production' if os.getenv('RENDER') else os.getenv('FLASK_ENV', 'development')
DEBUG = False  # Explicitly disable debug mode

app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Configuration
app.config.update(
    ENV=ENV,
    DEBUG=DEBUG,
    HOST=os.getenv('BACKEND_HOST', '0.0.0.0'),
    PORT=int(os.getenv('PORT', 10000))
)

# Initialize JWT
init_jwt(app)

# Register Blueprints
app.register_blueprint(health_bp)
app.register_blueprint(fetch_listings_bp)
app.register_blueprint(logging_bp)
app.register_blueprint(listings_bp)
app.register_blueprint(sse_bp)

def log_routes():
    log.debug("Registered routes:")
    for rule in app.url_map.iter_rules():
        log.debug(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

# Add this at the bottom of the file
if __name__ == '__main__':
    # This block should never execute on Render
    if ENV == 'development':
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=True
        )
    else:
        print("🚀 Production mode detected. Please use Gunicorn to run this application.")
        raise RuntimeError("Use gunicorn to run in production")

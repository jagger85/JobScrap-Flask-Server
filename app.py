from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from logger import get_logger, set_log_level
from server import sse_bp,listings_bp,logging_bp,fetch_listings_bp
import logging
from werkzeug.serving import WSGIRequestHandler, BaseWSGIServer
from config.jwt_config import init_jwt

log = get_logger('Server')
set_log_level(logging.DEBUG)
load_dotenv()

# Validate environment variables
required_env_vars = ['BACKEND_HOST', 'BACKEND_PORT']
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

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
    HOST=os.getenv('BACKEND_HOST'),
    PORT=int(os.getenv('BACKEND_PORT'))
)

# Initialize JWT
init_jwt(app)

# Register Blueprints
app.register_blueprint(sse_bp)
app.register_blueprint(listings_bp)
app.register_blueprint(logging_bp)
app.register_blueprint(fetch_listings_bp)

# Custom request handler for better error handling
class CustomRequestHandler(WSGIRequestHandler):
    def handle_error(self, request, client_address):
        log.error(f"Error handling request from {client_address}: {request}")
        pass  # Prevent server crash on SSL errors

# Increase server timeout
BaseWSGIServer.timeout = 60  # 60 seconds timeout

def log_routes():
    log.debug("Registered routes:")
    for rule in app.url_map.iter_rules():
        log.debug(f"{rule.endpoint}: {rule.rule} [{', '.join(rule.methods)}]")

if __name__ == '__main__':
    try:
        log.debug("=== Starting Flask Server ===")
        log.debug(f"Host: {app.config['HOST']}")
        log.debug(f"Port: {app.config['PORT']}")
        
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            debug=True
        )
    except Exception as e:
        log.error(f"Failed to start server: {str(e)}")
        log.exception("Detailed traceback:")
        raise

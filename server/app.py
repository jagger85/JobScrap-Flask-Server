from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from logger.logger import get_logger, set_log_level
from routes.sse_route import sse_bp
from routes.listings_route import listings_bp
import logging
from werkzeug.serving import WSGIRequestHandler, BaseWSGIServer
import ssl

log = get_logger('Server')
set_log_level(logging.DEBUG)
load_dotenv()

# Validate environment variables
required_env_vars = ['BACKEND_HOST', 'BACKEND_PORT', 'KEY_PATH', 'CERT_PATH']
for var in required_env_vars:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

app = Flask(__name__)

# Configure CORS with SSL support
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
    PORT=int(os.getenv('BACKEND_PORT')),
    KEY_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', os.getenv('KEY_PATH'))),
    CERT_PATH=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', os.getenv('CERT_PATH'))),
    # Add SSL-specific configurations
    SESSION_COOKIE_SECURE=True,
    REMEMBER_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True
)

# Verify that the key and cert files exist
if not os.path.exists(app.config['KEY_PATH']):
    raise FileNotFoundError(f"SSL key file not found: {app.config['KEY_PATH']}")
if not os.path.exists(app.config['CERT_PATH']):
    raise FileNotFoundError(f"SSL certificate file not found: {app.config['CERT_PATH']}")

# Register Blueprints
app.register_blueprint(sse_bp)
app.register_blueprint(listings_bp)

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

def init_ssl_context():
    """Initialize and verify SSL configuration"""
    log.info("=== SSL Configuration ===")
    log.info(f"KEY_PATH: {app.config['KEY_PATH']}")
    log.info(f"CERT_PATH: {app.config['CERT_PATH']}")
    
    # Verify certificate files exist and are readable
    if not os.path.exists(app.config['KEY_PATH']):
        log.error(f"SSL key file not found at: {app.config['KEY_PATH']}")
        raise FileNotFoundError("SSL key file not found")
    log.info("✓ SSL key file found")
        
    if not os.path.exists(app.config['CERT_PATH']):
        log.error(f"SSL certificate file not found at: {app.config['CERT_PATH']}")
        raise FileNotFoundError("SSL certificate file not found")
    log.info("✓ SSL certificate file found")
    
    # Log server configuration
    log.info("=== Server Configuration ===")
    log.info(f"Host: {app.config['HOST']}")
    log.info(f"Port: {app.config['PORT']}")
    log_routes()

# Move initialization code here, after app creation but before first request
init_ssl_context()

if __name__ == '__main__':
    try:
        log.info("=== Starting Flask Server ===")
        log.info(f"Host: {app.config['HOST']}")
        log.info(f"Port: {app.config['PORT']}")
        
        # Verify SSL files
        log.info("Checking SSL certificates...")
        if not os.path.exists(app.config['CERT_PATH']):
            raise FileNotFoundError(f"SSL certificate not found at: {app.config['CERT_PATH']}")
        if not os.path.exists(app.config['KEY_PATH']):
            raise FileNotFoundError(f"SSL key not found at: {app.config['KEY_PATH']}")
        log.info("✓ SSL certificates found")
        
        # Create SSL context
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(
            certfile=app.config['CERT_PATH'],
            keyfile=app.config['KEY_PATH']
        )
        log.info("✓ SSL context created successfully")
        
        app.run(
            host=app.config['HOST'],
            port=app.config['PORT'],
            ssl_context=ssl_context,
            debug=True
        )
    except Exception as e:
        log.error(f"Failed to start server: {str(e)}")
        log.exception("Detailed traceback:")
        raise

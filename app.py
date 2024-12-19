from flask import Flask
from logger import get_logger, set_log_level
import logging
from config.jwt_config import init_jwt
from config.server_config import ServerConfig
from server.routes.app_blueprints import register_blueprints
from flask_cors import CORS
from constants import environment

# Flask application setup
app = Flask(__name__)
ENV = environment['environment']
app.config['DEBUG'] = environment['flask_debug']

if ENV == 'production':
    app.config.from_object('config.server_config.ProductionConfig')
else:
    app.config.from_object('config.server_config.DevelopmentConfig')

# Initialize CORS before routes
CORS(app, resources=app.config.get('CORS_RESOURCES'))

# Initialize logging
log = get_logger('Server')
log_level = logging.DEBUG if ENV == 'development' else logging.DEBUG
set_log_level(log_level)


# Initialize JWT
init_jwt(app)

# Register blueprints
register_blueprints(app)

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
        app.run(host=ServerConfig.HOST, port=ServerConfig.PORT, debug=True)
    else:
        print("🚀 Production mode detected. Please use Gunicorn to run this application.")
        raise RuntimeError("Use gunicorn to run in production")

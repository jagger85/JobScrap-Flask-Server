from .sse_route import sse_bp
from .listings_route import listings_bp
from .auth_route import logging_bp
from .health_route import health_bp
from .reset_route import reset_bp
from .db_routes import user_bp
from .scrapping_routes import kalibrr_bp

routes = [ sse_bp, listings_bp, logging_bp,
health_bp, reset_bp, user_bp, kalibrr_bp]

def register_blueprints(app):
    for route in routes:
        app.register_blueprint(route)
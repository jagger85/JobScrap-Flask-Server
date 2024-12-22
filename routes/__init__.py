from server import stop_bp, sse_bp, listings_bp, logging_bp, fetch_listings_bp, health_bp, reset_bp
from .db import user_bp

routes = [ sse_bp, listings_bp, logging_bp,
health_bp, reset_bp, user_bp, kalibrr_bp]

def register_blueprints(app):
    blueprints = [
        sse_bp,
        listings_bp,
        logging_bp,
        fetch_listings_bp,
        health_bp,
        reset_bp,
        stop_bp
    ]
    for blueprint in blueprints:
        app.register_blueprint(blueprint)
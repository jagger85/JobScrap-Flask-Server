from server import sse_bp, listings_bp, logging_bp, fetch_listings_bp, health_bp

def register_blueprints(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(fetch_listings_bp)
    app.register_blueprint(logging_bp)
    app.register_blueprint(listings_bp)
    app.register_blueprint(sse_bp)
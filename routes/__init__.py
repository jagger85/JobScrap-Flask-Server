from .auth_route import logging_bp
from .health_route import health_bp
from .db_routes import user_bp
from .scrapping_routes import kalibrr_bp
from .sock_route import sock_bp, init_sock

routes = [ logging_bp,
health_bp, user_bp, kalibrr_bp,
sock_bp]

def register_blueprints(app):
    for route in routes:
        app.register_blueprint(route)
    init_sock(app)
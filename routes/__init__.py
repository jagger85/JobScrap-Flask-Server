from .auth_route import login_bp, validate_jwt_token_bp
from .health_route import health_bp
from .db_routes import user_bp, operation_bp
from .scrapping_routes import kalibrr_bp, jobstreet_bp
from .sock_route import sock_bp, init_sock

routes = [ login_bp, validate_jwt_token_bp, health_bp, user_bp, operation_bp, kalibrr_bp, jobstreet_bp, sock_bp]

def register_blueprints(app):
    for route in routes:
        app.register_blueprint(route)
    init_sock(app)

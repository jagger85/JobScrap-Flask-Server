from .auth_route import auth_bp
from .health_route import health_bp
from .db_routes import user_bp, operation_bp, automated_scrap_operation_bp
from .scrapping_routes import kalibrr_bp, jobstreet_bp, linkedin_bp, indeed_bp
from .sock_route import sock_bp, init_sock

routes = [ auth_bp, health_bp, user_bp, operation_bp, automated_scrap_operation_bp, kalibrr_bp, jobstreet_bp, linkedin_bp, indeed_bp, sock_bp]

def register_blueprints(app):
    for route in routes:
        app.register_blueprint(route)
    init_sock(app)

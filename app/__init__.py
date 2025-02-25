# app/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)

    from .connect import close_db
    from .routes import app_routes  # Import the routes blueprint

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        close_db()

    app.register_blueprint(app_routes)  # Register the blueprint

    return app

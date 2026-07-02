"""
Flask Application Factory
"""
import importlib
import os
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from app.config import config
from app.models import db


def create_app(config_name=None):
    """Create and configure Flask application."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    if config_name not in config:
        config_name = "development"

    # Direct template configurations outward to your root folders
    app = Flask(
        __name__,
        template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
        static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    )
    
    app.config.from_object(config[config_name])

    # Safeguard default session setting
    if not app.config.get("SESSION_TYPE"):
        app.config["SESSION_TYPE"] = "filesystem"

    # Initialize extensions
    db.init_app(app)
    CORS(app, supports_credentials=True)
    Session(app)

    # Import blueprints lazily to avoid circular import issues
    routes_module = importlib.import_module("app.routes")
    api = routes_module.api
    pages = routes_module.pages

    # Register blueprints safely
    app.register_blueprint(api)
    app.register_blueprint(pages)

    # Initialize tables and inject default admin account safely
    with app.app_context():
        db.create_all()

        from app.models import User
        hr_user = User.query.filter_by(username="hr@portal.com").first()
        if not hr_user:
            hr_user = User(
                username="hr@portal.com",
                full_name="HR Administrator",
                mobile_number="9999999999",
                employee_id="HR001",
                role="HR",
                is_active=True
            )
            hr_user.set_password("hrpass123")
            db.session.add(hr_user)
            db.session.commit()
            print("✓ Default HR account created: hr@portal.com / hrpass123")

    return app
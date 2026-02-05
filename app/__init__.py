
from flask import Flask
from config import Config

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for Next.js frontend
    from flask_cors import CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Initialize extensions here if any exist later

    # Register Blueprints
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app

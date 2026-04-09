from flask import Flask

from app.config import Config
from app.services.data_loader import validate_core_data


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    validate_core_data()

    from app.routes.blocks import blocks_bp
    from app.routes.days import days_bp
    from app.routes.exports import exports_bp
    from app.routes.library import library_bp
    from app.routes.main import main_bp
    from app.routes.weeks import weeks_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(days_bp)
    app.register_blueprint(weeks_bp)
    app.register_blueprint(blocks_bp)
    app.register_blueprint(exports_bp)
    app.register_blueprint(library_bp)

    return app

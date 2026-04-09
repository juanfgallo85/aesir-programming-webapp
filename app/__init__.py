import os

from flask import Flask, url_for

from app.config import Config
from app.services.data_loader import validate_core_data


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    validate_core_data()

    @app.context_processor
    def inject_asset_url():
        def asset_url(filename: str) -> str:
            normalized = filename.lstrip("/")
            if os.environ.get("VERCEL"):
                return f"/{normalized}"
            return url_for("static", filename=normalized)

        return {"asset_url": asset_url}

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

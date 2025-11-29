"""Flask application factory with modular routers."""
from __future__ import annotations

import logging

import swisseph as swe
from flask import Flask
from flask_cors import CORS

from app.core.config import settings
from app.core.logging import configure_logging
from app.routers.charts import charts_bp
from app.routers.chat import chat_bp
from app.routers.health import health_bp
from app.routers.interpretation import interpretation_bp
from app.routers.profile import profile_bp
from app.routers.user import user_bp

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    configure_logging(settings.log_level)
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    CORS(
        app,
        origins=settings.allowed_origins,
        supports_credentials=settings.cors_supports_credentials,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "OPTIONS"],
    )

    try:
        swe.set_ephe_path(settings.swisseph_path)
        logger.info("Swiss Ephemeris path set to %s", settings.swisseph_path)
    except Exception as exc:  # pragma: no cover - environment specific
        logger.error("Failed to set Swiss Ephemeris path: %s", exc)

    app.register_blueprint(health_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(charts_bp)
    app.register_blueprint(interpretation_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(profile_bp)

    return app


app = create_app()

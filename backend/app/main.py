"""FastAPI application factory with modular routers."""
from __future__ import annotations

import logging

import swisseph as swe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging
from app.routers import charts, chat, health, interpretation, profile, story, synastry, user

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    configure_logging(settings.log_level)
    app = FastAPI(title="Astrologi-AI API", debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=settings.cors_supports_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    try:
        swe.set_ephe_path(settings.swisseph_path)
        logger.info("Swiss Ephemeris path set to %s", settings.swisseph_path)
    except Exception as exc:  # pragma: no cover - environment specific
        logger.error("Failed to set Swiss Ephemeris path: %s", exc)

    app.include_router(health.router)
    app.include_router(user.router)
    app.include_router(charts.router)
    app.include_router(interpretation.router)
    app.include_router(chat.router)
    app.include_router(profile.router)
    app.include_router(story.router)
    app.include_router(synastry.router)

    return app


app = create_app()

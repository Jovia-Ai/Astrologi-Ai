"""FastAPI application factory with modular routers."""
from __future__ import annotations

import logging

import swisseph as swe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import transits as transits_route_module
from app.api.routes.natal_interpretation import router as natal_interpretation_router
from app.api.routes.home import router as home_router
from app.api.routes.sky import router as sky_router
from app.api.routes.transits import router as transits_router
from app.core.config import settings
from app.core.ephemeris_guard import assert_ephemeris_ready
from app.forum.forum_router import router as forum_router
from app.core.logging import configure_logging
from app.routers import charts, chat, health, profile, revenuecat, story, synastry, user

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

    # Hard guard: refuse to start when ephemeris files are missing.
    # `assert_ephemeris_ready` raises EphemerisMissingError with an actionable
    # message pointing at `backend/scripts/setup_ephemeris.sh`. We deliberately
    # let it propagate — silent fallback corrupts natal/transit math.
    assert_ephemeris_ready(settings.swisseph_path)
    swe.set_ephe_path(settings.swisseph_path)
    logger.info("Swiss Ephemeris path set to %s", settings.swisseph_path)

    @app.on_event("startup")
    def _prewarm_transit_runtime_assets() -> None:
        transits_route_module.prewarm_transit_runtime_assets()

    app.include_router(health.router)
    app.include_router(user.router)
    app.include_router(charts.router)
    app.include_router(natal_interpretation_router)
    app.include_router(home_router)
    app.include_router(transits_router)
    app.include_router(sky_router)
    app.include_router(chat.router)
    app.include_router(revenuecat.router)
    app.include_router(profile.router)
    app.include_router(story.router)
    app.include_router(synastry.router)
    app.include_router(forum_router)

    return app


app = create_app()

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth as auth_router
from app.api.v1 import health as health_router
from app.api.v1 import timeseries as timeseries_router
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine
from app.models import TimeseriesRequest, User  # noqa: F401  (register metadata)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Base.metadata.create_all(bind=engine)

    app.include_router(health_router.router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router.router)
    app.include_router(timeseries_router.router, prefix=settings.api_v1_prefix)

    return app


app = create_app()

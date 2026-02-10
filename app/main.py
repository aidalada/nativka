from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.init_indexes import init_indexes
from app.db.mongodb import get_database


def create_app() -> FastAPI:
    app = FastAPI(
        title="SwiftEats Backend",
        version="1.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    async def _startup() -> None:
        db = get_database()
        await init_indexes(db)

    return app


app = create_app()


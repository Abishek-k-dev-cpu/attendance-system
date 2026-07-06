import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.api import api_router
from app.database import close_mongodb_connection, connect_to_mongodb, get_database, ping_database
from app.database.config import get_settings
from app.schemas import HealthResponse
from app.services import ensure_default_settings
from app.utils import AppException, setup_logging
from app.utils.exceptions import app_exception_handler, http_exception_handler, unhandled_exception_handler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)

    await connect_to_mongodb()
    await ensure_default_settings(get_database())

    yield

    await close_mongodb_connection()
    logger.info("Shutting down %s", settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Production-ready Attendance Management API backed by MongoDB Atlas. "
            "Track student attendance across subjects with bulk Excel/CSV upload support."
        ),
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(AppException, app_exception_handler)
    application.add_exception_handler(Exception, unhandled_exception_handler)

    from fastapi import HTTPException

    application.add_exception_handler(HTTPException, http_exception_handler)

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = []
        for error in exc.errors():
            loc = " → ".join(str(part) for part in error.get("loc", []))
            errors.append(f"{loc}: {error.get('msg', 'Invalid value')}")
        return JSONResponse(
            status_code=422,
            content={"detail": errors[0] if len(errors) == 1 else errors},
        )

    application.include_router(api_router)

    @application.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health_check() -> HealthResponse:
        db_ok = await ping_database()
        return HealthResponse(
            status="ok" if db_ok else "degraded",
            database="connected" if db_ok else "disconnected",
        )

    return application


app = create_app()

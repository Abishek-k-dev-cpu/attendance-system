import logging
from collections.abc import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import OperationFailure

from app.database.config import get_settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_to_mongodb() -> None:
    global _client, _database

    settings = get_settings()
    logger.info("Connecting to MongoDB database '%s'", settings.database_name)

    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _database = _client[settings.database_name]

    try:
        await _client.admin.command("ping")
    except OperationFailure as exc:
        if exc.code == 8000 or "authentication failed" in str(exc).lower():
            logger.error(
                "MongoDB authentication failed. Check MONGODB_URI on Render: "
                "use the Database Access username/password (not your Atlas login), "
                "URL-encode special characters in the password, and redeploy."
            )
        raise

    await _ensure_indexes()
    logger.info("MongoDB connection established")


async def close_mongodb_connection() -> None:
    global _client, _database

    if _client is not None:
        _client.close()
        logger.info("MongoDB connection closed")

    _client = None
    _database = None


async def _ensure_indexes() -> None:
    if _database is None:
        return

    await _database.students.create_index("register_number", unique=True)
    await _database.students.create_index("attendance.subject_code")
    await _database.attendance_uploads.create_index("upload_time")
    await _database.announcements.create_index("date")
    logger.info("MongoDB indexes ensured")


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("MongoDB is not connected. Call connect_to_mongodb() first.")
    return _database


async def ping_database() -> bool:
    if _client is None:
        return False
    try:
        await _client.admin.command("ping")
        return True
    except Exception as exc:
        logger.error("MongoDB ping failed: %s", exc)
        return False


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    yield get_database()

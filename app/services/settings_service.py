from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase


async def ensure_default_settings(db: AsyncIOMotorDatabase) -> None:
    existing = await db.settings.find_one({"_id": "global"})
    if existing:
        return

    await db.settings.insert_one(
        {
            "_id": "global",
            "minimum_attendance": 75,
            "semester": "6",
            "academic_year": "2025-2026",
            "updated_at": datetime.now(UTC),
        }
    )

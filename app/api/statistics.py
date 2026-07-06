from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas import StatisticsResponse
from app.services import StatisticsService

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get(
    "",
    response_model=StatisticsResponse,
    summary="Attendance statistics",
    description="Returns average attendance, students below 75%, top 10, lowest attendance, and total students.",
)
async def get_statistics(db: AsyncIOMotorDatabase = Depends(get_db)) -> StatisticsResponse:
    service = StatisticsService(db)
    return await service.get_statistics()

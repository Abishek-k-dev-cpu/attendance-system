from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas import StudentListResponse
from app.services import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.get(
    "",
    response_model=StudentListResponse,
    summary="List all students",
    description="Returns all students with their overall attendance percentage.",
)
async def list_students(db: AsyncIOMotorDatabase = Depends(get_db)) -> StudentListResponse:
    service = StudentService(db)
    return await service.get_all_students()

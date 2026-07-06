from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas import StudentDetailResponse
from app.services import StudentService

router = APIRouter(prefix="/student", tags=["Student"])


@router.get(
    "/{register_number}",
    response_model=StudentDetailResponse,
    summary="Get student attendance details",
    description="Returns student profile, overall attendance, subject-wise breakdown, and last updated timestamp.",
)
async def get_student(
    register_number: str,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> StudentDetailResponse:
    service = StudentService(db)
    return await service.get_student_detail(register_number)

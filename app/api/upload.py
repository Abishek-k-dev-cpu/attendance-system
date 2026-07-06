from fastapi import APIRouter, Depends, File, UploadFile
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.schemas import UploadSummaryResponse
from app.services import UploadService

router = APIRouter(tags=["Upload"])


@router.post(
    "/upload",
    response_model=UploadSummaryResponse,
    summary="Upload attendance file",
    description="Upload an Excel (.xlsx, .xls) or CSV file to update student and attendance records.",
)
async def upload_attendance(
    file: UploadFile = File(..., description="Excel or CSV attendance file"),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UploadSummaryResponse:
    content = await file.read()
    filename = file.filename or "upload.csv"
    service = UploadService(db)
    return await service.process_upload(filename, content)

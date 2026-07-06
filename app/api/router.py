from fastapi import APIRouter

from app.api.statistics import router as statistics_router
from app.api.student import router as student_router
from app.api.students import router as students_router
from app.api.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(student_router)
api_router.include_router(students_router)
api_router.include_router(upload_router)
api_router.include_router(statistics_router)

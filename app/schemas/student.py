from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SubjectAttendanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject_code: str
    subject_name: str
    classes_conducted: int
    classes_attended: int
    percentage: float


class OverallAttendanceSchema(BaseModel):
    classes_conducted: int
    classes_attended: int
    percentage: float


class StudentDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    register_number: str
    name: str
    department: str
    year: str
    section: str
    semester: str
    photo: str | None = None
    overall_attendance: OverallAttendanceSchema
    subject_wise_attendance: list[SubjectAttendanceSchema]
    last_updated: datetime | None = None


class StudentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    register_number: str
    name: str
    department: str
    year: str
    section: str
    semester: str
    photo: str | None = None
    overall_percentage: float = Field(description="Overall attendance percentage across all subjects")


class StudentListResponse(BaseModel):
    total: int
    students: list[StudentListItem]

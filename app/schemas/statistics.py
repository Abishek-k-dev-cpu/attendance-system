from pydantic import BaseModel, Field


class StudentAttendanceRank(BaseModel):
    register_number: str
    name: str
    percentage: float


class StatisticsResponse(BaseModel):
    average_attendance: float = Field(description="Average overall attendance across all students")
    students_below_75: list[StudentAttendanceRank]
    top_10_attendance: list[StudentAttendanceRank]
    lowest_attendance: list[StudentAttendanceRank]
    total_students: int = Field(description="Total number of students in the database")

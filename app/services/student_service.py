from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas import (
    OverallAttendanceSchema,
    StudentDetailResponse,
    StudentListItem,
    StudentListResponse,
    SubjectAttendanceSchema,
)
from app.utils import NotFoundError, validate_register_number
from app.utils.attendance import compute_overall_from_attendance
from app.utils.sanitize import sanitize_text


class StudentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.students

    async def get_student_detail(self, register_number: str) -> StudentDetailResponse:
        reg_no = validate_register_number(register_number)
        student = await self.collection.find_one({"register_number": reg_no})
        if not student:
            raise NotFoundError(f"Student with register number '{reg_no}' not found.")

        attendance = student.get("attendance", [])
        overall_pct, total_conducted, total_attended = compute_overall_from_attendance(attendance)

        subject_wise = [
            SubjectAttendanceSchema(
                subject_code=item["subject_code"],
                subject_name=item["subject_name"],
                classes_conducted=item["classes_conducted"],
                classes_attended=item["classes_attended"],
                percentage=item["percentage"],
            )
            for item in sorted(attendance, key=lambda x: x["subject_code"])
        ]

        return StudentDetailResponse(
            register_number=student["register_number"],
            name=student["name"],
            department=student["department"],
            year=student["year"],
            section=student["section"],
            semester=student["semester"],
            photo=student.get("photo"),
            overall_attendance=OverallAttendanceSchema(
                classes_conducted=total_conducted,
                classes_attended=total_attended,
                percentage=overall_pct,
            ),
            subject_wise_attendance=subject_wise,
            last_updated=student.get("last_updated"),
        )

    async def get_all_students(self) -> StudentListResponse:
        cursor = self.collection.find({}, {"_id": 0})
        students = await cursor.to_list(length=None)

        items = [
            StudentListItem(
                register_number=student["register_number"],
                name=student["name"],
                department=student["department"],
                year=student["year"],
                section=student["section"],
                semester=student["semester"],
                photo=student.get("photo"),
                overall_percentage=student.get("overall_percentage", 0.0),
            )
            for student in sorted(students, key=lambda s: s["register_number"])
        ]

        return StudentListResponse(total=len(items), students=items)

    async def upsert_student_attendance(
        self,
        register_number: str,
        name: str,
        department: str,
        year: str,
        section: str,
        semester: str,
        subject_code: str,
        subject_name: str,
        classes_conducted: int,
        classes_attended: int,
        percentage: float,
    ) -> dict[str, int]:
        now = datetime.now(UTC)
        subject_entry = {
            "subject_code": subject_code,
            "subject_name": sanitize_text(subject_name),
            "classes_conducted": classes_conducted,
            "classes_attended": classes_attended,
            "percentage": percentage,
        }

        existing = await self.collection.find_one({"register_number": register_number})
        profile = {
            "name": sanitize_text(name),
            "department": sanitize_text(department),
            "year": sanitize_text(year, 20),
            "section": sanitize_text(section, 20),
            "semester": sanitize_text(semester, 20),
        }

        if not existing:
            attendance = [subject_entry]
            overall_pct, _, _ = compute_overall_from_attendance(attendance)
            await self.collection.insert_one(
                {
                    "register_number": register_number,
                    **profile,
                    "photo": None,
                    "attendance": attendance,
                    "overall_percentage": overall_pct,
                    "last_updated": now,
                }
            )
            return {"added": 1, "updated": 0}

        attendance_list = list(existing.get("attendance", []))
        is_new_subject = True
        for index, item in enumerate(attendance_list):
            if item["subject_code"] == subject_code:
                attendance_list[index] = subject_entry
                is_new_subject = False
                break

        if is_new_subject:
            attendance_list.append(subject_entry)

        overall_pct, _, _ = compute_overall_from_attendance(attendance_list)
        await self.collection.update_one(
            {"register_number": register_number},
            {
                "$set": {
                    **profile,
                    "attendance": attendance_list,
                    "overall_percentage": overall_pct,
                    "last_updated": now,
                }
            },
        )

        if is_new_subject:
            return {"added": 1, "updated": 0}
        return {"added": 0, "updated": 1}

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.schemas import StatisticsResponse, StudentAttendanceRank


class StatisticsService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db.students

    async def get_statistics(self) -> StatisticsResponse:
        cursor = self.collection.find(
            {},
            {"register_number": 1, "name": 1, "overall_percentage": 1, "_id": 0},
        )
        students = await cursor.to_list(length=None)

        rankings = [
            StudentAttendanceRank(
                register_number=student["register_number"],
                name=student["name"],
                percentage=student.get("overall_percentage", 0.0),
            )
            for student in students
        ]

        if not rankings:
            return StatisticsResponse(
                average_attendance=0.0,
                students_below_75=[],
                top_10_attendance=[],
                lowest_attendance=[],
                total_students=0,
            )

        average = round(sum(r.percentage for r in rankings) / len(rankings), 1)
        below_75 = sorted(
            [r for r in rankings if r.percentage < 75],
            key=lambda r: r.percentage,
        )
        sorted_desc = sorted(rankings, key=lambda r: r.percentage, reverse=True)
        sorted_asc = sorted(rankings, key=lambda r: r.percentage)

        return StatisticsResponse(
            average_attendance=average,
            students_below_75=below_75,
            top_10_attendance=sorted_desc[:10],
            lowest_attendance=sorted_asc[:10],
            total_students=len(rankings),
        )

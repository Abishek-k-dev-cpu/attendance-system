from app.utils.percentage import overall_attendance


def compute_overall_from_attendance(attendance: list[dict]) -> tuple[float, int, int]:
    total_conducted = sum(item.get("classes_conducted", 0) for item in attendance)
    total_attended = sum(item.get("classes_attended", 0) for item in attendance)
    percentage = overall_attendance(total_attended, total_conducted)
    return percentage, total_conducted, total_attended

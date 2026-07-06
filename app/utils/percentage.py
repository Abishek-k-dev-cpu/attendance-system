def calculate_percentage(classes_attended: int, classes_conducted: int) -> float:
    if classes_conducted <= 0:
        return 0.0
    return round((classes_attended / classes_conducted) * 100, 1)


def overall_attendance(total_attended: int, total_conducted: int) -> float:
    return calculate_percentage(total_attended, total_conducted)

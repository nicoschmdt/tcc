import math
from datetime import timedelta, datetime


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    x_part = math.pow(a[0] - b[0], 2)
    y_part = math.pow(a[1] - b[1], 2)
    return math.sqrt(x_part + y_part)


def compute_angle(point1: tuple[float, float], point2: tuple[float, float], point3: tuple[float, float]) -> float:
    ang = math.degrees(
        math.atan2(point3[1]-point2[1], point3[0]-point2[0]) -
        math.atan2(point1[1]-point2[1], point1[0]-point2[0]))

    return ang + 360 if ang < 0 else ang


def time_difference(date1: datetime, date2: datetime) -> timedelta:
    if date1 > date2:
        return date1 - date2

    return date2 - date1

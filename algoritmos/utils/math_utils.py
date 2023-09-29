import math
from datetime import timedelta, datetime
from geopy import distance

import numpy as np


def compute_angle(point1: tuple[float, float], point2: tuple[float, float], point3: tuple[float, float]) -> float:
    ang = math.degrees(
        math.atan2(point3[1] - point2[1], point3[0] - point2[0]) -
        math.atan2(point1[1] - point2[1], point1[0] - point2[0]))

    return ang + 360 if ang < 0 else ang


def time_difference(date1: datetime, date2: datetime) -> timedelta:
    if date1 > date2:
        return date1 - date2

    return date2 - date1


def timedelta_diff(date1: timedelta, date2: timedelta) -> timedelta:
    if date1 > date2:
        return date1 - date2

    return date2 - date1


def get_middle(loc1: tuple[float, float], loc2: tuple[float, float]) -> tuple[float, float]:
    x = (loc1[0] + loc2[0]) / 2
    y = (loc1[1] + loc2[1]) / 2
    return x, y


def get_minor_axis(center: tuple[float, float], foci1: tuple[float, float], major: float) -> float:
    c = distance.distance(center, foci1).kilometers
    a = major / 2
    return math.sqrt(pow(a, 2) - pow(c, 2)) * 2


def ellipsis_angle(foci1: tuple[float, float], foci2: tuple[float, float]):
    return np.rad2deg(np.arctan2(foci2[1] - foci1[1], foci2[0] - foci1[0]))

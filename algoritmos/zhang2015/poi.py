from dataclasses import dataclass, field
from datetime import datetime, timedelta

from algoritmos.utils.math_utils import distance, compute_angle, time_difference
from algoritmos.utils.trajetory import Point


@dataclass
class PoI:
    id: str
    loc: tuple[float, float]
    t: datetime
    neighbours: list['PoI'] = field(default_factory=list)

    def __hash__(self):
        return hash(repr(self))


# Algorithm 2, Pag 4
def extract_poi(trajectory: list[Point], min_angle: float, min_dist: float, min_stay_time: timedelta) -> tuple[set[PoI], list[Point | PoI]]:
    pois = {point_to_poi(trajectory[0])}
    new_points = [point_to_poi(trajectory[0])]
    current_pos = 1
    next_pos = 2

    while current_pos < len(trajectory):
        point = trajectory[current_pos]

        next_point = None
        for index, candidate in enumerate(trajectory[current_pos:-1]):
            if distance(point.get_coordinates(), candidate.get_coordinates()) > min_dist:
                next_point = candidate
                next_pos = index
                break
            new_points.append(candidate)

        if next_point is None:
            break

        if time_difference(point.utc_timestamp, next_point.utc_timestamp) >= min_stay_time:
            if next_pos == current_pos + 1:
                pois |= {point_to_poi(point)}
                new_points.append(point_to_poi(point))
            else:
                poi = {PoI(
                    id=point.user_id,
                    loc=get_center(point, next_point),
                    t=point.utc_timestamp
                )}
                pois |= poi
                new_points.append(poi)
        else:
            angle = compute_angle(
                trajectory[current_pos-1].get_coordinates(), point.get_coordinates(), trajectory[current_pos+1].get_coordinates())
            if angle >= min_angle:
                pois |= {point_to_poi(point)}
                new_points.append(point_to_poi(point))

        current_pos = next_pos
    pois |= {point_to_poi(trajectory[-1])}  # adding the end
    new_points.append(point_to_poi(trajectory[-1]))
    return pois, new_points


def get_center(point: Point, point2: Point) -> tuple[float, float]:
    latitude = (point.latitude + point2.latitude)/2
    longitude = (point.longitude + point2.longitude)/2
    return latitude, longitude


def point_to_poi(point: Point) -> PoI:
    return PoI(
        id=point.user_id,
        loc=point.get_coordinates(),
        t=point.utc_timestamp
    )


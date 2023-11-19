from dataclasses import dataclass, field
from datetime import datetime, timedelta
from geopy import distance

from algoritmos.utils import semantic
from algoritmos.utils.math_utils import compute_angle, time_difference, get_middle
from algoritmos.utils.semantic import PoiCategory
from algoritmos.utils.trajetory import Point


@dataclass
class PoI:
    id: int
    loc: tuple[float, float]
    t: datetime
    semantic: PoiCategory
    neighbours: set[int] = field(default_factory=set)

    def __hash__(self):
        return hash(repr(self))


# Algorithm 2, Pag 4
def extract_poi(trajectory: list[Point], min_angle: float, min_dist: float, min_stay_time: timedelta, counter: int) -> \
        tuple[set[PoI], list[Point | PoI], int]:
    pois = {point_to_poi(trajectory[0], counter)}
    new_points = [point_to_poi(trajectory[0], counter)]
    counter += 1
    current_pos = 1
    next_pos = 2

    while current_pos < len(trajectory):
        point = trajectory[current_pos]
        next_point = None
        for index, candidate in enumerate(trajectory[current_pos+1:-1]):
            if distance.distance(point.get_coordinates(), candidate.get_coordinates()).meters > min_dist:
                next_point = candidate
                next_pos = (index + 1) + current_pos
                break
            new_points.append(candidate)

        if next_point is None:
            break

        if time_difference(point.timestamp, next_point.timestamp) >= min_stay_time:
            if next_pos == current_pos + 1:
                pois |= {point_to_poi(point, counter)}
                new_points.append(point_to_poi(point, counter))
                counter += 1
            else:
                poi = {PoI(
                    id=counter,
                    loc=get_middle(point.get_coordinates(), next_point.get_coordinates()),
                    t=point.timestamp,
                    semantic=semantic.generalize_venue_category(point.category)
                )}
                counter += 1
                pois |= poi
                new_points.append(poi)
        else:
            angle = compute_angle(
                trajectory[current_pos-1].get_coordinates(), point.get_coordinates(), trajectory[current_pos+1].get_coordinates())
            if angle >= min_angle:
                pois |= {point_to_poi(point, counter)}
                new_points.append(point_to_poi(point, counter))
                counter += 1

        current_pos = next_pos
    pois |= {point_to_poi(trajectory[-1], counter)}  # adding the end
    new_points.append(point_to_poi(trajectory[-1], counter))
    counter += 1
    return pois, new_points, counter


def point_to_poi(point: Point, counter: int) -> PoI:
    return PoI(
        id=counter,
        loc=point.get_coordinates(),
        t=point.timestamp,
        semantic=semantic.generalize_venue_category(point.category)
    )

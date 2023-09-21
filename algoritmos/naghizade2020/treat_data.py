from dataclasses import dataclass
from datetime import datetime, timedelta

from algoritmos.utils.math_utils import time_difference, distance
from algoritmos.utils.semantic import PoiCategory, SemanticPoint


@dataclass
class Stop:
    locations: list[tuple[float, float]]
    start: datetime
    end: datetime
    semantic: PoiCategory
    type: str
    sensitivity: float = None

    def get_duration(self) -> timedelta:
        return self.end - self.start

    def get_position(self) -> tuple[float, float]:
        x = sum([x for x, y in self.locations]) / len(self.locations)
        y = sum([y for x, y in self.locations]) / len(self.locations)
        return x, y


@dataclass
class Move:
    locations: list[tuple[float, float]]
    start: datetime
    end: datetime

    def get_duration(self) -> timedelta:
        return self.end - self.start


@dataclass
class Segmented:
    points: list[Stop | Move]
    privacy_settings: dict[PoiCategory, float]

    def process_sensitivity(self) -> None:
        trip_duration = self.points[-1].end - self.points[0].start

        for point in self.points:
            if isinstance(point, Move):
                continue

            stop_s = (trip_duration - point.get_duration()) / trip_duration
            point.sensitivity = pow(self.privacy_settings[point.semantic], stop_s)
            

@dataclass
class SubSegment:
    points: list[Stop | Move]
    init_index: int
    end_index: int

    def index(self, point: [Stop | Move]) -> int:
        for i, p in enumerate(self.points):
            if p == point:
                return i


def identify_stops(trajectories: list[tuple[list[SemanticPoint], dict[PoiCategory, float]]], dist_threshold: float,
                   temporal_threshold: timedelta) -> list[Segmented]:
    segmented_trajectories = []

    for traj_points, user_sensitivity_rank in trajectories:
        points = []
        stay_points = []
        move_points = []
        ref_point = traj_points[0]
        for compared_point in traj_points[1:]:
            #  possivel stop
            if distance(ref_point.get_coordinates(), compared_point.get_coordinates()) < dist_threshold:
                stay_points.append(ref_point)
                if compared_point == traj_points[-1]:
                    stay_points.append(compared_point)

            else:
                if stay_points:
                    # stay points eram stay points
                    if time_difference(stay_points[0].utc_timestamp,
                                       stay_points[-1].utc_timestamp) > temporal_threshold:
                        # se tiver algum move point guardado adiciona-se eles antes dos stay points
                        if move_points:
                            locations = [stored for stored in move_points]
                            points.append(Move(locations, move_points[0].utc_timestamp, move_points[-1].utc_timestamp))
                            move_points = []
                        locations = [stored.get_coordinates() for stored in stay_points]
                        semantic, sem_type = get_semantic(stay_points)
                        points.append(
                            Stop(locations, stay_points[0].utc_timestamp, stay_points[-1].utc_timestamp, semantic,
                                 sem_type))
                    # stay points não eram stay points
                    else:
                        move_points.extend(stay_points)
                    stay_points = []

                else:
                    move_points.append(ref_point)

        # os move points são antes dos stay points
        if stay_points:
            if time_difference(stay_points[0].utc_timestamp, stay_points[-1].utc_timestamp) > temporal_threshold:
                # se tiver algum move point guardado adiciona-se eles antes dos stay points
                if move_points:
                    locations = [stored for stored in move_points]
                    points.append(Move(locations, move_points[0].utc_timestamp, move_points[-1].utc_timestamp))
                    move_points = []
                locations = [stored.get_coordinates() for stored in stay_points]
                semantic, sem_type = get_semantic(stay_points)
                points.append(
                    Stop(locations, stay_points[0].utc_timestamp, stay_points[-1].utc_timestamp, semantic, sem_type))
            # stay points não eram stay points
            else:
                move_points.extend(stay_points)

        if move_points:
            locations = [stored for stored in move_points]
            points.append(Move(locations, move_points[0].utc_timestamp, move_points[-1].utc_timestamp))

        segmented_trajectory = Segmented(points, user_sensitivity_rank)
        segmented_trajectory.process_sensitivity()
        segmented_trajectories.append(segmented_trajectory)

    return segmented_trajectories


def get_semantic(points: list[SemanticPoint]) -> tuple[PoiCategory, str]:
    x = sum([point.latitude for point in points]) / len(points)
    y = sum([point.longitude for point in points]) / len(points)

    min_dist = float('inf')
    category_chosen = None
    type_chosen = None
    for point in points:
        dist = distance(point.get_coordinates(), (x, y))
        if dist < min_dist:
            min_dist = dist
            category_chosen = point.category
            type_chosen = point.type

    return category_chosen, type_chosen


def get_all_pois(trajectories: list[Segmented]) -> list[Stop]:
    all_poi = []
    for trajectory in trajectories:
        pois = [point for point in trajectory.points if isinstance(point, Stop)]
        all_poi.extend(pois)

    return all_poi

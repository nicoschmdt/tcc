from dataclasses import dataclass
from enum import Enum, auto
from datetime import timedelta, datetime
from algoritmos.utils.trajetory import Trajectory, Point


class PoiCategory(str, Enum):
    Entertainment = auto()
    Education = auto()
    Scenery = auto()
    Business = auto()
    Industry = auto()
    Residence = auto()
    Transport = auto()


@dataclass
class SemanticPoint:
    category: PoiCategory
    latitude: float
    longitude: float
    timestamp: datetime
    duration: timedelta
    type: str = ""

    def get_coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude


@dataclass
class SemanticTrajectory:
    points: list[SemanticPoint]
    n: int = 1


def get_venue_category(trajectories: list[Trajectory]) -> list[SemanticTrajectory]:
    altered_trajectories = []

    for trajectory in trajectories:
        tu_trajectory = SemanticTrajectory([])
        for point in trajectory.points:
            tu_point = modify_point(point)
            tu_trajectory.points.append(tu_point)

        altered_trajectories.append(tu_trajectory)

    return altered_trajectories


def get_category_with_type(trajectories: list[tuple[Trajectory, dict[PoiCategory, float]]]) -> \
        list[tuple[list[SemanticPoint], dict[PoiCategory, float]]]:
    altered_trajectories = []

    for trajectory, user_settings in trajectories:
        semantic = []
        for point in trajectory.points:
            sem_point = modify_point(point)
            sem_point.type = point.category
            semantic.append(sem_point)

        altered_trajectories.append((semantic, user_settings))

    return altered_trajectories


def modify_point(point: Point) -> SemanticPoint:
    return SemanticPoint(
        generalize_venue_category(point.category),
        point.lat,
        point.lon,
        point.timestamp,
        point.duration,
        point.category
    )


def generalize_venue_category(venue_category: str) -> PoiCategory:
    if any(sub_str in venue_category for sub_str in
           ['Shop', 'Store', 'Restaurant', 'Bakery', 'Wash', 'Embassy', 'Ramen', 'Diner', 'Salon', 'Place',
            'Steakhouse', 'Market', 'Joint', 'store', 'Food', 'Service', 'Bar', 'Café', 'Cafe', 'Office', 'Bank',
            'Mall', 'Newsstand', 'Fair', 'Tea', 'City', 'Gastropub', 'Studio', 'Bodega', 'Rental', 'Dealership',
            'Photography Lab', 'Medical Center']):
        return PoiCategory.Business
    elif any(sub_str in venue_category for sub_str in
             ['Factory', 'Military', 'Distillery', 'Government', 'Harbor', 'Facility', 'Winery', 'Brewery', 'Tattoo']):
        return PoiCategory.Industry
    elif any(sub_str in venue_category for sub_str in
             ['Residential Building', 'Building', 'Shelter', 'Neighborhood', 'Home', 'Hotel', 'Housing', 'House']):
        return PoiCategory.Residence
    elif any(sub_str in venue_category for sub_str in
             ['Scenery', 'Scenic', 'Park', 'Outdoors', 'Garden', 'Museum', 'Castle', 'River', 'Cemetery', 'Temple',
              'Synagogue', 'Church', 'Shrine', 'Historic', 'Mosque', 'Planetarium', 'Spot', 'Rest Area', 'Plaza',
              'Spiritual', 'Campground']):
        return PoiCategory.Scenery
    elif any(sub_str in venue_category for sub_str in ['School', 'College', 'Student', 'University']):
        return PoiCategory.Education
    elif any(sub_str in venue_category for sub_str in
             ['Music', 'Movie', 'Playground', 'Arcade', 'Art', 'Entertainment', 'Gym', 'Nightlife', 'Spa', 'Pool',
              'Library', 'Aquarium', 'Beach', 'Zoo', 'Bowling', 'Theater', 'Athletic', 'Casino', 'Comedy', 'Stadium',
              'Concert', 'Convention', 'Ski', 'Racetrack']):
        return PoiCategory.Entertainment
    elif any(sub_str in venue_category for sub_str in
             ['Train', 'Bike', 'Airport', 'Ferry', 'Station', 'Road', 'Moving', 'Transport', 'Subway', 'Bridge',
              'Travel', 'Taxi', 'Light Rail']):
        return PoiCategory.Transport


def split_with_settings(trajectories: dict[str, tuple[Trajectory, dict[PoiCategory]]],
                        min_traj: int = 1) -> list[tuple[Trajectory, dict[PoiCategory, float]]]:
    """
    Divide as trajetórias por dia
    Se o tamanho da trajetória for menor que min_traj a trajetória é descartada
    """
    splitted = []
    for user_id in trajectories:
        trajectory, user_settings = trajectories[user_id]
        compare = trajectory.points[0]
        lista = Trajectory([compare])
        for point in trajectory.points[1:]:
            if compare.timestamp.day == point.timestamp.day:
                lista.points.append(point)
            else:
                splitted.append((lista, user_settings))
                lista = Trajectory([point])
            compare = point
        splitted.append((lista, user_settings))

    return [(trajectory, settings) for trajectory, settings in splitted
            if len(trajectory.points) >= min_traj]

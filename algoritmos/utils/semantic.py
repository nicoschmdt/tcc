from dataclasses import dataclass
from enum import Enum, auto
from datetime import timedelta, datetime

from algoritmos.utils.region import Region
from algoritmos.utils.trajetoria import Trajectory, Point


class PoiCategory(Enum):
    Entertainment = auto()
    Education = auto()
    Scenery = auto()
    Business = auto()
    Industry = auto()
    Residence = auto()
    Transport = auto()


@dataclass
class SemanticPoint:
    name: str
    user_id: str
    category: PoiCategory
    latitude: float
    longitude: float
    utc_timestamp: datetime
    duration: timedelta
    region: Region


@dataclass
class SemanticTrajectory:
    trajectory: list[SemanticPoint]
    n: int = 1

    def reshape(self) -> None:
        """
        Confere se os pontos semânticos não se sobresaem temporalmente.
        """
        pass


def get_venue_category(trajectories: list[Trajectory]) -> list[SemanticTrajectory]:
    altered_trajectories = []

    for trajectory in trajectories:
        tu_trajectory = SemanticTrajectory([])
        for point in trajectory.trajectory:
            tu_point = modify_point(point)
            tu_trajectory.trajectory.append(tu_point)

        altered_trajectories.append(tu_trajectory)

    return altered_trajectories


def modify_point(point: Point) -> SemanticPoint:
    return SemanticPoint(
        point.name,
        point.user_id,
        {generalize_venue_category(point.venue_category)},
        point.latitude,
        point.longitude,
        point.utc_timestamp,
        point.duration)


def generalize_venue_category(venue_category: str) -> PoiCategory:
    if any(sub_str in venue_category for sub_str in
           ['Shop', 'Store', 'Restaurant', 'Bakery', 'Wash', 'Embassy', 'Ramen', 'Diner', 'Salon', 'Place',
            'Steakhouse', 'Market', 'Joint', 'store', 'Food', 'Service', 'Bar', 'Café', 'Cafe', 'Office', 'Bank',
            'Mall', 'Newsstand', 'Fair', 'Tea', 'City', 'Gastropub', 'Studio', 'Bodega', 'Rental', 'Dealership',
            'Photography Lab', 'Medical Center']):
        return PoiCategory.Business
    elif any(sub_str in venue_category for sub_str in
             ['Factory', 'Military', 'Distillery', 'Government', 'Harbor', 'Facility', 'Winery', 'Brewery']):
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

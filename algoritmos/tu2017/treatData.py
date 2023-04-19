from ..utils.trajetoria import process_trajectories, Trajectory, Point
from ..utils.graph import Graph, Region
from dataclasses import dataclass
from datetime import timedelta, datetime
from enum import Enum, auto
from typing import List, Set


# t-closeness: distribuição igual de PoI
# l-diversity: every point has at least l categories
class PoiCategory(Enum):
    Entertainment = auto()
    Education = auto()
    Scenery = auto()
    Business = auto()
    Industry = auto()
    Residence = auto()
    Transport = auto()


@dataclass
class TuPoint:
    name: str
    user_id: str
    category: set[PoiCategory]
    latitude: float
    longitude: float
    utc_timestamp: datetime
    duration: float


@dataclass
class TuTrajectory:
    trajectory: List[TuPoint]
    n: int = 1


def get_venue_category(trajectories: list[Trajectory]) -> list[TuTrajectory]:
    altered_trajectories = []

    for trajectory in trajectories:
        tu_trajectory = TuTrajectory([])
        for point in trajectory.trajectory:
            tu_point = modify_point(point)
            tu_trajectory.trajectory.append(tu_point)

        altered_trajectories.append(tu_trajectory)

    return altered_trajectories


def modify_point(point: Point) -> TuPoint:
    return TuPoint(
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


def construct_graph(trajectories: list[TuTrajectory]):
    graph = Graph()

    for trajectory in trajectories:
        neighbour = []
        for point in trajectory.trajectory:
            region = Region(
                [point],
                neighbour
            )

            graph.add_vertex(region)

            if neighbor != []:
                graph.add_neighbours()  # todo
                neighbor = []
            else:
                neighbor = [region]


if __name__ == "__main__":
    count = 0
    # for categoria in lista_categorias:
    #     a = generalize_venue_category(categoria)
    #     if a == 'a':
    #         count += 1

    print(count)
    # trajectories = process_trajectories('resources/dataset_TSMC2014_TKY.csv')
    # get_venue_category(trajectories)
    # print(trajectories)

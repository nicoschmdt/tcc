import csv
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Sequence

from algoritmos.utils.semantic import PoiCategory


@dataclass
class Point:
    name: str
    user_id: str
    venue_id: set[str]
    venue_category_id: set[str]
    venue_category: str
    latitude: float
    longitude: float
    utc_timestamp: datetime
    duration: timedelta

    def get_coordinates(self) -> tuple[float, float]:
        return self.latitude, self.longitude


@dataclass
class Trajectory:
    points: list[Point]


def create_raw_trajectories(name: str) -> dict[str, Trajectory]:
    trajectories = {}
    with open(name) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for i, row in enumerate(reader):
            user_id, *data = row
            if user_id not in trajectories:
                trajectories[user_id] = Trajectory([])
            point_created = create_point(row)
            trajectories[user_id].points.append(point_created)
            # if i == 1000000:
            # break
    return trajectories


def create_point(point_info: Sequence[str]) -> Point:
    return Point(
        name=point_info[1],
        user_id=point_info[0],
        venue_id={point_info[1]},
        venue_category_id={point_info[2]},
        venue_category=point_info[3],
        latitude=float(point_info[4]),
        longitude=float(point_info[5]),
        # int(point_info[6]),
        utc_timestamp=datetime.strptime(point_info[7], '%a %b %d %H:%M:%S %z %Y'),
        duration=timedelta(hours=0))


# acho que dá pra melhorar, dar um limite maximo de diferença de horário ou de proximidade
def split_trajectories(trajectories: dict[str, Trajectory], min_traj: int = 1) -> list[Trajectory]:
    """
    Divide as trajetórias por dia
    Se o tamanho da trajetória for menor que min_traj a trajetória é descartada
    """
    splitted = []
    for user_id in trajectories:
        trajectory = trajectories[user_id].points
        compare = trajectory[0]
        lista = Trajectory([compare])
        for point in trajectory[1:]:
            if compare.utc_timestamp.day == point.utc_timestamp.day:
                lista.points.append(point)
            else:
                splitted.append(lista)
                lista = Trajectory([point])
            compare = point
        splitted.append(lista)

    splitted = [trajectory for trajectory in splitted
                if len(trajectory.points) >= min_traj]

    return splitted


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
            if compare.utc_timestamp.day == point.utc_timestamp.day:
                lista.points.append(point)
            else:
                splitted.append((lista, user_settings))
                lista = Trajectory([point])
            compare = point
        splitted.append((lista, user_settings))

    splitted = [(trajectory, settings)
                for trajectory, settings in splitted
                if len(trajectory.points) >= min_traj]

    return splitted


def add_duration(trajectories: list[Trajectory]) -> list[Trajectory]:
    """
    Recebe uma lista de Trajectory e retorna uma nova lista com a duração de cada ponto atualizada
    Pontos tem a sua duração atualizada se dado um Ponto, o próximo possuir o mesmo venue_id que o anterior
    """
    new_list = []
    for trajectory in trajectories:
        point_one = trajectory.points[0]
        new_trajectory = Trajectory([])
        for segment in trajectory.points[1:]:
            if point_one.venue_id != segment.venue_id:
                new_trajectory.points.append(point_one)
                point_one = segment
            # same location just update the duration
            else:
                timestamp_one = point_one.utc_timestamp
                timestamp_two = segment.utc_timestamp
                new_duration = timestamp_two - timestamp_one
                point_one.duration = new_duration + point_one.duration
        new_trajectory.points.append(point_one)
        new_list.append(new_trajectory)
    return new_list

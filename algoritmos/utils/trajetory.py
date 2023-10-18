import csv
from dataclasses import dataclass
from datetime import timedelta, datetime
from typing import Sequence
from skmob.preprocessing import filtering
from skmob import TrajDataFrame


@dataclass
class Point:
    name: str
    uid: str
    venue_id: set[str]
    category: str
    lat: float
    lon: float
    timestamp: datetime
    duration: timedelta

    def get_coordinates(self) -> tuple[float, float]:
        return self.lat, self.lon


@dataclass
class Trajectory:
    points: list[Point]


def process(name: str):
    points = []
    with open(name) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            user_id = int(row[0])
            venue_id = row[1]
            category = row[3]
            lat = float(row[4])
            lon = float(row[5])
            timestamp = row[7]
            points.append([user_id, venue_id, category, lat, lon, timestamp])

    dataset = TrajDataFrame(points, user_id=0, latitude=3, longitude=4, datetime=5)
    return filtering.filter(dataset, max_speed_kmh=10.)


def raw(name: str) -> dict[str, Trajectory]:
    filtered = process(name)
    trajectories = {}
    for index in range(len(filtered)):
        uid = str(filtered['uid'][index])
        if uid not in trajectories:
            trajectories[uid] = Trajectory([])
            p = point(filtered, index)
            trajectories[uid].points.append(p)

    return trajectories


def point(filtered, index):
    return Point(
        name=filtered[1][index],
        uid=filtered['uid'][index],
        venue_id={filtered[1][index]},
        category=filtered[2][index],
        lat=filtered['lat'][index],
        lon=filtered['lng'][index],
        timestamp=filtered['datetime'][index],
        duration=timedelta(hours=0)
    )


def create_raw_trajectories(name: str) -> dict[str, Trajectory]:
    trajectories = {}
    with open(name) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            user_id, *data = row
            if user_id not in trajectories:
                trajectories[user_id] = Trajectory([])
            point_created = create_point(row)
            trajectories[user_id].points.append(point_created)
    return trajectories


def create_point(point_info: Sequence[str]) -> Point:
    return Point(
        name=point_info[1],
        uid=point_info[0],
        venue_id={point_info[1]},
        category=point_info[3],
        lat=float(point_info[4]),
        lon=float(point_info[5]),
        timestamp=datetime.strptime(point_info[7], '%a %b %d %H:%M:%S %z %Y'),
        duration=timedelta(hours=0))


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
        for p in trajectory[1:]:
            if compare.timestamp.day == p.timestamp.day:
                lista.points.append(p)
            else:
                splitted.append(lista)
                lista = Trajectory([p])
            compare = p
        splitted.append(lista)

    return [trajectory for trajectory in splitted if len(trajectory.points) >= min_traj]


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
                timestamp_one = point_one.timestamp
                timestamp_two = segment.timestamp
                new_duration = timestamp_two - timestamp_one
                point_one.duration = new_duration + point_one.duration
        new_trajectory.points.append(point_one)
        new_list.append(new_trajectory)
    return new_list

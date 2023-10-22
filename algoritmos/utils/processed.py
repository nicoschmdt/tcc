from skmob.core.trajectorydataframe import TrajDataFrame

from algoritmos.naghizade2020.treat_data import Segmented, Stop, Move
from algoritmos.tu2017.region import Region
from algoritmos.tu2017.treat_data import TuTrajectory
from algoritmos.utils.trajetory import Point
from algoritmos.zhang2015.group import ZhangTrajectory
from algoritmos.zhang2015.poi import PoI


def naghizade(trajectories: list[Segmented]) -> TrajDataFrame:
    points = []

    for trajectory in trajectories:
        uid = trajectory.uid
        for point in trajectory.points:
            duration = point.end - point.start
            step = duration/len(point.locations)
            time = point.start
            for lat, lon in point.locations:
                points.append([uid, lat, lon, time])
                time += step

    return TrajDataFrame(points, user_id=0, latitude=1, longitude=2, datetime=3)


def tu(trajectories: list[TuTrajectory],  regions: dict[int, Region]) -> TrajDataFrame:
    points = []
    for trajectory in trajectories:
        for point in trajectory.points:
            timestamp = point.utc_timestamp
            coordinates = [regions[rid].center_point for rid in point.region_id]
            lat, lon = [sum(tup) for tup in zip(*coordinates)]
            for uid in trajectory.uid:
                points.append([uid, lat, lon, timestamp])

    return TrajDataFrame(points, user_id=0, latitude=1, longitude=2, datetime=3)


def zhang(trajectories: list[list[ZhangTrajectory]]) -> TrajDataFrame:
    points = []

    for group in trajectories:
        for trajectory in group:
            uid = trajectory.uid
            for point in trajectory.points:
                if isinstance(point, Point):
                    points.append([uid, point.lat, point.lon, point.timestamp])
                elif isinstance(point, PoI):
                    lat, lon = point.loc
                    points.append([uid, lat, lon, point.t])

    return TrajDataFrame(points, user_id=0, latitude=1, longitude=2, datetime=3)

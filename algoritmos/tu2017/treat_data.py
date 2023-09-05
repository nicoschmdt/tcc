from dataclasses import dataclass
from datetime import timedelta, datetime
from itertools import pairwise

from algoritmos.utils.semantic import SemanticTrajectory, SemanticPoint
from ..utils.graph import Graph, Region

AREA_RANGE = 150


@dataclass
class TuPoint:
    utc_timestamp: datetime
    duration: timedelta
    region: Region


@dataclass
class TuTrajectory:
    points: list[TuPoint]
    n: int = 1

    def reshape(self) -> None:
        """
        Confere se os pontos semânticos não se sobresaem temporalmente.
        """
        updated_points = []
        for point, compared in pairwise(self.points):
            # o próximo ponto começa temporalmente depois do atual
            if point.utc_timestamp + point.duration < compared.utc_timestamp:
                updated_points.append(point)
                continue

            else:
                # Calcula o tempo final de um ponto com base no inicio do próximo e atualiza a duração
                init = point.utc_timestamp
                duration = point.duration
                new_duration = duration - (init + duration - compared.utc_timestamp)
                updated_points.append(TuPoint(point.utc_timestamp, new_duration, point.region))

        self.points = updated_points


def construct_graph(trajectories: list[SemanticTrajectory]) -> tuple[Graph, list[TuTrajectory]]:
    graph = Graph()
    categories = {}
    poi_sum = 0

    tu_trajectories = []
    for trajectory in trajectories:
        tu_points = []
        for point in trajectory.trajectory:
            region = construct_region(point)
            tu_points.append(TuPoint(point.utc_timestamp, point.duration, region))
            graph.add_vertex(region)

            poi_sum += 1
            try:
                categories[point.category] += 1
            except KeyError:
                categories[point.category] = 1
        tu_trajectories.append(TuTrajectory(tu_points))

    graph.poi_distribution = {category: categories[category] / poi_sum for category in categories}
    return graph.prune_and_simplify(), tu_trajectories


def construct_region(point: SemanticPoint) -> Region:
    return Region(
        center_point=(point.latitude, point.longitude),
        area=AREA_RANGE,
        categories={point.category: 1},
        neighbours=[])

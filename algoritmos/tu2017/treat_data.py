from dataclasses import dataclass
from datetime import timedelta, datetime
from itertools import pairwise

from algoritmos.utils.semantic import SemanticTrajectory, SemanticPoint, PoiCategory
from ..utils.graph import Graph, Region

AREA_RANGE = 150


@dataclass
class TuPoint:
    utc_timestamp: datetime
    duration: timedelta
    region_id: list[int]


@dataclass
class TuTrajectory:
    id: int
    points: list[TuPoint]
    n: int = 1

    def __hash__(self):
        return hash(repr(self))

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
                updated_points.append(TuPoint(point.utc_timestamp, new_duration, point.region_id))

        self.points = updated_points


def construct_graph(trajectories: list[SemanticTrajectory]) -> tuple[Graph, list[TuTrajectory]]:
    graph = Graph()
    categories = {}
    poi_sum = 0
    region_id = 0
    trajectory_id = 0
    tu_trajectories = []
    for trajectory in trajectories:
        tu_points = []
        for point in trajectory.points:
            region = construct_region(point, region_id)
            tu_points.append(TuPoint(point.utc_timestamp, point.duration, [region_id]))
            region_id += 1
            graph.add_vertex(region)

            poi_sum += 1
            try:
                categories[point.category] += 1
            except KeyError:
                categories[point.category] = 1
        tu_trajectories.append(TuTrajectory(trajectory_id, tu_points))
        trajectory_id += 1
    graph.poi_distribution = {category: categories[category] / poi_sum for category in categories}
    return graph, tu_trajectories


def update_ids(info: dict[int, list[int]], trajectories: list[TuTrajectory], regions: dict[int, Region]) -> None:
    for trajectory in trajectories:
        for point in trajectory.points:
            regions_id = set(point.region_id)
            new_ids = set()
            for reg_id in regions_id:
                neighbours = regions[reg_id].neighbours_id
                found = False
                for key, values in info.items():
                    updated = set()
                    remove = set()
                    for neighbour in neighbours:
                        if neighbour in values:
                            updated |= {key}
                            remove |= {neighbour}
                    neighbours |= updated
                    neighbours -= remove
                    if reg_id in values:
                        found = True
                        new_ids |= {key}
                regions[reg_id].neighbours_id = neighbours
                if not found:
                    new_ids |= {reg_id}
            point.region_id = list(new_ids)


def update_neighbours(graph: Graph, info: dict[int, list[int]]) -> None:
    for region in graph.vertices:
        neighbours = {nid for nid in region.neighbours_id}
        updated = set()
        for neighbour_id in neighbours:
            found = False
            for key, values in info.items():
                if neighbour_id in values:
                    found = True
                    updated |= {key}
            if not found:
                updated |= {neighbour_id}
        region.neighbours_id = list(updated)


def construct_categories(semantic: PoiCategory = None) -> dict[PoiCategory, int]:
    categories = {}
    for category in PoiCategory:
        categories[category] = 0

    if semantic is not None:
        categories[semantic] = 1

    return categories


def construct_region(point: SemanticPoint, region_id: int) -> Region:
    return Region(
        id=region_id,
        center_point=(point.latitude, point.longitude),
        area=AREA_RANGE,
        categories=construct_categories(point.category),
        neighbours_id=set())

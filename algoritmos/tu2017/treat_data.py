from dataclasses import dataclass
from datetime import timedelta, datetime

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
    trajectory: list[TuPoint]
    n: int = 1

    def reshape(self) -> None:
        """
        Confere se os pontos semânticos não se sobresaem temporalmente.
        """
        # TODO
        pass


def construct_graph(trajectories: list[SemanticTrajectory]) -> (Graph, list[TuTrajectory]):
    graph = Graph()
    categories = {}
    poi_sum = 0

    tu_trajectories = []
    for trajectory in trajectories:
        tu_trajectory = []
        for point in trajectory.trajectory:
            region = construct_region(point)
            tu_trajectory.append(TuPoint(point.utc_timestamp, point.duration, region))
            graph.add_vertex(region)

            poi_sum += 1
            try:
                categories[point.category] += 1
            except KeyError:
                categories[point.category] = 1
        tu_trajectories.append(tu_trajectory)

    graph.poi_distribution = {category: categories[category] / poi_sum for category in categories}
    return graph.prune_and_simplify(), tu_trajectories


def construct_region(point: SemanticPoint) -> Region:
    return Region(
            center_point=(point.latitude, point.longitude),
            area=AREA_RANGE,
            categories={point.category: 1},
            neighbours=[])


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

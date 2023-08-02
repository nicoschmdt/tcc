from algoritmos.utils.semantic import SemanticTrajectory, PoiCategory
from ..utils.graph import Graph, Region

AREA_RANGE = 150


def construct_graph(trajectories: list[SemanticTrajectory]) -> Graph:
    graph = Graph()
    categories = {}
    poi_sum = 0

    for trajectory in trajectories:
        for point in trajectory.trajectory:
            region = Region(
                center_point=(point.latitude, point.longitude),
                area=AREA_RANGE,
                points=[point],
                categories={point.category: 1},
                neighbours=[]
            )
            point.region = region
            graph.add_vertex(region)

            poi_sum += 1
            try:
                categories[point.category] += 1
            except KeyError:
                categories[point.category] = 1

    graph.poi_distribution = {category: categories[category] / poi_sum for category in categories}
    return graph.prune_and_simplify()


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

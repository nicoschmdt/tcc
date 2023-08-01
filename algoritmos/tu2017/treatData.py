from algoritmos.utils.semantic import SemanticTrajectory
from ..utils.graph import Graph, Region

AREA_RANGE = 150


def construct_graph(trajectories: list[SemanticTrajectory]) -> Graph:
    graph = Graph()

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

from algoritmos.utils.semantic import SemanticTrajectory
from ..utils.graph import Graph, Region

AREA_RANGE = 100


def construct_graph(trajectories: list[SemanticTrajectory]) -> Graph:
    graph = Graph()

    for trajectory in trajectories:
        neighbour = []
        for point in trajectory.trajectory:
            # if previous_region is not None:
            #     if previous_region.is_inside(point):
            #         previous_region.add_point(point)

            region = Region(
                center_point=point,
                area=AREA_RANGE,
                points=[point],
                neighbours=neighbour
            )

            graph.add_vertex(region)

    graph.prune_and_simplify()
    return graph


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

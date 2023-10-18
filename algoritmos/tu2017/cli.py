from algoritmos.tu2017.cost_matrix import create_cost_matrix
from algoritmos.tu2017.treat_data import construct_graph, TuTrajectory, update_ids, update_neighbours
from algoritmos.tu2017.tu import merging_trajectories
from algoritmos.tu2017.graph import Graph
from algoritmos.utils.io import write, read_tu, read_graph, read_regions, read_cost_matrix, read_merged
from algoritmos.tu2017.region import Region
from algoritmos.utils.semantic import get_venue_category
from algoritmos.utils.trajetory import create_raw_trajectories, split_trajectories, add_duration


def main():
    # pre-process
    dataset_name = "../../resources/dataset_TSMC2014_NYC.csv"
    # trajectories = create_raw_trajectories(dataset_name)
    # splitted = split_trajectories(trajectories, 3)
    # with_duration = add_duration(splitted)

    # read
    tu_trajectories = read_tu('semantic.json')
    # graph = read_graph('graph.json')
    graph = read_graph('graph_updated.json')
    regions = read_regions('regions.json')
    cost_matrix = read_cost_matrix('cost_matrix_test.json')
    # merged = read_merged('merged.json')

    # semantic
    # semantic = get_venue_category(with_duration)

    # graph, tu_trajectories = construct_graph(semantic)
    # new_graph, merged = graph.prune_and_simplify()
    # regions = {vertex.id: vertex for vertex in graph.vertices}
    # update_ids(merged, tu_trajectories, regions)
    # update_neighbours(graph, merged)
    # cost_matrix = create_cost_matrix(tu_trajectories, regions)


    # write
    # write(graph, 'graph_updated.json')
    # write(regions, 'regions.json')
    # write(tu_trajectories, 'semantic.json')
    # write(merged, 'merged.json')
    # write(cost_matrix, 'cost_matrix_test.json')

    # treat data
    k = 4
    l = 5
    t = 0.01
    anonymized = merging_trajectories(tu_trajectories, graph, cost_matrix, k, l, t, regions)
    write(anonymized, 'k4l5t001-anonymized.json')

    # k influence: k variando de 2 à 5; l=6 e t=0.01
    # l influence: k=2; l variando de 4 à 6; t='inf' (unconstrained)
    # t influence: k=2; l=6; t variando de 0.1 à 0.001


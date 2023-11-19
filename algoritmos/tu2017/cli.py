import json
from pathlib import Path

from algoritmos.tu2017.cost_matrix import create_cost_matrix
from algoritmos.tu2017.treat_data import construct_graph, TuTrajectory, update_ids, update_neighbours
from algoritmos.tu2017.tu import merging
from algoritmos.tu2017.graph import Graph
from algoritmos.utils.io import write, read_tu, read_graph, read_regions, read_costs, read_merged
from algoritmos.tu2017.region import Region
from algoritmos.utils.semantic import get_venue_category
from algoritmos.utils.trajetory import create_raw_trajectories, split_trajectories, add_duration


def main():
    # pre-process
    # dataset_name = Path(__file__).parent / "../../resources/dataset_TSMC2014_NYC-half.csv"
    dataset_name = Path(__file__).parent / "../../resources/dataset_TSMC2014_TKY-half.csv"
    # dataset_name = "../../tests/resources/test.csv"
    trajectories = create_raw_trajectories(str(dataset_name))
    splitted = split_trajectories(trajectories, 3)
    with_duration = add_duration(splitted)

    # read
    # tu_trajectories = read_tu('semantic.json')
    # tu_trajectories = read_tu('tu2017/traj-test.json')
    tu_trajectories = read_tu('tu2017/updated-ids-TKY.json')
    # graph = read_graph('tu2017/graph.json')
    graph = read_graph('tu2017/graph_updated-neighbours-TKY.json')
    regions = read_regions('tu2017/regions-TKY.json')
    # cost_matrix = read_cost_matrix('cost_matrix_3.json')
    # merged = read_merged('tu2017/merged.json')

    # semantic
    semantic = get_venue_category(with_duration)

    graph, tu_trajectories = construct_graph(semantic)
    # write(tu_trajectories, 'tu2017/traj-test-TKY.json')
    # write(graph, 'tu2017/graph-TKY.json')
    new_graph, merged = graph.prune_and_simplify()
    # write(new_graph, 'tu2017/graph_updated-TKY.json')
    # write(merged, 'tu2017/merged-TKY.json')
    regions = {vertex.id: vertex for vertex in graph.vertices}
    # write(regions, 'tu2017/regions-TKY.json')
    update_ids(merged, tu_trajectories, regions)
    # write(tu_trajectories, 'tu2017/updated-ids-TKY.json')
    update_neighbours(graph, merged)
    # write(graph, 'tu2017/graph_updated-neighbours-TKY.json')
    create_cost_matrix(tu_trajectories, regions)


    # write
    # write(tu_trajectories, 'tu2017/semantic.json')

    # treat data
    print(f'anonymizing')
    k = 2
    l = 4
    t = 0.01
    rmv = get_removed()
    merging('tu2017/k2l4t001-anonymized-TKY.json', tu_trajectories, graph, k, l, t, regions, rmv)

    # k influence: k variando de 2 à 5; l=6 e t=0.01
    # l influence: k=2; l variando de 4 à 6; t='inf' (unconstrained)
    # t influence: k=2; l=6; t variando de 0.1 à 0.001


def get_removed():
    with open('tu2017/k2l4t001-anonymized-TKY.json', 'r') as f:
        ids = []
        for line in f.readlines():
            data = json.loads(line)
            ids.append(int(data['id']))
            ids.append(data['ids_merged'][0])

    return ids

# commitar a trajetória
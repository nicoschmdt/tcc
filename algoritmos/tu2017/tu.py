import csv
import math
import similarity
from geopy.distance import geodesic
# from dataclasses import dataclass
from networkx import Graph
from pprint import pprint
from numpy import argmax, argmin
from typing import List, Set

from algoritmos.tu2017.cost_matrix import add_trajectory_cost, remove_from_cost_matrix
from algoritmos.tu2017.treatData import construct_graph
from algoritmos.utils.graph import get_connected_region
from algoritmos.utils.semantic import SemanticTrajectory, SemanticPoint
from .algoritmos.trajetoria import process_trajectories, Point, Trajectory


def merging_trajectories(trajectories: list[SemanticTrajectory], merge_cost_matrix, delta_k: int):
    """
    """
    graph = construct_graph(trajectories)
    generalized_dataset = []

    while len(trajectories) > 2:

        i, j = argmin(merge_cost_matrix)

        # new trajectory
        tm = merge(trajectories[i], trajectories[j], graph)

        # delete
        delete(trajectories, trajectories[i], trajectories[j])
        merge_cost_matrix = remove_from_cost_matrix(merge_cost_matrix, i, j)

        if tm.n < delta_k:
            merge_cost_matrix = add_trajectory_cost(merge_cost_matrix, tm)
            trajectories.append(tm)
        else:
            generalized_dataset.append(tm)

    return generalized_dataset


def merge(trajectory: SemanticTrajectory, trajectory2: SemanticTrajectory, graph: Graph) -> SemanticTrajectory:
    # TODO: ver como receber os parametros delta L e delta T
    delta_l = 2
    delta_t = 0.5

    if len(trajectory.trajectory) > len(trajectory2.trajectory):
        bigger_trajectory = trajectory
        smaller_trajectory = trajectory2
    else:
        bigger_trajectory = trajectory2
        smaller_trajectory = trajectory

    # lista com tuplas sendo um ponto e a indicação de se esse ponto já foi mergeado
    points = [(point, False) for point in smaller_trajectory.trajectory]

    # junta todos os pontos da maior trajetoria na menor
    for point in bigger_trajectory.trajectory:
        chosen_point = get_smallest_merge_cost_partner(point, smaller_trajectory)
        # TODO: ver algum jeito de sinalizar que o chosen point na lista de points
        merged_point = merge_points(point, chosen_point, graph, delta_l, delta_t)
        # TODO: atualizar o merged point na bigger trajectory e em points

    # TODO: juntar os pontos não juntados da menor trajetoria nela mesma
    merged_points = []
    for point, merged in points:
        if merged:
            continue

    # TODO: conferir se os tempos entre os pontos adjacentes não se sobressaem
    return SemanticTrajectory(trajectory=merged_points,n=trajectory.n + trajectory2.n)


def get_smallest_merge_cost_partner(point: SemanticPoint, trajectory: SemanticTrajectory) -> SemanticPoint:
    """
    Encontra o ponto com o menor custo de junção em outra trajetória
    """
    pass


def merge_points(pointA: SemanticPoint, pointB: SemanticPoint, graph: Graph, delta_l: float, delta_t: float) -> SemanticPoint:
    """
    """

    tc = min(ta, tb)
    dc = max(ta + da, tb + db) - tc

    lc1 = get_connected_region(la, lb)

    while lc1 < delta_l:
        x = getNeighbours(lc1)
        for i in enumerate(len(x)):
            r = {lc1, x[i]}
            b[i] = delta_r

        i = argmax(b)
        lc1 = {lc1, x[i]}

    lc2 = lc1

    while lc2 < delta_t:
        x = getNeighbours(lc2)
        for i in enumerate(len(x)):
            r = {lc2, x[i]}
            b[i] = delta_r
        i = argmin(b)
        lc2 = {lc2, x[i]}

    lc = lc2


##### OLD

# merging two spatiotemporal points, returns a new Point of the merged locations
def merge_points(point_one, point_two, diversity_criteria, closeness_criteria, trajectories):
    timestamp1 = point_one.utc_timestamp
    timestamp2 = point_two.utc_timestamp
    # prob gotta turn this one like the utc_timestamp format
    timestamp = min(timestamp1, timestamp2)
    duration = max(point_one.duration + timestamp1,
                   point_two.duration + timestamp2)
    # location = get_connected_region(graph,point_one,point_two)
    duration -= timestamp
    location = point_one.venue_id | point_two.venue_id
    categories = point_one.venue_category_id | point_two.venue_category_id

    graph = generate_distance_graph([point
                                     for tr in trajectories
                                     for point in tr.trajectory])

    points = [point_one, point_two]
    diversity = get_diversity(location)

    while diversity < diversity_criteria:
        x = nearest_points(point_one, graph)
        B = []
        for x_i, _ in x:
            holder = location | x_i.venue_id
            B.append(get_diversity(holder))
        i = argmax(B)
        x_i, _ = x[i]
        location |= x_i.venue_id
        categories |= x_i.venue_category_id
        points.append(x_i)
        diversity = get_diversity(location)

    all_points = [graph.nodes[node]['point'] for node in graph.nodes] + points

    # arrumar
    closeness = get_closeness(points, all_points)
    tries = 0
    while closeness > closeness_criteria and tries < 100:
        x = nearest_points(point_one, graph)
        B = []
        for x_i, _ in x:
            holder_point = points + [x_i]
            B.append(get_closeness(holder_point, all_points))
        i = argmin(B)
        x_i, _ = x[i]
        location |= x_i.venue_id
        categories |= x_i.venue_category_id
        points.append(x_i)
        closeness = get_closeness(points, all_points)
        tries += 1

    # create new point
    new_point = Point(
        name=point_one.name,
        user_id='',
        venue_id=location,
        venue_category_id=categories,
        latitude=point_one.latitude,  # ver com a fernanda como fazer em relação a latitude
        longitude=point_one.longitude,  # e longitude dos pontos mergeados
        timezone_offset=point_one.timezone_offset,
        utc_timestamp=timestamp,
        duration=duration)

    return new_point


def nearest_points(point: Point, g: Graph, n: int = 10):
    point_a = point.name

    nearest = sorted(
        [
            (g.nodes[point_b]['point'], g.edges[point_a, point_b]['weight'])
            for point_b in g.nodes
        ], key=lambda k: k[1])
    return nearest[:n]


# get how many diverse venue_ids we have in a point
def get_diversity(places):
    return len(places)


def poi_distribution(points):
    m = {}
    for point in points:
        for category in point.venue_category_id:
            try:
                m[category] += 1
            except KeyError:
                m[category] = 1
    m_sum = sum(v for v in m.values())
    return {u: m[u] / m_sum for u in m}


# get how many diverse category_ids we have in a point
def get_closeness(r, R):
    x = poi_distribution(r)
    y = poi_distribution(R)
    return sum(x[u] * math.log(x[u] / y[u]) for u in x)


# merging trajectories // acho que vou precisar passar o graph tb..
# The algorithm will iterate until all the trajectories in T have been k-anonymized.
def merge_trajectories(trajectories: list[Trajectory], similarity_matrix, anonymity_criteria: int):
    generalized_dataset = []
    possible_to_merge = True  # depois penso em um nome melhor
    while possible_to_merge:  # enquanto tiver duas trajetorias com o k menor que o criterio
        k = argmax(similarity_matrix)  # os que tiverem a maior similaridade serão escolhidos
        i = k % len(similarity_matrix)
        j = k // len(similarity_matrix)
        new_trajectory = merge(trajectories[i], trajectories[j], trajectories)
        new_trajectory.n = trajectories[i].n + trajectories[j].n
        # tirando as trajetorias da lista de trajectories
        trajectories.pop(i)
        trajectories.pop(j - 1)
        # how do I remove things from the similarity matrix??
        remove_from(i, j, similarity_matrix)
        if new_trajectory.n < anonymity_criteria:
            # for trajectory in trajectories:
            add_similarity(similarity_matrix, trajectories, new_trajectory)
            trajectories.append(new_trajectory)
        else:
            generalized_dataset.append(new_trajectory)
        if len(trajectories) < 2:  # preciso pensar nessa condição aqui
            possible_to_merge = False
    return generalized_dataset


def remove_from(i, j, similarity_matrix):
    similarity_matrix.pop(i)
    similarity_matrix.pop(j - 1)
    for line in similarity_matrix:
        line.pop(i)
        line.pop(j - 1)


# calcular o custo dessa nova trajetoria com as já existentes e adicionar na sm
def add_similarity(matrix, trajectories, trajectory1):
    cost = []
    for trajectory in trajectories:
        cost.append(similarity.msm(trajectory, trajectory1))
    cost.append('-inf')
    i = 0
    for line in matrix:
        line.append(cost[i])
        i += 1
    matrix.append(cost)


def main(name, anonymity_criteria):
    trajectories = process_trajectories(name)
    # similarity_matrix = create_similarity_matrix(trajectories)
    # anonymized = merge_trajectories(trajectories,similarity_matrix,anonymity_criteria)


if __name__ == '__main__':
    main('resources/dataset_TSMC2014_TKY.csv', 3)

from pprint import pprint
from numpy import argmax, argmin

from algoritmos.tu2017 import cost_matrix
from algoritmos.tu2017.treat_data import construct_graph, TuPoint, TuTrajectory
from algoritmos.utils import region
from algoritmos.utils.graph import get_connected_region, Graph


def merging_trajectories(trajectories: list[TuTrajectory],
                         merge_cost_matrix: dict[TuTrajectory, list[tuple[float, TuTrajectory]]],
                         delta_k: int, delta_l: int, delta_t: float):
    """
    """
    graph = construct_graph(trajectories)
    generalized_dataset = []

    while len(trajectories) > 2:

        # ver como isso vai ser pego
        i, j = argmin(merge_cost_matrix)
        first_trajectory = trajectories[i]
        second_trajectory = trajectories[j]

        # new trajectory
        tm = merge(trajectories[i], trajectories[j], graph, delta_l, delta_t)

        trajectories.remove(first_trajectory)
        trajectories.remove(second_trajectory)
        merge_cost_matrix = cost_matrix.remove_from_cost_matrix(merge_cost_matrix, i)
        merge_cost_matrix = cost_matrix.remove_from_cost_matrix(merge_cost_matrix, j)

        if tm.n < delta_k:
            merge_cost_matrix = cost_matrix.add_trajectory_cost(merge_cost_matrix, tm)
            trajectories.append(tm)
        else:
            generalized_dataset.append(tm)

    return generalized_dataset


def merge(trajectory: TuTrajectory, trajectory2: TuTrajectory, graph: Graph, delta_l: int,
          delta_t: float) -> TuTrajectory:
    """
    Identifica qual das duas trajetórias possui a maior quantidade de pontos.
    """
    if len(trajectory.trajectory) > len(trajectory2.trajectory):
        return merge_trajectories(trajectory, trajectory2, graph, delta_l, delta_t)
    return merge_trajectories(trajectory2, trajectory, graph, delta_l, delta_t)


def merge_trajectories(bigger_trajectory: TuTrajectory, smaller_trajectory: TuTrajectory, graph: Graph,
                       delta_l: int, delta_t: float) -> TuTrajectory:
    """
    """
    points = [(index, False) for index, _ in enumerate(smaller_trajectory.trajectory)]

    for point in bigger_trajectory.trajectory:
        chosen_point, _ = get_smallest_merge_cost_partner(point, smaller_trajectory.trajectory)
        merged_point, index = merge_points(point, chosen_point, graph, delta_l, delta_t)
        smaller_trajectory.trajectory[index] = merged_point
        points[index] = (index, True)

    altered_points = merge_remaining_points(smaller_trajectory, points, graph, delta_l, delta_t)

    semantic_trajectory = TuTrajectory(trajectory=altered_points, n=bigger_trajectory.n + smaller_trajectory.n)
    semantic_trajectory.reshape()
    return semantic_trajectory


def merge_remaining_points(trajectory: TuTrajectory, point_status: list[tuple[int, bool]], graph: Graph, delta_l: int, delta_t: float) -> list[TuPoint]:
    """
    Une os pontos que ainda não foram alterados da menor trajetória
    com o ponto com o menor custo de junção de si mesmo.
    """
    altered_points = trajectory.trajectory.copy()
    for index, merged in point_status:
        if not merged:
            actual_point = trajectory.trajectory[index]
            chosen_point, point_index = get_smallest_merge_cost_partner(actual_point, altered_points, trajectory.n)
            merge_point, _ = merge_points(actual_point, chosen_point, graph, delta_l, delta_t)
            altered_points[index] = merge_point
            altered_points.pop(point_index)

    return altered_points


def get_smallest_merge_cost_partner(point: TuPoint, trajectory: list[TuPoint], n: int) -> (TuPoint, int):
    """
    Encontra o ponto com o menor custo de junção em outra trajetória e retorna ele junto de seu indice.
    """

    cost = []
    for index, point_b in enumerate(trajectory):
        if point == point_b:
            continue

        cost.append((point_b, cost_matrix.point_loss(point, point_b, n, n), index))

    chosen_point, _, index = min(cost, key=lambda tup: tup[1])
    return chosen_point, index


def merge_points(point_a: TuPoint, point_b: TuPoint, graph: Graph, delta_l: float,
                 delta_t: float) -> TuPoint:
    """
    Unir dois pontos espaço-temporais resulta em um novo
    ponto com inicio e duração atualizados e que respeita
    os critérios de l-diversidade e t-proximidade.
    """
    tc, duration = cost_matrix.join_spacetime(point_a, point_b)

    lc = get_connected_region(graph, point_a.region, point_b.region)

    while lc.get_diversity() < delta_l:
        diversities = {}
        for neighbour in lc.neighbours:
            diversity = region.get_possible_diversity(lc, neighbour)
            diversities[neighbour] = diversity

        lc.join_region(argmax(diversities))

    while lc.get_closeness(graph.poi_distribution) < delta_t:
        closeness_values = {}
        for neighbour in lc.neighbours:
            closeness = region.get_possible_closeness(lc, neighbour, graph.poi_distribution)
            closeness_values[neighbour] = closeness

        lc.join_region(argmin(closeness_values))

    return TuPoint(
        utc_timestamp=tc,
        duration=duration,
        region=lc
    )


def main(name, anonymity_criteria):
    pass
    # trajectories = process_trajectories(name)
    # similarity_matrix = create_similarity_matrix(trajectories)
    # anonymized = merge_trajectories(trajectories,similarity_matrix,anonymity_criteria)


if __name__ == '__main__':
    main('resources/dataset_TSMC2014_TKY.csv', 3)

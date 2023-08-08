from pprint import pprint
from numpy import argmax, argmin

from algoritmos.tu2017 import cost_matrix
from algoritmos.tu2017.treatData import construct_graph
from algoritmos.utils import region
from algoritmos.utils.graph import get_connected_region, Graph
from algoritmos.utils.semantic import SemanticTrajectory, SemanticPoint


def merging_trajectories(trajectories: list[SemanticTrajectory],
                         merge_cost_matrix: dict[SemanticTrajectory, list[tuple[float, SemanticTrajectory]]],
                         delta_k: int, delta_l: int, delta_t: float):
    """
    """
    graph = construct_graph(trajectories)
    generalized_dataset = []

    while len(trajectories) > 2:

        # ver como isso vai ser pego
        i, j = argmin(merge_cost_matrix)

        # new trajectory
        tm = merge(trajectories[i], trajectories[j], graph, delta_l, delta_t)

        # delete
        delete(trajectories, trajectories[i], trajectories[j])
        merge_cost_matrix = cost_matrix.remove_from_cost_matrix(merge_cost_matrix, i)
        merge_cost_matrix = cost_matrix.remove_from_cost_matrix(merge_cost_matrix, j)

        if tm.n < delta_k:
            merge_cost_matrix = cost_matrix.add_trajectory_cost(merge_cost_matrix, tm)
            trajectories.append(tm)
        else:
            generalized_dataset.append(tm)

    return generalized_dataset


def merge(trajectory: SemanticTrajectory, trajectory2: SemanticTrajectory, graph: Graph, delta_l: int,
          delta_t: float) -> SemanticTrajectory:
    """
    Identifica qual das duas trajetórias possui a maior quantidade de pontos.
    """
    if len(trajectory.trajectory) > len(trajectory2.trajectory):
        return merge_trajectories(trajectory, trajectory2, graph, delta_l, delta_t)
    return merge_trajectories(trajectory2, trajectory, graph, delta_l, delta_t)


def merge_trajectories(bigger_trajectory: SemanticTrajectory, smaller_trajectory: SemanticTrajectory, graph: Graph,
                       delta_l: int, delta_t: float) -> SemanticTrajectory:
    """
    Then we pick out the unmerged points of 𝑇𝑗 and merge them into
    one of the rest merged points in 𝑇𝑗 . At last, we carry out a
    reshaping operation to avoid time overlap between adjacent points
    Ti = bigger_trajectory
    """
    points = [(index, False) for index in enumerate(smaller_trajectory.trajectory)]

    for point in bigger_trajectory.trajectory:
        chosen_point = get_smallest_merge_cost_partner(point, smaller_trajectory)
        merged_point, index = merge_points(point, chosen_point, graph, delta_l, delta_t)
        smaller_trajectory.trajectory[index] = merged_point
        points[index] = (index, True)

    # TODO: juntar os pontos não juntados da menor trajetoria nela mesma
    merged_points = []
    for point, merged in points:
        if merged:
            continue

    semantic_trajectory = SemanticTrajectory(trajectory=merged_points, n=bigger_trajectory.n + smaller_trajectory.n)
    semantic_trajectory.reshape()
    return semantic_trajectory


def get_smallest_merge_cost_partner(point: SemanticPoint, trajectory: SemanticTrajectory) -> (SemanticPoint, int):
    """
    Encontra o ponto com o menor custo de junção em outra trajetória e retorna ele junto de seu indice.
    """
    pass


def merge_points(point_a: SemanticPoint, point_b: SemanticPoint, graph: Graph, delta_l: float,
                 delta_t: float) -> SemanticPoint:
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

    return SemanticPoint(
        name='',
        user_id='',
        utc_timestamp=tc,
        duration=duration,
        region=lc
    )


##### OLD
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


def main(name, anonymity_criteria):
    pass
    # trajectories = process_trajectories(name)
    # similarity_matrix = create_similarity_matrix(trajectories)
    # anonymized = merge_trajectories(trajectories,similarity_matrix,anonymity_criteria)


if __name__ == '__main__':
    main('resources/dataset_TSMC2014_TKY.csv', 3)

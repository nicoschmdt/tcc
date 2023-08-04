from algoritmos.tu2017 import similarity
from algoritmos.utils.semantic import SemanticTrajectory


def create_cost_matrix(trajectories: list[SemanticTrajectory]) -> dict[
    SemanticTrajectory, list[tuple[float, SemanticTrajectory]]]:
    """
    Cria a matriz de custo C.
    Como Cij == Cji a matriz é preenchida somente na parte superior
    e a parte inferior é copiada da superior já existente
    """

    matrix = {}
    for i, trajectory_one in enumerate(trajectories):
        cost_list = []

        for trajectory_accounted in matrix.keys():
            for trajectory_passed, value in matrix[trajectory_accounted]:
                if trajectory_passed == trajectory_one:
                    cost_list.append((value, trajectory_accounted))

        for j, trajectory_two in enumerate(trajectories[i:]):
            if trajectory_one != trajectory_two:
                cost = similarity.get_loss(trajectory_one, trajectory_two)
                cost_list.append((cost, trajectory_two))

        matrix[trajectory_one] = cost_list
    return matrix


def add_trajectory_cost(matrix: dict[SemanticTrajectory, list[tuple[float, SemanticTrajectory]]],
                        trajectory: SemanticTrajectory) -> dict[
    SemanticTrajectory, list[tuple[float, SemanticTrajectory]]]:
    """
    Adiciona uma trajetória a uma matriz de custo e calcula o custo de junção
    dessa trajetória com todas as outras presentes na matriz
    """

    cost_list = []
    for matrix_trajectory in matrix.keys():
        cost = similarity.get_loss(matrix_trajectory, trajectory)
        cost_list.append((cost, matrix_trajectory))
        matrix[matrix_trajectory].append((cost, trajectory))

    matrix[trajectory] = cost_list
    return matrix


def remove_from_cost_matrix(matrix: dict[SemanticTrajectory, list[tuple[float, SemanticTrajectory]]],
                            trajectory: SemanticTrajectory) -> dict[
    SemanticTrajectory, list[tuple[float, SemanticTrajectory]]]:
    """
    Remove da matriz de custo a trajetória recebida por parametro.
    """

    matrix.pop(trajectory)

    for matrix_trajectory in matrix.keys():
        new_list = [(cost, traj) for (cost, traj) in matrix[matrix_trajectory] if traj != trajectory]
        matrix[matrix_trajectory] = new_list

    return matrix

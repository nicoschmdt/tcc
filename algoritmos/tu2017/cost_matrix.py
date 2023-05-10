from algoritmos.tu2017.similarity import spatio_temporal_loss
from algoritmos.utils.semantic import SemanticTrajectory


def create_cost_matrix(trajectories: list[SemanticTrajectory], weights: dict[str, int]):
    """
    Cria a matriz de custo C.
    Como Cij == Cji a matriz é preenchida somente na parte superior
    e a parte inferior é copiada da superior já existente
    """
    matrix = []
    for i, trajectory_one in enumerate(trajectories):
        lista = []

        for j in range(i):
            lista.append(matrix[j][i])

        for j, trajectory_two in enumerate(trajectories[i:]):
            if trajectory_one == trajectory_two:
                lista.append(float('inf'))
            else:
                cost = spatio_temporal_loss(trajectory_one, trajectory_two, weights)
                # lista.append(msm(trajectory_one,trajectory_two)) # -> fazer
                lista.append(cost)
        matrix.append(lista)
    return matrix


def add_trajectory_cost(matrix, trajectory: SemanticTrajectory):
    """
    Adiciona uma trajetória a uma matriz de custo e calcula o custo de junção
    dessa trajetória com todas as outras presentes na matriz
    """
    pass


def remove_from_cost_matrix(matrix, i: int, j: int):
    """
    Remove da matriz de custo o índice i e o índice j
    """
    pass

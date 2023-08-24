from datetime import timedelta, datetime, timezone

from algoritmos.tu2017.treat_data import TuPoint, TuTrajectory
from algoritmos.utils.semantic import PoiCategory


def create_cost_matrix(trajectories: list[TuTrajectory]) -> dict[TuTrajectory, list[tuple[float, TuTrajectory]]]:
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
                cost = get_loss(trajectory_one, trajectory_two)
                cost_list.append((cost, trajectory_two))

        matrix[trajectory_one] = cost_list
    return matrix


def add_trajectory_cost(matrix: dict[TuTrajectory, list[tuple[float, TuTrajectory]]],
                        trajectory: TuTrajectory) -> dict[TuTrajectory, list[tuple[float, TuTrajectory]]]:
    """
    Adiciona uma trajetória a uma matriz de custo e calcula o custo de junção
    dessa trajetória com todas as outras presentes na matriz
    """

    cost_list = []
    for matrix_trajectory in matrix.keys():
        cost = get_loss(matrix_trajectory, trajectory)
        cost_list.append((cost, matrix_trajectory))
        matrix[matrix_trajectory].append((cost, trajectory))

    matrix[trajectory] = cost_list
    return matrix


def remove_from_cost_matrix(matrix: dict[TuTrajectory, list[tuple[float, TuTrajectory]]],
                            trajectory: TuTrajectory) -> dict[TuTrajectory, list[tuple[float, TuTrajectory]]]:
    """
    Remove da matriz de custo a trajetória recebida por parametro.
    """

    matrix.pop(trajectory)

    for matrix_trajectory in matrix.keys():
        new_list = [(cost, traj) for (cost, traj) in matrix[matrix_trajectory] if traj != trajectory]
        matrix[matrix_trajectory] = new_list

    return matrix


def get_loss(trajectory_a: TuTrajectory, trajectory_b: TuTrajectory) -> float:
    #  Si > Sj
    if len(trajectory_a.trajectory) > len(trajectory_b.trajectory):
        return spatio_temporal_loss(trajectory_a, trajectory_b)
    #  Si <= Sj
    return spatio_temporal_loss(trajectory_b, trajectory_a)


def spatio_temporal_loss(bigger_trajectory: TuTrajectory, smaller_trajectory: TuTrajectory) -> float:
    """
    Calcula a perda espaço-temporal entre duas trajetórias.
    Assume que a trajetória com mais pontos é o primeiro
    argumento.
    """

    cost = 0
    for point_bigger in bigger_trajectory.trajectory:
        possible_match = []
        for point_smaller in smaller_trajectory.trajectory:
            possible_match.append(point_loss(point_bigger, point_smaller, bigger_trajectory.n, smaller_trajectory.n))
        cost += min(possible_match)

    return cost / len(bigger_trajectory.trajectory)


def point_loss(point_a: TuPoint, point_b: TuPoint, n_a: int, n_b: int) -> float:
    """
    Args: n_a e n_b são a quantidade de trajetórias presentes na trajetória recebida anteriormente, é o parametro n
    Calcula a perda espaço-temporal da junção de dois pontos
    **** lembrete que preciso considerar que se a diferença de tempo entre dois pontos for > 8 horas a perda é total
    """

    wt, wl = 0.5, 0.5
    t_loss = temporal_loss(point_a, point_b, n_a, n_b)
    s_loss = spatial_loss(point_a, point_b, n_a, n_b)

    return wt * t_loss + wl * s_loss


def join_spacetime(point_a: TuPoint, point_b: TuPoint) -> (datetime, timedelta):
    """
    Calcula o novo tempo de inicio e de duração entre dois datetimes.
    """
    init_a = point_a.utc_timestamp
    init_b = point_b.utc_timestamp

    if init_a < init_b:
        init = init_a
    else:
        init = init_b

    end_time_a = init_a + point_a.duration
    end_time_b = init_b + point_b.duration
    if end_time_a < end_time_b:
        duration = end_time_b - init
    else:
        duration = end_time_a - init

    return init, duration


def temporal_loss(point_a: TuPoint, point_b: TuPoint, n_a: int, n_b: int) -> float:
    """
    Calcula a perda temporal da junção de dois pontos
    0Tm = 8 horas
    0T* = (dc - da)*ni + (dc - db)*nj /(ni+nj)
    0T = min((0T*/0Tm), 1)
    """
    temporal_threshold = 28800  # 8 horas
    _, duration = join_spacetime(point_a, point_b)

    theta = ((duration - point_a.duration) * n_a + (duration - point_b.duration) * n_b) / (n_a + n_b)
    return min(theta / temporal_threshold, 1)


def spatial_loss(point_a: TuPoint, point_b: TuPoint, n_a: int, n_b: int) -> float:
    """
    Calcula a perda espacial da junção de dois pontos
    0Lm = 25km²
    Sl = spatial area of location l -> tipo area de 2 metros quadrados
    0L* = (Slc - Sla) * ni + (Slc - Slb) * nj
    0L = min(0L* / 0Lm, 1)
    """
    spatial_threshold = 25000  # 25km²
    area = point_a.region.area + point_b.region.area

    theta = ((area - point_a.region.area) * n_a + (area - point_b.region.area) * n_b) / (n_a + n_b)
    return min(theta / spatial_threshold, 1)


if __name__ == "__main__":
    a = TuPoint(category={PoiCategory.Business}, latitude=0.0, longitude=0.0,
                utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc),
                duration=timedelta(seconds=3600))
    b = TuPoint(category={PoiCategory.Transport}, latitude=9.0, longitude=8.0,
                utc_timestamp=datetime(2012, 4, 3, 19, 30, tzinfo=timezone.utc), duration=timedelta(0))

    a_initPoint = a.utc_timestamp
    print(f'{a_initPoint=}')
    a_endPoint = a_initPoint + a.duration
    print(f'{a_endPoint=}')
    b_initPoint = b.utc_timestamp
    print(f'{b_initPoint=}')
    b_endPoint = b_initPoint + b.duration
    print(f'{b_endPoint=}')

    # d = calculate_new_duration(a_endPoint, b_endPoint)
    print(join_spacetime(a, b))
    # print(d)

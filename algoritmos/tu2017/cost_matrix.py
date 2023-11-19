from datetime import timedelta, datetime

from algoritmos.tu2017.treat_data import TuPoint, TuTrajectory
from algoritmos.tu2017.region import Region
from algoritmos.utils.io import write


def create_cost_matrix(trajectories: list[TuTrajectory], regions) -> None:
    """
    Cria a matriz de custo C.
    Como Cij == Cji a matriz é preenchida somente na parte superior
    e a parte inferior é copiada da superior já existente
    """

    matrix = {}
    part = 1
    for i, trajectory_one in enumerate(trajectories[:-1]):
        # verificar se o tam do matrix tá grande demais, salvar e resetar
        print(f'{i}/{len(trajectories)-1}')
        if i == (2000*part):
            write(matrix, f'cost_matrix_{part}.json')
            part += 1
            matrix = {}
        cost_list = []
        for j, trajectory_two in enumerate(trajectories[i:]):
            if trajectory_one == trajectory_two:
                continue

            end = trajectory_one.points[-1].utc_timestamp
            init = trajectory_two.points[0].utc_timestamp
            if init > end:
                d = init - end
            else:
                end = trajectory_one.points[0].utc_timestamp
                init = trajectory_two.points[-1].utc_timestamp
                d = init - end

            if d.total_seconds() < timedelta(hours=8).total_seconds():
                cost = get_loss(trajectory_one, trajectory_two, regions)
                cost_list.append((cost, trajectory_two.id))

        matrix[trajectory_one.id] = cost_list

    write(matrix, f'tu2017/cost_matrix_{part}.json')


def add_trajectory_cost(matrix: dict[int, list[tuple[float, int]]], trajectory: TuTrajectory, regions, compendium) -> None:
    """
    Adiciona uma trajetória a uma matriz de custo e calcula o custo de junção
    dessa trajetória com todas as outras presentes na matriz
    """

    cost_list = []
    for matrix_traj_id in matrix.keys():
        cost = get_loss(compendium[matrix_traj_id], trajectory, regions)
        cost_list.append((cost, matrix_traj_id))

    matrix[trajectory.id] = cost_list


def remove(matrix: dict[int, list[tuple[float, int]]], tid: int) -> None:
    """
    Remove da matriz de custo a trajetória recebida por parametro.
    """

    if tid in matrix.keys():
        matrix.pop(tid)

    for matrix_trajectory in matrix.keys():
        new_list = [(cost, traj) for (cost, traj) in matrix[matrix_trajectory] if traj != tid]
        matrix[matrix_trajectory] = new_list


def merge_matrix(matrix1, matrix2) -> None:
    for tid, costs in matrix1.items():
        matrix2[tid] = costs


def clean(matrix: dict[int, list[tuple[float, int]]], removed: set[int]) -> dict[int, list[tuple[float, int]]]:
    cleaned = {}
    for traj_id, costs in matrix.items():
        if traj_id not in removed:
            cleaned[traj_id] = [(value, tid) for value, tid in costs if tid not in removed]
    return cleaned


def get_loss(trajectory_a: TuTrajectory, trajectory_b: TuTrajectory, regions) -> float:
    #  Si > Sj
    if len(trajectory_a.points) > len(trajectory_b.points):
        return spatio_temporal_loss(trajectory_a, trajectory_b, regions)
    #  Si <= Sj
    return spatio_temporal_loss(trajectory_b, trajectory_a, regions)


def spatio_temporal_loss(bigger_trajectory: TuTrajectory, smaller_trajectory: TuTrajectory, regions) -> float:
    """
    Calcula a perda espaço-temporal entre duas trajetórias.
    Assume que a trajetória com mais pontos é o primeiro
    argumento.
    """

    cost = 0
    for point_bigger in bigger_trajectory.points:
        possible_match = []
        for point_smaller in smaller_trajectory.points:
            possible_match.append(point_loss(point_bigger, point_smaller, bigger_trajectory.n, smaller_trajectory.n, regions))
        cost += min(possible_match)

    return cost / len(bigger_trajectory.points)


def point_loss(point_a: TuPoint, point_b: TuPoint, n_a: int, n_b: int, regions) -> float:
    """
    Args: n_a e n_b são a quantidade de trajetórias presentes na trajetória recebida anteriormente, é o parametro n
    Calcula a perda espaço-temporal da junção de dois pontos
    **** lembrete que preciso considerar que se a diferença de tempo entre dois pontos for > 8 horas a perda é total
    """

    wt, wl = 0.5, 0.5
    t_loss = temporal_loss(point_a, point_b, n_a, n_b)
    s_loss = spatial_loss(point_a, point_b, n_a, n_b, regions)

    return wt * t_loss + wl * s_loss


def join_spacetime(point_a: TuPoint, point_b: TuPoint) -> tuple[datetime, timedelta]:
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
    temporal_threshold = timedelta(hours=8)  # 8 horas
    _, duration = join_spacetime(point_a, point_b)

    theta = (((duration - point_a.duration) * n_a + (duration - point_b.duration) * n_b) / (n_a + n_b)).total_seconds()
    return min(theta / temporal_threshold.total_seconds(), 1)


def spatial_loss(point_a: TuPoint, point_b: TuPoint, n_a: int, n_b: int, regions: dict[int, Region]) -> float:
    """
    Calcula a perda espacial da junção de dois pontos
    0Lm = 25km²
    Sl = spatial area of location l -> tipo area de 2 metros quadrados
    0L* = (Slc - Sla) * ni + (Slc - Slb) * nj
    0L = min(0L* / 0Lm, 1)
    """
    spatial_threshold = 25000  # 25km²
    area_a = sum([regions[reg_id].area for reg_id in point_a.region_id])
    area_b = sum([regions[reg_id].area for reg_id in point_b.region_id])
    area = area_a + area_b

    theta = ((area - area_a) * n_a + (area - area_b) * n_b) / (n_a + n_b)
    return min(theta / spatial_threshold, 1)


def get_min_merge_cost(cost_matrix: dict[int, list[tuple[float, int]]]) -> \
        tuple[int, int]:
    minimal_cost_found = 1.0  # maximal cost
    traj1 = None
    traj2 = None

    for trajectory_id in cost_matrix.keys():
        for cost, candidate in cost_matrix[trajectory_id]:
            if cost < minimal_cost_found:
                minimal_cost_found = cost
                traj1 = trajectory_id
                traj2 = candidate

    print(f'cost={minimal_cost_found}')
    return traj1, traj2

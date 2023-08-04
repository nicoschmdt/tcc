from algoritmos.utils.semantic import SemanticPoint, PoiCategory, SemanticTrajectory
from datetime import timedelta, datetime, timezone


def get_loss(trajectory_a: SemanticTrajectory, trajectory_b: SemanticTrajectory) -> float:
    #  Si > Sj
    if len(trajectory_a.trajectory) > len(trajectory_b.trajectory):
        return spatio_temporal_loss(trajectory_a, trajectory_b)
    #  Si <= Sj
    return spatio_temporal_loss(trajectory_b, trajectory_a)


def spatio_temporal_loss(bigger_trajectory: SemanticTrajectory, smaller_trajectory: SemanticTrajectory) -> float:
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

    return cost/len(bigger_trajectory.trajectory)


def point_loss(point_a: SemanticPoint, point_b: SemanticPoint, n_a: int, n_b: int) -> float:
    """
    Args: n_a e n_b são a quantidade de trajetórias presentes na trajetória recebida anteriormente, é o parametro n
    Calcula a perda espaço-temporal da junção de dois pontos
    **** lembrete que preciso considerar que se a diferença de tempo entre dois pontos for > 8 horas a perda é total
    """

    wt, wl = 0.5, 0.5
    t_loss = temporal_loss(point_a, point_b, n_a, n_b)
    s_loss = spatial_loss(point_a, point_b, n_a, n_b)

    return wt * t_loss + wl * s_loss


def join_spacetime(point_a: SemanticPoint, point_b: SemanticPoint) -> (datetime, timedelta):
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


def temporal_loss(point_a: SemanticPoint, point_b: SemanticPoint, n_a: int, n_b: int) -> float:
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


def spatial_loss(point_a: SemanticPoint, point_b: SemanticPoint, n_a: int, n_b: int) -> float:
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
    return min(theta/spatial_threshold, 1)


if __name__ == "__main__":
    a = SemanticPoint(name='10', user_id='1', category={PoiCategory.Business}, latitude=0.0, longitude=0.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc),
                      duration=timedelta(seconds=3600))
    b = SemanticPoint(name='12', user_id='2', category={PoiCategory.Transport}, latitude=9.0, longitude=8.0,
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

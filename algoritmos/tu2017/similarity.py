from .treatData import PoiCategory, SemanticTrajectory, SemanticPoint
from datetime import timedelta, datetime, timezone
from geopy.distance import geodesic


# 10 and 0.5 are thresholds
# preciso entender o que esse método faz e como faz
# eu sei que ele ve a similaridade entre duas trajetorias
def msm(trajectory_a: SemanticTrajectory, trajectory_b: SemanticTrajectory):
    results = []
    for point_a in trajectory_a.trajectory:
        line = []
        for point_b in trajectory_b.trajectory:
            variable = 0
            if distance(point_a, point_b) < 2:
                variable = 1
            if time(point_a, point_b) < 0.5:
                variable += 1
            if semantics(point_a, point_b) >= 0.5:
                variable += 1
            line.append(variable / 3)
        results.append(line)
    ab, ba = score(results)
    return (ab + ba) / (len(trajectory_a.trajectory) + len(trajectory_b.trajectory))


def score(matrix):
    sum_max_line = 0
    sum_max_column = 0
    for line in matrix:
        sum_max_line += max(line)
    for i in range(len(matrix[0])):
        max_column = matrix[0][i]
        for line in matrix[1:]:
            max_column = max(max_column, line[i])
        sum_max_column += max_column
    return sum_max_line, sum_max_column


# space dimension
def distance(a, b):
    coordinate_one = (a.latitude, a.longitude)
    coordinate_two = (b.latitude, b.longitude)
    return geodesic(coordinate_one, coordinate_two).miles


# time dimension
def time(a: SemanticPoint, b: SemanticPoint) -> float:
    tempo2_a = a.utc_timestamp + a.duration
    tempo2_b = b.utc_timestamp + b.duration
    if tempo2_a < b.utc_timestamp or tempo2_b < a.utc_timestamp:
        return 1
    numerador = diam(max(a.utc_timestamp, tempo2_a), min(b.utc_timestamp, tempo2_b))
    divisor = diam(min(a.utc_timestamp, b.utc_timestamp), max(tempo2_a, tempo2_b))
    if divisor == timedelta(hours=0):
        return 1
    return 1 - (numerador / divisor)


def diam(a, b):
    return abs(b - a)


# semantic dimension
def semantics(a, b):
    if a.venue_category_id.intersection(b.venue_category_id):
        return 1
    return 0


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


def spatio_temporal_loss(trajectory_a: SemanticTrajectory, trajectory_b: SemanticTrajectory, weights: dict[str, int]):
    """
    Calcula a perda espaço-temporal entre duas trajetórias
    """

    pass


def point_loss(point_a: SemanticPoint, point_b: SemanticPoint, n_a: int, n_b: int):
    """
    Args: n_a e n_b são a quantidade de trajetórias presentes na trajetória recebida anteriormente, é o parametro n
    Calcula a perda espaço-temporal da junção de dois pontos
    **** lembrete que preciso considerar que se a diferença de tempo entre dois pontos for > 8 horas a perda é total
    """

    wt, wl = 0.5
    temporal_loss = temporal_loss(point_a, point_b, n_a, n_b)
    spatial_loss = spatial_loss(point_a, point_b, n_a, n_b)

    return wt * temporal_loss + wl * spatial_loss


def calculate_new_duration(point_a: datetime, point_b: datetime) -> datetime:
    """
    Calcula o novo intervalo de tempo que iria resultar da junção de dois pontos
    Considera-se que a diferença de tempo entre os dois pontos é menor que 8 horas -> acho que a diferença de tempo poderia ser menor, tipo 2/3 horas
    """

    if point_a <= point_b:
        return point_b

    return point_a


def temporal_loss(point_a: SemanticPoint, point_b: SemanticPoint, n_a: int, n_b: int):
    """
    Calcula a perda temporal da junção de dois pontos
    0Tm = 8 horas
    0T* = (dc - da)*ni + (dc - db)*nj
    0T = min((0T*/(ni+nj)/0Tm), 1)
    """

    a_initPoint = point_a.utc_timestamp
    a_endPoint = a_initPoint + point_a.duration
    b_initPoint = point_b.utc_timestamp
    b_endPoint = b_initPoint + point_b.duration

    duration_c = calculate_new_duration(a_endPoint, b_endPoint)

    teta_star = ((duration_c - a_endPoint) * n_a + (duration_c - b_endPoint) * n_b) / (n_a + n_b)

    return min(teta_star, 1)


def spatial_loss(point_a: SemanticPoint, point_b: SemanticPoint, n_a: int, n_b: int):
    """
    Calcula a perda espacial da junção de dois pontos
    0Lm = 25km²
    Sl = spatial area of location l
    0L* = (Slc - Sla) * ni + (Slc - Slb) * nj
    0L = min(0L* / 0Lm, 1)
    """

    pass


if __name__ == "__main__":
    a = SemanticPoint(name='10', user_id='1', category={PoiCategory.Business}, latitude=0.0, longitude=0.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(seconds=3600))
    b = SemanticPoint(name='12', user_id='2', category={PoiCategory.Transport}, latitude=9.0, longitude=8.0,
                      utc_timestamp=datetime(2012, 4, 3, 19, 30, tzinfo=timezone.utc), duration=timedelta(0))

    a_initPoint = a.utc_timestamp
    a_endPoint = a_initPoint + a.duration
    b_initPoint = b.utc_timestamp
    b_endPoint = b_initPoint + b.duration

    d = calculate_new_duration(a_endPoint, b_endPoint)
    # print(d)

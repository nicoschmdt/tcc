from algoritmos.tu2017 import cost_matrix
from algoritmos.tu2017.treat_data import TuPoint, TuTrajectory
from algoritmos.tu2017.graph import get_connected_region, Graph
from algoritmos.tu2017.region import Region, calculate_diversity, get_closeness
from algoritmos.utils import io
from algoritmos.utils.io import read_costs


def merging(name: str, trajectories: list[TuTrajectory], graph,
            delta_k: int, delta_l: int, delta_t: float, regions, removed: list[int] = None, next_m: int = 1):
    compendium = {trajectory.id: trajectory for trajectory in trajectories}
    merge_cost = read_costs(f'tu2017/cost_matrix_{next_m}.json')

    if removed:
        for tid in removed:
            cost_matrix.remove(merge_cost, tid)

    removed_ids = set()

    print('anonymizing')
    while len(trajectories) > 2 or len(merge_cost) > 2:
        if len(merge_cost) <= 500 and next_m < 8:
            next_matrix = cost_matrix.clean(read_costs(f'tu2017/cost_matrix_{next_m}.json'), removed_ids)
            cost_matrix.merge_matrix(merge_cost, next_matrix)  # considerando apenas k=2
            merge_cost = next_matrix
            next_m += 1
            removed_ids = set()

        print(f'{len(trajectories)=}')
        first_id, second_id = cost_matrix.get_min_merge_cost(merge_cost)
        print(f'{first_id=}, {second_id=}')
        first = compendium[first_id]
        second = compendium[second_id]

        # new trajectory
        tm = merge(first, second, graph, delta_l, delta_t, regions)

        trajectories.remove(first)
        trajectories.remove(second)
        cost_matrix.remove(merge_cost, first_id)
        cost_matrix.remove(merge_cost, second_id)
        removed_ids |= {first_id, second_id}

        if tm.n < delta_k:
            print(f'new id: {tm.id}')
            compendium[tm.id] = tm
            cost_matrix.add_trajectory_cost(merge_cost, tm, regions, compendium)
            trajectories.append(tm)
        else:
            io.append(tm, name)


def merge(trajectory: TuTrajectory, trajectory2: TuTrajectory, graph: Graph, delta_l: int,
          delta_t: float, regions) -> TuTrajectory:
    """
    Identifica qual das duas trajetórias possui a maior quantidade de pontos.
    """
    if len(trajectory.points) > len(trajectory2.points):
        return merge_trajectories(trajectory, trajectory2, graph, delta_l, delta_t, regions)
    return merge_trajectories(trajectory2, trajectory, graph, delta_l, delta_t, regions)


def merge_trajectories(bigger: TuTrajectory, smaller: TuTrajectory, graph: Graph,
                       delta_l: int, delta_t: float, regions) -> TuTrajectory:
    """
    """
    uid = bigger.uid
    uid.extend(smaller.uid)
    points = [(index, False) for index, _ in enumerate(smaller.points)]

    for point in bigger.points:
        chosen_point, index = smallest_merge_cost(point, smaller.points, bigger.n, smaller.n, regions)
        merged_point = merge_points(point, chosen_point, graph, delta_l, delta_t, regions)
        smaller.points[index] = merged_point
        points[index] = (index, True)

    altered_points = merge_remaining_points(smaller, points, bigger.n, graph, delta_l, delta_t, regions)

    n = bigger.n + smaller.n
    ids = bigger.ids_merged.copy() | {smaller.id}
    semantic_trajectory = TuTrajectory(uid=uid, id=bigger.id, points=altered_points, n=n, ids_merged=ids)
    semantic_trajectory.reshape()
    return semantic_trajectory


def merge_remaining_points(trajectory: TuTrajectory, status: list[tuple[int, bool]], big_n: int, graph: Graph,
                           delta_l: int, delta_t: float, regions) -> list[TuPoint]:
    """
    Une os pontos que ainda não foram alterados da menor trajetória
    com o ponto com o menor custo de junção de si mesmo.
    """
    altered_points = trajectory.points.copy()
    enumerated_pts = {index for index, stat in status if stat is True}
    for index, merged in status:
        if index not in enumerated_pts:
            actual_point = trajectory.points[index]
            chosen_point, point_index = smallest_merge_cost(actual_point, altered_points, big_n, trajectory.n, regions)
            merge_point = merge_points(actual_point, chosen_point, graph, delta_l, delta_t, regions)
            altered_points[point_index] = merge_point
            enumerated_pts |= {index, point_index}

    return altered_points


def smallest_merge_cost(point: TuPoint, points: list[TuPoint], big_n: int, small_n: int, regions) \
        -> tuple[TuPoint, int]:
    """
    Encontra o ponto com o menor custo de junção em outra trajetória e retorna ele junto de seu indice.
    """

    cost = []
    for index, point_b in enumerate(points):
        if point == point_b:
            continue

        cost.append((point_b, cost_matrix.point_loss(point, point_b, big_n, small_n, regions), index))

    chosen_point, _, index = min(cost, key=lambda tup: tup[1])
    return chosen_point, index


def merge_points(point_a: TuPoint, point_b: TuPoint, graph: Graph, delta_l: float,
                 delta_t: float, regions: dict[int, Region]) -> TuPoint:
    """
    Unir dois pontos espaço-temporais resulta em um novo
    ponto com inicio e duração atualizados e que respeita
    os critérios de l-diversidade e t-proximidade.
    """
    tc, duration = cost_matrix.join_spacetime(point_a, point_b)

    con_regions = get_connected_region(graph, point_a.region_id, point_b.region_id, regions)
    neighbours = {neighbour for reg in con_regions for neighbour in reg.neighbours_id
                  if neighbour not in con_regions}
    while calculate_diversity(con_regions) < delta_l:
        diversities = {}
        for neighbour_id in neighbours:
            neighbour = regions[neighbour_id]
            tmp = con_regions.copy()
            tmp |= {neighbour}
            diversities[neighbour] = calculate_diversity(tmp)

        if not diversities:
            break
        chosen = max(diversities, key=diversities.get)
        neighbours.remove(chosen.id)
        con_regions |= {chosen}

    # update neighbours
    neighbours = {neighbour for reg in con_regions for neighbour in reg.neighbours_id
                  if neighbour not in con_regions}
    while get_closeness(con_regions, graph.poi_distribution) < delta_t:
        closeness = {}
        for neighbour_id in neighbours:
            neighbour = regions[neighbour_id]
            tmp = con_regions.copy()
            tmp |= {neighbour}
            closeness[neighbour] = get_closeness(tmp, graph.poi_distribution)

        if not closeness:
            break
        chosen = min(closeness, key=closeness.get)
        neighbours.remove(chosen.id)
        con_regions |= {chosen}

    return TuPoint(
        utc_timestamp=tc,
        duration=duration,
        region_id=[reg.id for reg in con_regions]
    )

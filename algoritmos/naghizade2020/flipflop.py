from algoritmos.naghizade2020.treat_data import Segmented, Stop, Move, SubSegment


# TODO: organizar a nova sequencia de pontos antes de retornar do displacement e replacement
# algorithm 1 -> the algorithm displaces the first stop with the retrieved POI
# TODO: o local[0] que vai alterar
def stop_displacement(local, pois, axis_maj):
    foci_one, foci_two = local.points[0], local.points[-1]
    find_poi = find_poi_in_ellipse(foci_one, foci_two, pois, axis_maj)

    while len(find_poi) == 0 and axis_maj < delta:
        maj_a = axis_maj * 2
        find_poi = find_poi_in_ellipse(foci_one, foci_two, pois, axis_maj)

    poi = filter(find_poi)
    sp1 = shortest_path(local.points[0], poi)
    sp2 = shortest_path(local.points[-1], poi)
    tgen = gen_gps(local, sp1, sp2)
    tdis = replace_stop(tgen, stop1, poi)

    return tdis


# The replacement algorithm can be summarised as follows:
# Having a trajectory, T , a sensitive
# stop point, S ∈ S and a point of interest, poi ∈ P, the
# algorithm removes S from T . Then, it finds
# the point inside T that corresponds to poi, and following
# the pattern of S creates a stop
# TODO: organizar a nova sequencia de pontos antes de retornar do displacement e replacement
def stop_replacement(local: SubSegment, stop: Stop):
    return mewo()  # TODO


# algorithm 3
# TODO: O algoritmo flip-flop já verifica o replacement
def flip_flop_exchange(trajectory: Segmented, subtrajectories: list[SubSegment], all_pois: list[Stop], axis) -> \
        list[Stop | Move]:
    anonymized = trajectory.points[subtrajectories[0].init_index:]

    for local in subtrajectories:
        # procura por pois menos sensíveis que o poi no inicio da trajetória local
        pois = [(segment, segment.sensitivity) for segment in local.points[1:-1]
                if isinstance(segment, Stop) and segment.sensitivity < local.points[0].sensitivity]
        if pois:
            least_sensitive, _ = min(pois, key=lambda value: value[1])
            anonymized.extend(stop_replacement(local, least_sensitive))
        else:
            anonymized.extend(stop_displacement(local, all_pois, axis))
    return anonymized

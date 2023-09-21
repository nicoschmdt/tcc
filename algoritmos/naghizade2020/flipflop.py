from algoritmos.naghizade2020.treat_data import Segmented, Stop, Move, SubSegment


# TODO: organizar a nova sequencia de pontos antes de retornar do displacement e replacement
# algorithm 1 -> the algorithm displaces the first stop with the retrieved POI
# TODO: o local[0] que vai alterar
def stop_displacement(local, pois, axis_maj):
    foci_one, foci_two = local.points[0], local.points[-1]
    find_poi = find_poi_in_ellipse(foci_one, foci_two, pois, axis_maj)

    while not find_poi and axis_maj < delta:
        maj_a = axis_maj * 2
        find_poi = find_poi_in_ellipse(foci_one, foci_two, pois, axis_maj)

    poi = filter(find_poi)
    sp1 = shortest_path(local.points[0], poi)
    sp2 = shortest_path(local.points[-1], poi)
    tgen = gen_gps(local, sp1, sp2)
    tdis = stop_replacement(tgen, stop1, poi)

    return tdis


def stop_replacement(local: SubSegment, stop: Stop) -> None:
    stop_index = local.index(stop)
    first = local.points[0]
    end_time_old = first.end  # 10:30
    first.end = first.start + stop.get_duration()
    end_time_att = first.end  # 10:10

    for point in local.points[1:stop_index]:
        new_start = end_time_att + (point.start - end_time_old)
        if point == stop:
            end_time_att = point.end
        else:
            end_time_old = point.end
            end_time_att = new_start + point.get_duration()
        point.start = new_start
        point.end = end_time_att


# algorithm 3
# TODO: O algoritmo flip-flop já verifica o replacement
def flip_flop_exchange(trajectory: Segmented, subtrajectories: list[SubSegment], all_pois: list[Stop], axis) -> \
        Segmented:
    sub = []
    for local in subtrajectories:
        # procura por pois menos sensíveis que o poi no inicio da trajetória local
        # de [1:-1] para desconsiderar o inicio e fim da trajetória
        pois = [(segment, segment.sensitivity) for segment in local.points[1:-1]
                if isinstance(segment, Stop) and segment.sensitivity < local.points[0].sensitivity]
        if pois:
            least_sensitive, _ = min(pois, key=lambda value: value[1])
            stop_replacement(local, least_sensitive)
            sub.append(local)
        else:
            sub.append(stop_displacement(local, all_pois, axis))

    anonymized = []
    begin = 0
    for anon in sub:
        if begin != anon.init_index:
            anonymized.extend(trajectory.points[begin:anon.init_index])
        anonymized.extend(anon.points[anon.init_index:anon.end_index + 1])  # end_index não inclusivo
        begin = anon.end_index + 1

    return Segmented(anonymized, trajectory.privacy_settings)

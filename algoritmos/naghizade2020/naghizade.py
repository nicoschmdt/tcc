def stop_displacement(stop1, stop2,  local_trajectory, pois, axis_maj):
    foci_one, foci_two = find_foci(stop1, stop2)
    find_poi = find_poi_in_ellipse(foci_one, foci_two, pois, axis_maj)

    while len(find_poi) == 0 and axis_maj < delta:
        maj_a = axis_maj * 2
        find_poi = find_poi_in_ellipse(foci_one, foci_two, pois, axis_maj)

    poi = filter(find_poi)
    sp1 = shortest_path(stop1, poi)
    sp2 = shortest_path(stop2, poi)
    tgen = gen_gps(local_trajectory, sp1, sp2)
    tdis = replace_stop(tgen, stop1, poi)


def flip_flop_exchange(trajectories, sensitive_stop_points, all_pois):
    i = 1
    anonymized = []

    while i <= len(sensitive_stop_points):
        startIndex = sensitive_stop_points[i][ID]  # TODO: de onde vem o ID?
        endIndex = sensitive_stop_points[i + 1][ID]
        local_trajectory = trajectories[startIndex: endIndex]
        P = filter(route_poi(local_trajectory, all_pois))
        if len(P) > 0 then:
            poi = least_sensitive(P)
            anonymized = anonymized + replaceStop(anonymized, sensitive_stop_points[i], poi)
        else:  # TODO: entender oq tá acontecendo na chamada do stop displacement
            foci1, foci2 = sensitive_stop_points[i], sensitive_stop_points[i + 1]
            Tdis = stop_displacement(local_trajectory, foci1, foci2, P, axis_maj )T ∗ ← T ∗ + Tdis
        i += 1
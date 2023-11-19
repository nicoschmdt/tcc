from dataclasses import dataclass
from datetime import timedelta

from geopy import distance
from algoritmos.utils.math_utils import time_difference
from algoritmos.zhang2015.poi import PoI


@dataclass
class RoI:
    id: int
    core: int
    points: set[int]

    def belongs(self, poi: int) -> bool:
        return poi in self.points


@dataclass
class Clusters:
    clusters: list[RoI]

    def add_to_nearest_cluster(self, point: PoI, poi_compendium) -> None:
        chosen_roi = None
        calc_distance = float('inf')
        for roi in self.clusters:
            current_distance = distance.distance(point.loc, poi_compendium[roi.core].loc).meters
            if current_distance < calc_distance:
                chosen_roi = roi
                calc_distance = current_distance

        chosen_roi.points |= {point.id}


def cluster_poi(points: set[PoI], compendium, spatial_radius: float, temporal_radius: timedelta, density_threshold) -> tuple[Clusters, list[PoI]]:
    calculate_neighbours(points, spatial_radius, temporal_radius)
    print(f'clustering poi')
    clusters = []
    visited = []
    noise_candidate = []
    id_count = 0
    for i, point in enumerate(points):
        if point not in visited:
            visited.append(point)
            if len(point.neighbours) < density_threshold:
                noise_candidate.append(point)
            else:
                cluster, id_count = expand_cluster(point, compendium, clusters, density_threshold, visited, id_count)
                clusters.append(cluster)

    final_clusters = Clusters(clusters=clusters)
    noise = []
    for i, candidate in enumerate(noise_candidate):
        if len(candidate.neighbours) > 0:
            final_clusters.add_to_nearest_cluster(candidate, compendium)
        else:
            noise.append(candidate)

    return final_clusters, noise


# Algorithm 3, Pag 5
def expand_cluster(point: PoI, compendium: dict[int, PoI], clusters: list[RoI], density_threshold, visited, id_count) -> tuple[RoI, int]:
    roi = RoI(
        id=id_count,
        core=point.id,
        points={point.id}
    )
    id_count += 1

    neighbours = point.neighbours
    while True:
        new_neighbours = set()
        for neighbour_id in neighbours:
            current = compendium[neighbour_id]
            if neighbour_id not in visited:
                visited.append(neighbour_id)
                if len(current.neighbours) >= density_threshold:
                    new_neighbours |= current.neighbours

            clustered = False
            for created_clusters in clusters:
                if created_clusters.belongs(current.id):
                    clustered = True

            if not clustered:
                roi.points |= {current.id}

        if not new_neighbours:
            break

        neighbours = new_neighbours

    return roi, id_count


# A call of Retrieve_Neighbors(object, Eps1, Eps2) returns the objects that have a distance less
# than Eps1 and Eps2 parameters to the selected object. In other words, Retrieve_Neighbors function retrieves
# all objects density-reachable (see Definition 6) from the selected object with respect to Eps1, Eps2, and MinPts
def calculate_neighbours(points: set[PoI], spatial_radius: float, temporal_radius: timedelta) -> None:
    """
    Calcula os vizinhos para cada PoI e atualiza a sua lista.
    """
    pois = list(points)
    for i, point in enumerate(pois):
        for candidate in pois[i:]:
            if point != candidate:
                if distance.distance(point.loc, candidate.loc).meters <= spatial_radius \
                            and time_difference(candidate.t, point.t) <= temporal_radius:
                    point.neighbours |= {candidate.id}
                    candidate.neighbours |= {point.id}

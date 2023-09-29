from dataclasses import dataclass
from datetime import timedelta

from geopy import distance
from algoritmos.utils.math_utils import time_difference
from algoritmos.zhang2015.poi import PoI


@dataclass
class RoI:
    core: PoI
    points: list[PoI]

    def belongs(self, poi: PoI) -> bool:
        return poi in self.points


@dataclass
class Clusters:
    clusters: list[RoI]

    def add_to_nearest_cluster(self, point: PoI) -> None:
        chosen_roi = None
        calc_distance = float('inf')
        for roi in self.clusters:
            current_distance = distance.distance(point.loc, roi.core.loc).kilometers
            if current_distance < calc_distance:
                chosen_roi = roi
                calc_distance = current_distance

        chosen_roi.points.append(point)


def cluster_poi(points: set[PoI], spatial_radius: float, temporal_radius: timedelta, density_threshold) -> Clusters:
    calculate_neighbours(points, spatial_radius, temporal_radius)

    clusters = []
    visited = []
    noise_candidate = []
    for point in points:
        if point not in visited:
            visited.append(point)
            if len(point.neighbours) < density_threshold:
                noise_candidate.append(point)
            else:
                cluster = expand_cluster(point, clusters, density_threshold, visited)
                clusters.append(cluster)

    final_clusters = Clusters(clusters=clusters)
    noise = []
    for candidate in noise_candidate:
        if len(candidate.neighbours) > 0:
            final_clusters.add_to_nearest_cluster(candidate)
        else:
            noise.append(candidate)

    return final_clusters


# Algorithm 3, Pag 5
def expand_cluster(point: PoI, clusters: list[RoI], density_threshold, visited) -> RoI:
    roi = RoI(
        core=point,
        points=[point]
    )

    neighbours = point.neighbours
    while True:
        new_neighbours = []
        for neighbour in neighbours:
            if neighbour not in visited:
                visited.append(neighbour)
                if len(neighbour.neighbours) >= density_threshold:
                    new_neighbours.extend(neighbour.neighbours)

            clustered = False
            for created_clusters in clusters:
                if created_clusters.belongs(neighbour):
                    clustered = True

            if not clustered:
                roi.points.append(neighbour)

        if not new_neighbours:
            break

        neighbours = new_neighbours

    return roi


# A call of Retrieve_Neighbors(object, Eps1, Eps2) returns the objects that have a distance less
# than Eps1 and Eps2 parameters to the selected object. In other words, Retrieve_Neighbors function retrieves
# all objects density-reachable (see Definition 6) from the selected object with respect to Eps1, Eps2, and MinPts
def calculate_neighbours(points: set[PoI], spatial_radius: float, temporal_radius: timedelta) -> None:
    """
    Calcula os vizinhos para cada PoI e atualiza a sua lista.
    """
    for i, point in enumerate(points):
        for candidate in points[i:]:
            if distance.distance(point.loc, candidate.loc).kilometers <= spatial_radius \
                    and time_difference(candidate.t, point.t) <= temporal_radius:
                point.neighbours.append(candidate)
                candidate.neighbours.append(point)

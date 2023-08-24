from dataclasses import dataclass

from algoritmos.utils.math_utils import distance
from algoritmos.zhang2015.poi import PoI


@dataclass
class Cluster:
    core: PoI
    points: list[PoI]

    def belongs(self, poi: PoI) -> bool:
        return poi in self.points


@dataclass
class Clusters:
    clusters: list[Cluster]

    def add_to_nearest_cluster(self, point: PoI) -> None:
        pass


def cluster_poi(points: set[PoI], spatial_radius: float, temporal_radius, density_threshold) -> Clusters:
    clusters = []
    unvisited_points = [point for point in points]
    noise_candidate = []
    for point in points:
        if point in unvisited_points:
            unvisited_points.remove(point)
            neighbours = get_neighbours(point, points, spatial_radius, temporal_radius)
            if len(neighbours) < density_threshold:
                noise_candidate.append(point)
            else:
                # TODO: pedir a opinião do tiz de como lidar com esse unvisited
                #  points, imagino que retornar ele assim n seja legal
                unvisited_points, cluster = expand_cluster(point, neighbours, clusters, spatial_radius, temporal_radius,
                                                           density_threshold, unvisited_points)
                clusters.append(cluster)

    final_clusters = Clusters(clusters=clusters)
    noise = []
    for candidate in noise_candidate:
        ncN = get_neighbours(candidate, points, spatial_radius, temporal_radius)
        if len(ncN) > 0:
            final_clusters.add_to_nearest_cluster(candidate)
        else:
            noise.append(candidate)

    return final_clusters


# Algorithm 3, Pag 5
def expand_cluster(point: PoI, neighbours: list[PoI], clusters: list[Cluster], spatial_radius: float, temporal_radius, density_threshold, unvisited):
    cluster = Cluster(
        core=point,
        points=[]
    )

    for neighbour in neighbours:
        if neighbour in unvisited:
            unvisited.remove(neighbour)
            M = get_neighbours(neighbour, spatial_radius, temporal_radius)
            if len(M) >= density_threshold:
                neighbours |= M  # TODO: ver com o tiz se essa alteração na lista enquanto ela é iterada é ok

        for created_clusters in clusters:
            if not created_clusters.belongs(neighbour):
                cluster.points.append(neighbour)

    return unvisited, cluster


# A call of Retrieve_Neighbors(object, Eps1, Eps2) returns the objects that have a distance less
# than Eps1 and Eps2 parameters to the selected object. In other words, Retrieve_Neighbors function retrieves
# all objects density-reachable (see Definition 6) from the selected object with respect to Eps1, Eps2, and MinPts
def get_neighbours(point: PoI, points: set[PoI], spatial_radius, temporal_radius) -> list[PoI]:
    neighbours = []

    for poi in points:
        if poi == point:
            continue

        if distance(point.loc, poi.loc) <= spatial_radius and (poi.t - point.t) <= temporal_radius:
            neighbours.append(poi)

    return neighbours

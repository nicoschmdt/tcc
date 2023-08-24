from dataclasses import dataclass

from algoritmos.utils.trajetory import Trajectory, Point
from algoritmos.zhang2015.group import get_groups
from algoritmos.zhang2015.roi import cluster_poi
from algoritmos.zhang2015.poi import extract_poi, PoI


# Algorithm 1, Pag 3
@dataclass
class ZhangTrajectory:
    points: list[Point]
    pois: set[PoI]

    def similarity(self, trajectory: 'ZhangTrajectory') -> float:
        return len(self.pois & trajectory.pois) / len(self.pois | trajectory.pois)

    def similarity_group(self, group: list['ZhangTrajectory']):
        sim = 0
        for trajectory in group:
            sim += self.similarity(trajectory)

        return sim/len(group)


def anonimization_algorithm(trajectories: list[Trajectory], min_angle, min_dist, min_stay_time, spatial_radius, temporal_radius, density_threshold, alpha, k) -> None:
    """
    Algoritmo de proteção de privacidade de
    trajetórias k-anonimidade baseado em POI
    """
    pois = set()
    zhang_trajectories = []
    for trajectory in trajectories:
        poi = extract_poi(trajectory.points, min_angle, min_dist, min_stay_time)
        zhang_trajectories.append(ZhangTrajectory(trajectory.points, pois=poi))
        pois |= poi

    roi = cluster_poi(pois, spatial_radius, temporal_radius, density_threshold)
    groups = get_groups(zhang_trajectories, alpha, k)

    D* = {}
    for group in groups:
        D* |= anonymity(group)

    return D*


#
# if __name__ == '__main__':
#     trajectories = return_dict('resources/dataset_TSMC2014_TKY.csv')
#     # for trajectory in trajectories.items():
#     #     print(trajectory)
import random
from dataclasses import dataclass, field

from algoritmos.utils.trajetory import Trajectory, Point
from algoritmos.zhang2015.group import get_groups
from algoritmos.zhang2015.roi import cluster_poi, RoI
from algoritmos.zhang2015.poi import extract_poi, PoI


# Algorithm 1, Pag 3
@dataclass
class ZhangTrajectory:
    points: list[Point | PoI]
    pois: set[PoI]
    rois: set[RoI] = field(default_factory=set)

    def similarity(self, trajectory: 'ZhangTrajectory') -> float:
        return len(self.rois & trajectory.rois) / len(self.rois | trajectory.rois)

    def similarity_group(self, group: list['ZhangTrajectory']) -> float:
        sim = 0
        for trajectory in group:
            sim += self.similarity(trajectory)

        return sim / len(group)


def anonymize(trajectories: list[Trajectory], min_angle, min_dist, min_stay_time, spatial_radius, temporal_radius,
              density_threshold, alpha, k) -> list[list[ZhangTrajectory]]:
    """
    Algoritmo de proteção de privacidade de
    trajetórias k-anonimidade baseado em POI
    """
    pois = set()
    zhang_trajectories = []
    for trajectory in trajectories:
        poi, new_points = extract_poi(trajectory.points, min_angle, min_dist, min_stay_time)
        zhang_trajectories.append(ZhangTrajectory(new_points, pois=poi))
        pois |= poi

    roi = cluster_poi(pois, spatial_radius, temporal_radius, density_threshold)
    groups = get_groups(zhang_trajectories, roi, alpha, k)

    shuffled = []
    for group in groups:
        shuffled.append(swap(group))

    return shuffled


def swap(trajectories: list[ZhangTrajectory]) -> list[ZhangTrajectory]:
    swapped_trajectories = []
    for trajectory in trajectories:
        swapped_trajectories.append(trajectory)

    return swapped_trajectories


def swap_poi(trajectory: ZhangTrajectory) -> ZhangTrajectory:
    new_trajectory_points = []
    new_pois = set()
    for point in trajectory.points:
        if isinstance(point, PoI):
            roi = find_roi(point, trajectory.rois)
            new_poi = random.sample(roi.points, 1)
            new_trajectory_points.append(new_poi)
            new_pois |= new_poi
        else:
            new_trajectory_points.append(point)

    return ZhangTrajectory(new_trajectory_points, new_pois, trajectory.rois)


def find_roi(poi: PoI, rois: set[RoI]) -> RoI:
    for roi in rois:
        if roi.belongs(poi):
            return roi

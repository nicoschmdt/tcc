# Algorithm 4, Pag 6
from dataclasses import dataclass, field

from algoritmos.utils.trajetory import Point
from algoritmos.zhang2015.poi import PoI
from algoritmos.zhang2015.roi import Clusters


@dataclass
class ZhangTrajectory:
    points: list[Point | PoI]
    pois: set[int]
    rois: set[int] = field(default_factory=set)

    def similarity(self, trajectory: 'ZhangTrajectory') -> float:
        return len(self.rois & trajectory.rois) / len(self.rois | trajectory.rois)

    def similarity_group(self, group: list['ZhangTrajectory']) -> float:
        sim = 0
        for trajectory in group:
            sim += self.similarity(trajectory)

        return sim / len(group)


def get_groups(trajectories: list[ZhangTrajectory], rois: Clusters, alpha: float, k: int) -> list[list[ZhangTrajectory]]:
    assign_regions(trajectories, rois)

    groups = []
    not_grouped = [traj for traj in trajectories]
    for i, trajectory in enumerate(trajectories):
        if trajectory not in not_grouped:
            continue

        group = []
        for traj in trajectories[i+1:]:
            if trajectory.similarity(traj) == 1:
                not_grouped.remove(traj)
                group.append(traj)

        if group:
            not_grouped.remove(trajectory)
            groups.append(group)

    for trajectory in not_grouped:
        for group in groups:
            if trajectory.similarity_group(group) >= alpha:
                group.append(trajectory)
                break

    anonymized = []
    for group in groups:
        if len(group) >= k:
            anonymized.append(group)

    return anonymized


def assign_regions(trajectories: list[ZhangTrajectory], rois: Clusters) -> None:
    for trajectory in trajectories:
        for roi in rois.clusters:
            for poi in trajectory.pois:
                if roi.belongs(poi):
                    trajectory.rois |= {roi.id}
                    break

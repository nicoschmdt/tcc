# Algorithm 4, Pag 6
from dataclasses import dataclass, field

from algoritmos.utils.trajetory import Point
from algoritmos.zhang2015.poi import PoI
from algoritmos.zhang2015.roi import Clusters


@dataclass
class ZhangTrajectory:
    uid: str
    points: list[Point | PoI]
    pois: set[int]
    rois: set[int] = field(default_factory=set)

    def similarity(self, trajectory: 'ZhangTrajectory') -> float:
        union = len(self.rois | trajectory.rois)
        if union == 0:
            return 0
        return len(self.rois & trajectory.rois) / union

    def similarity_group(self, group: list['ZhangTrajectory']) -> float:
        sim = 0
        for trajectory in group:
            sim += self.similarity(trajectory)

        return sim / len(group)


def get_groups(trajectories: list[ZhangTrajectory], rois: Clusters, noise: list[PoI], alpha: float, k: int) -> list[list[ZhangTrajectory]]:
    assign_regions(trajectories, noise, rois)

    groups = []
    not_grouped = [traj for traj in trajectories]
    for i, trajectory in enumerate(trajectories):
        print(f'{i}/{len(trajectories)}')
        if trajectory not in not_grouped:
            continue

        group = [trajectory]
        for traj in trajectories[i+1:]:
            if trajectory.similarity(traj) == 1:
                not_grouped.remove(traj)
                group.append(traj)

        if len(group) > 1:
            not_grouped.remove(trajectory)
            groups.append(group)

    for i, trajectory in enumerate(not_grouped):
        print(f'{i}/{len(not_grouped)}')
        for group in groups:
            if trajectory.similarity_group(group) >= alpha:
                group.append(trajectory)
                break

    anonymized = []
    for group in groups:
        if len(group) >= k:
            anonymized.append(group)

    return anonymized


def assign_regions(trajectories: list[ZhangTrajectory], noise: list[PoI], rois: Clusters) -> None:
    trajs = []
    for tr in trajectories:
        pois = set()
        rmv = []
        for poi in tr.pois:
            if poi not in noise:
                found = False
                for roi in rois.clusters:
                    if roi.belongs(poi):
                        found = True
                        tr.rois |= {roi.id}
                        break
                if found:
                    pois |= {poi}
                else:
                    rmv.append(poi)
        pts = [pt for pt in tr.points if pt not in rmv]
        trajs.append(ZhangTrajectory(tr.uid, pts, pois, tr.rois))

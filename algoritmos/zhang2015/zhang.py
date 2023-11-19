import random

from algoritmos.utils.io import write, read_groups, read_rois
from algoritmos.utils.trajetory import Trajectory
from algoritmos.zhang2015.group import get_groups, ZhangTrajectory
from algoritmos.zhang2015.roi import cluster_poi, RoI
from algoritmos.zhang2015.poi import extract_poi, PoI


# Algorithm 1, Pag 3
def anonymize(trajectories: list[ZhangTrajectory], pois: set[PoI], spatial_radius, temporal_radius,
              density_threshold, alpha, k, name: str = '') -> list[list[ZhangTrajectory]]:
    """
    Algoritmo de proteção de privacidade de
    trajetórias k-anonimidade baseado em POI
    """

    # groups = read_groups('groups.json')
    # roi_compendium = read_rois('roi_compendium.json')

    poi_compendium = {poi.id: poi for poi in pois}
    clusters, noise = cluster_poi(pois, poi_compendium, spatial_radius, temporal_radius, density_threshold)
    roi_compendium = {roi.id: roi for roi in clusters.clusters}
    groups = get_groups(trajectories, clusters, noise, alpha, k)

    write(groups, f'zhang2015/groups{name}.json')
    write(roi_compendium, f'zhang2015/roi_compendium{name}.json')
    write(poi_compendium, f'zhang2015/poi_compendium{name}.json')

    shuffled = []
    for group in groups:
        shuffled.append(swap(group, roi_compendium, poi_compendium))

    return shuffled


def process_pois(trajectories: list[Trajectory], min_angle, min_dist, min_stay_time) \
                -> tuple[list[ZhangTrajectory], set[PoI]]:
    pois = set()
    zhang_traj = []
    curr_id = 0
    for i, trajectory in enumerate(trajectories):
        uid = trajectory.points[0].uid
        extracted, points, curr_id = extract_poi(trajectory.points, min_angle, min_dist, min_stay_time, curr_id)
        zhang_traj.append(ZhangTrajectory(uid=uid, points=points, pois={poi.id for poi in extracted}))
        pois |= extracted
    
    return zhang_traj, pois


def swap(trajectories: list[ZhangTrajectory], roi_compendium, poi_compendium) -> list[ZhangTrajectory]:
    swapped_trajectories = []
    group_rois = get_rois_from_group(trajectories, roi_compendium)
    for trajectory in trajectories:
        swapped_trajectories.append(swap_poi(trajectory, poi_compendium, group_rois))

    return swapped_trajectories


def get_rois_from_group(trajectories: list[ZhangTrajectory], roi_compendium) -> set[RoI]:
    rois = set()
    for trajectory in trajectories:
        for roi_id in trajectory.rois:
            rois |= roi_compendium[roi_id]
    return rois


def swap_poi(trajectory: ZhangTrajectory, poi_compendium, group_rois: set[RoI]) -> ZhangTrajectory:
    new_trajectory_points = []
    new_pois = set()

    for point in trajectory.points:
        if isinstance(point, PoI):
            # roi, found = find_roi(point.id, trajectory.rois, roi_compendium)
            # if found:
            roi = random.sample(list(group_rois), 1)[0]
            new_poi = random.sample(list(roi.points), 1)
            new_trajectory_points.append(poi_compendium[new_poi[0]])
            new_pois |= set(new_poi)
        else:
            new_trajectory_points.append(point)

    return ZhangTrajectory(trajectory.uid, new_trajectory_points, new_pois, trajectory.rois)


def find_roi(poi_id: int, rois: set[int], roi_compendium) -> tuple[RoI | None, bool]:
    for roi_id in rois:
        roi = roi_compendium[roi_id]
        if roi.belongs(poi_id):
            return roi, True
    return None, False

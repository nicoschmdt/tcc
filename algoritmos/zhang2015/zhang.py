import random

from algoritmos.utils.io import write, read_groups, read_rois
from algoritmos.utils.trajetory import Trajectory
from algoritmos.zhang2015.group import get_groups, ZhangTrajectory
from algoritmos.zhang2015.roi import cluster_poi, RoI
from algoritmos.zhang2015.poi import extract_poi, PoI


# Algorithm 1, Pag 3
def anonymize(trajectories: list[ZhangTrajectory], pois: set[PoI], spatial_radius, temporal_radius,
              density_threshold, alpha, k) -> list[list[ZhangTrajectory]]:
    """
    Algoritmo de proteção de privacidade de
    trajetórias k-anonimidade baseado em POI
    """

    # groups = read_groups('groups.json')
    # roi_compendium = read_rois('roi_compendium.json')

    poi_compendium = {poi.id: poi for poi in pois}
    clusters = cluster_poi(pois, poi_compendium, spatial_radius, temporal_radius, density_threshold)
    roi_compendium = {roi.id: roi for roi in clusters.clusters}
    groups = get_groups(trajectories, clusters, alpha, k)

    # write(groups, 'groups.json')
    # write(roi_compendium, 'roi_compendium.json')

    shuffled = []
    for group in groups:
        shuffled.append(swap(group, roi_compendium, poi_compendium))

    return shuffled


def process_pois(trajectories: list[Trajectory], min_angle, min_dist, min_stay_time) \
                -> tuple[list[ZhangTrajectory], set[PoI]]:
    pois = set()
    zhang_traj = []
    curr_id = 0
    for trajectory in trajectories:
        uid = trajectory.points[0].uid
        extracted, points, curr_id = extract_poi(trajectory.points, min_angle, min_dist, min_stay_time, curr_id)
        zhang_traj.append(ZhangTrajectory(uid=uid, points=points, pois={poi.id for poi in extracted}))
        pois |= extracted
    
    return zhang_traj, pois


def swap(trajectories: list[ZhangTrajectory], roi_compendium, poi_compendium) -> list[ZhangTrajectory]:
    swapped_trajectories = []
    for trajectory in trajectories:
        swapped_trajectories.append(swap_poi(trajectory, roi_compendium, poi_compendium))

    return swapped_trajectories


def swap_poi(trajectory: ZhangTrajectory, roi_compendium, poi_compendium) -> ZhangTrajectory:
    new_trajectory_points = []
    new_pois = set()
    for point in trajectory.points:
        if isinstance(point, PoI):
            roi = find_roi(point.id, trajectory.rois, roi_compendium)
            new_poi = random.sample(list(roi.points), 1)
            new_trajectory_points.append(poi_compendium[new_poi[0]])
            new_pois |= set(new_poi)
        else:
            new_trajectory_points.append(point)

    return ZhangTrajectory(trajectory.uid, new_trajectory_points, new_pois, trajectory.rois)


def find_roi(poi_id: int, rois: set[int], roi_compendium) -> RoI:
    for roi_id in rois:
        roi = roi_compendium[roi_id]
        if roi.belongs(poi_id):
            return roi

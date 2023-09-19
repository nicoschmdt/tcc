from algoritmos.tu2017.tu import merging_trajectories
from algoritmos.utils.semantic import get_venue_category
from algoritmos.utils.trajetory import create_raw_trajectories, split_trajectories, add_duration


def main():
    # pre-process
    dataset_name = ""
    trajectories = create_raw_trajectories(dataset_name)
    splitted = split_trajectories(trajectories)
    with_duration = add_duration(splitted)

    # semantic
    semantic = get_venue_category(with_duration)

    # treat data
    anonymized = merging_trajectories(semantic, k, l, t)

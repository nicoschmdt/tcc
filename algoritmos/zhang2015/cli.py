from algoritmos.utils.trajetory import create_raw_trajectories, split_trajectories
from algoritmos.zhang2015.zhang import anonymize


def main():
    # pre-process
    dataset_name = ""
    trajectories = create_raw_trajectories(dataset_name)
    splitted = split_trajectories(trajectories)
    # with_duration = add_duration(splitted)  # TODO: ver se precisa usar

    # treat data
    anonymized = anonymize(splitted, min_angle, min_dist, min_stay_time, spatial_radius, temporal_radius,
                           density_threshold, alpha, k)
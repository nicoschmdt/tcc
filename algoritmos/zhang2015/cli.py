import math
from datetime import timedelta

from algoritmos.utils.io import write, read_pois, read_zhang
from algoritmos.utils.trajetory import raw, split_trajectories
from algoritmos.zhang2015.zhang import anonymize, process_pois


def main():
    # pre-process
    dataset_name = "../../resources/dataset_TSMC2014_NYC.csv"
    trajectories = raw(dataset_name)
    # trajectories = create_raw_trajectories(dataset_name)
    splitted = split_trajectories(trajectories)
    # with_duration = add_duration(splitted)  # TODO: ver se precisa usar

    # read
    zhang_trajectories = read_zhang('trajectories.json')
    pois = read_pois('pois.json')

    # parameters
    min_angle = 30  # degree
    min_dist = 200  # meters
    min_stay_time = timedelta(minutes=20)
    spatial_radius = 200  # meters TODO: conferir mesma coisa pro spatial radius == min dist
    temporal_radius = timedelta(minutes=20)  # TODO: conferir se é ok considerar o temporal radius == min stay time
    density_threshold = math.log(len(splitted))
    alpha = 0  #
    k = 2

    # treat data
    # zhang_trajectories, pois = process_pois(splitted, min_angle, min_dist, min_stay_time)

    # write
    # write(zhang_trajectories, 'trajectories.json')
    # write(pois, 'pois.json')


    # alpha values = 0 and 2000
    # k values = 2, 4, 6, 8, 10 e 12
    anonymized = anonymize(zhang_trajectories, pois, spatial_radius, temporal_radius,
                           density_threshold, alpha, k)
    write(anonymized, 'anonymized.json')

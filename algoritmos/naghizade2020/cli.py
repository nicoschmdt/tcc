from algoritmos.naghizade2020.naghizade import naghizade
from algoritmos.naghizade2020.treat_data import identify_stops, get_all_pois
from algoritmos.utils.generator import generate_settings
from algoritmos.utils.semantic import get_category_with_type
from algoritmos.utils.trajetory import create_raw_trajectories, split_with_settings


def main():
    # pre-process
    dataset_name = ""
    trajectories = create_raw_trajectories(dataset_name)
    trajectories_with_settings = generate_settings(trajectories)
    splitted = split_with_settings(trajectories_with_settings)

    # semantic
    semantic = get_category_with_type(splitted)

    # treat data
    # TODO o artigo não menciona sobre o valor de dist e temporal thresholds
    segmented = identify_stops(semantic, dist_threshold, temporal_threshold)
    all_pois = get_all_pois(segmented)

    anonymized = naghizade(segmented, all_pois, axis)

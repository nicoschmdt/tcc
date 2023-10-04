import json
from dataclasses import is_dataclass, asdict
from datetime import timedelta, datetime

from algoritmos.naghizade2020.naghizade import naghizade
from algoritmos.naghizade2020.treat_data import identify_stops, get_all_pois, Segmented, Stop, Move
from algoritmos.utils.generator import generate_settings
from algoritmos.utils.semantic import get_category_with_type, split_with_settings, PoiCategory
from algoritmos.utils.trajetory import create_raw_trajectories


def main():
    # pre-process
    dataset_name = "../../resources/dataset_TSMC2014_NYC.csv"
    trajectories = create_raw_trajectories(dataset_name)
    trajectories_with_settings = generate_settings(trajectories)
    splitted = split_with_settings(trajectories_with_settings, 2)

    # semantic
    semantic = get_category_with_type(splitted)

    # treat data
    dist_threshold = 200  # meters
    temporal_threshold = timedelta(minutes=20)
    segmented = identify_stops(semantic, dist_threshold, temporal_threshold)
    # segmented = read('naghizade.json')
    # write(segmented, 'naghizade.json')
    all_pois = get_all_pois(segmented)

    anonymized = naghizade(segmented, all_pois)


class DCJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, datetime):
            return o.strftime('%d/%m/%Y, %H:%M:%S')
        return super().default(o)


def write(trajectories, name: str):
    with open(name, 'w') as f:
        json.dump(trajectories, f, cls=DCJSONEncoder)


def read(name: str):
    with open(name, 'r') as f:
        data = json.load(f)

    trajectories = []
    for trajectory in data:
        locations = []
        for location in trajectory['points']:
            if 'semantic' in location:
                locations = location['locations']
                start = datetime.strptime(location['start'], '%d/%m/%Y, %H:%M:%S')
                end = datetime.strptime(location['end'], '%d/%m/%Y, %H:%M:%S')
                semantic = location['semantic']
                sensitivity = location['sensitivity']
                loc = Stop(locations, start, end, semantic, location['type'], sensitivity)
            else:
                locations = location['locations']
                start = datetime.strptime(location['start'], '%d/%m/%Y, %H:%M:%S')
                end = datetime.strptime(location['end'], '%d/%m/%Y, %H:%M:%S')
                loc = Move(locations, start, end)

            locations.append(loc)
        privacy = trajectory['privacy_settings']
        settings = {}
        category: PoiCategory
        for category in PoiCategory:
            settings[category] = float(privacy[category.value])
        length = trajectory['length']
        trajectories.append(Segmented(locations, settings, length))

    return trajectories

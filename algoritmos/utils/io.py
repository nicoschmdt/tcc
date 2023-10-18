import json
from dataclasses import is_dataclass, asdict
from datetime import datetime, timedelta

from algoritmos.naghizade2020.treat_data import Stop, Move, Segmented
from algoritmos.tu2017.treat_data import TuPoint, TuTrajectory
from algoritmos.tu2017.graph import Graph
from algoritmos.utils.region import Region
from algoritmos.utils.semantic import PoiCategory
from algoritmos.utils.trajetory import Point
from algoritmos.zhang2015.group import ZhangTrajectory
from algoritmos.zhang2015.poi import PoI
from algoritmos.zhang2015.roi import RoI


class DCJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, datetime):
            return o.strftime('%d/%m/%Y, %H:%M:%S')
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, timedelta):
            return o.total_seconds()
        return super().default(o)


def write(trajectories, name: str):
    with open(name, 'w') as f:
        json.dump(trajectories, f, cls=DCJSONEncoder)


def read_merged(name: str):
    with open(name, 'r') as f:
        data = json.load(f)
    return {int(reg_id): [int(sid) for sid in data[reg_id]] for reg_id in data}


def read_graph(name: str):
    with open(name, 'r') as f:
        data = json.load(f)

    vertices = {read_region(vertex) for vertex in data['vertices']}

    distribution = {}
    dist = data['poi_distribution']

    category: PoiCategory
    for category in PoiCategory:
        distribution[category] = float(dist[category.value])

    return Graph(vertices, distribution)


def read_region(vertex):
    vertex_id = vertex['id']
    center_point = vertex['center_point']
    area = vertex['area']
    categories = {}
    cat_qtd = vertex['categories']
    category: PoiCategory
    for category in PoiCategory:
        categories[category] = int(cat_qtd[category.value])
    neighbours = set(vertex['neighbours_id'])
    return Region(vertex_id, center_point, area, categories, neighbours)


def read_categories(name: str):
    with open(name, 'r') as f:
        data = json.load(f)

    categories = {}
    category: PoiCategory
    for category in PoiCategory:
        categories[category] = int(data[category.value])


def read_regions(name: str):
    with open(name, 'r') as f:
        data = json.load(f)

    return {int(region): read_region(data[region]) for region in data}


def read_cost_matrix(name: str):
    with open(name, 'r') as f:
        data = json.load(f)

    matrix = {}
    for key in data:
        cost_list = []
        costs = data[key]
        for cost, traj_id in costs:
            # trajectory = read_tu_trajectory(traj_dict)
            cost_list.append((float(cost), int(traj_id)))
        matrix[int(key)] = cost_list
    return matrix


def read_tu_trajectory(trajectory) -> TuTrajectory:
    points = []
    n = trajectory['n']
    traj_id = trajectory['id']
    for point in trajectory['points']:
        date = datetime.strptime(point['utc_timestamp'], '%d/%m/%Y, %H:%M:%S')
        duration = timedelta(seconds=point['duration'])
        region_id = [int(reg_id) for reg_id in point['region_id']]
        points.append(TuPoint(date, duration, region_id))
    return TuTrajectory(traj_id, points, n)


def read_tu(name: str):
    with open(name, 'r') as f:
        data = json.load(f)

    return [read_tu_trajectory(trajectory) for trajectory in data]


def read_naghizade(name: str) -> list[Segmented]:
    with open(name, 'r') as f:
        data = json.load(f)

    trajectories = []
    for trajectory in data:
        points = []
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

            points.append(loc)
        privacy = trajectory['privacy_settings']
        settings = {}
        category: PoiCategory
        for category in PoiCategory:
            settings[category] = float(privacy[category.value])
        length = trajectory['length']
        trajectories.append(Segmented(points, settings, length))

    return trajectories


def read_zhang(name: str) -> list[ZhangTrajectory]:
    with open(name, 'r') as f:
        data = json.load(f)

    return get_zhang(data)


def get_zhang(data) -> list[ZhangTrajectory]:
    trajectories = []
    for trajectory in data:
        points = []
        for point in trajectory['points']:
            if 'id' in point:
                points.append(read_poi(point))
            else:
                name = point['name']
                uid = point['user_id']
                venue = point['venue_id']
                category = point['venue_category']
                lat = point['latitude']
                long = point['longitude']
                timestamp = datetime.strptime(point['utc_timestamp'], '%d/%m/%Y, %H:%M:%S')
                duration = timedelta(seconds=point['duration'])
                points.append(Point(name, uid, venue, category, lat, long, timestamp, duration))
        pois = set(trajectory['pois'])
        rois = set(trajectory['rois'])
        trajectories.append(ZhangTrajectory(points, pois, rois))
    return trajectories


def read_pois(name: str) -> set[PoI]:
    with open(name, 'r') as f:
        data = json.load(f)

    pois = set()
    for poi in data:
        pois |= {read_poi(poi)}

    return pois


def read_poi(line) -> PoI:
    t = datetime.strptime(line['t'], '%d/%m/%Y, %H:%M:%S')
    return PoI(line['id'], line['loc'], t, set(line['neighbours']))


def read_rois(name: str) -> dict[int, RoI]:
    with open(name, 'r') as f:
        data = json.load(f)

    return {int(key): get_roi(value) for key, value in data.items()}


def get_roi(line) -> RoI:
    return RoI(line['id'], int(line['core']), set(line['points']))


def read_groups(name: str) -> list[list[ZhangTrajectory]]:
    with open(name, 'r') as f:
        data = json.load(f)

    return [get_zhang(line) for line in data]

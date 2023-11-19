from datetime import timedelta, datetime

import polyline
import requests

from algoritmos.naghizade2020.treat_data import Segmented, Stop, Move, SubSegment
from matplotlib.patches import Ellipse
from geopy import distance

from algoritmos.utils.math_utils import get_middle, get_minor_axis, ellipsis_angle, time_difference, timedelta_diff
from algoritmos.utils.semantic import PoiCategory


# algorithm 1 -> the algorithm displaces the first stop with the retrieved POI
def stop_displacement(local: SubSegment, pois: list[Stop], boundary: float, settings: dict[PoiCategory, float]) -> tuple[SubSegment | None, bool]:
    # apenas 1 stop point
    if len(local.points) == 1:
        stop = local.points[0]
        foci1 = stop.locations[0]
        foci2 = stop.locations[-1]
    else:
        foci1 = local.points[0].get_position()
        foci2 = local.points[-1].get_position()

    dist_foci = distance.distance(foci1, foci2).meters
    if foci1 == foci2:
        dist_foci = 200
    axis_maj = dist_foci + (0.2 * dist_foci)
    ellipsis_center = get_middle(foci1, foci2)
    angle = ellipsis_angle(foci1, foci2)
    axis_min = get_minor_axis(ellipsis_center, foci1, axis_maj)

    ellipse = Ellipse(ellipsis_center, axis_maj, axis_min, angle=angle)
    find_poi = find_poi_ellipse(ellipse, pois, local.points[0], local.points[-1], dist_foci)

    while not find_poi and axis_maj * 2 < boundary:
        axis_maj *= 2
        axis_min = get_minor_axis(ellipsis_center, foci1, axis_maj)
        ellipse = Ellipse(ellipsis_center, axis_maj, axis_min, angle=angle)
        find_poi = find_poi_ellipse(ellipse, pois, local.points[0], local.points[-1], dist_foci)

    found_pois = [(segment, segment.sensitivity) for segment in find_poi
                  if settings[segment.semantic] < local.points[0].sensitivity]

    if not found_pois:
        return None, False

    poi, _ = min(found_pois, key=lambda value: value[1])
    poi.sensitivity = settings[poi.semantic]
    new_segment = form_segment(local, poi)
    stop_replacement(new_segment, poi)

    return new_segment, True


def form_segment(segment: SubSegment, new_stop: Stop) -> SubSegment:
    init = segment.points[0]
    end = segment.points[-1]
    json = osrm_get(init.get_position(), new_stop.get_position())
    move1 = create_move_segment(json, init.end)

    new_stop.start = move1.end
    json2 = osrm_get(new_stop.get_position(), end.get_position())
    move2 = create_move_segment(json2, new_stop.end)

    new_stop.end = move2.start
    footprint = [init, move1, new_stop, move2, end]
    return SubSegment(footprint, segment.init_index, segment.end_index)


def create_move_segment(json, previous_end: datetime) -> Move:
    legs = json['routes'][0]['legs'][0]
    duration = timedelta(seconds=legs['duration'])
    steps = legs['steps']
    init_time = steps[0]['duration']
    move_segment = []
    for step in steps:
        points = polyline.decode(step['geometry'])
        move_segment.append(points[len(points) // 2])
    start = previous_end + timedelta(seconds=init_time)
    end = previous_end + duration
    return Move(move_segment, start, end)


# /route/v1/{profile}/{coordinates}?alternatives={true|false|number}&steps={true|false}&geometries={polyline|polyline6|geojson}&overview={full|simplified|false}&annotations={true|false}
def osrm_get(coordinate1: tuple[float, float], coordinate2: tuple[float, float]):
    url = 'https://routing.openstreetmap.de/'
    coordinates = f'{coordinate1[1]},{coordinate1[0]};{coordinate2[1]},{coordinate2[0]}'
    details = f'routed-car/route/v1/driving/{coordinates}?steps=true&overview=false'
    response = requests.get(f'{url}{details}')
    return response.json()


def bounded(poi: Stop, local1: Stop, local2: Stop, dist_foci: float) -> bool:
    travel_time = time_difference(local1.start, local2.end)
    speed = dist_foci / (travel_time.total_seconds() / 3600)
    if local1 != local2:
        dist1 = distance.distance(local1.get_position(), poi.get_position()).kilometers
        dist2 = distance.distance(poi.get_position(), local2.get_position()).kilometers
        dist = dist1 + dist2
    else:
        dist = distance.distance(local1.get_position(), poi.get_position()).kilometers
    new_duration = timedelta(hours=dist / speed)
    if new_duration.total_seconds()*2 <= travel_time.total_seconds():
        return True
    return False


def find_poi_ellipse(ellipse: Ellipse, pois: list[Stop], local1: Stop, local2: Stop, dist_foci: float) -> list[Stop]:
    return [poi for poi in pois
            if ellipse.contains_point(poi.get_position())
            and bounded(poi, local1, local2, dist_foci)]


def stop_replacement(local: SubSegment, stop: Stop) -> None:
    stop_index = local.index(stop)
    first = local.points[0]
    end_time_old = first.end  # 10:30
    first.end = first.start + stop.get_duration()
    end_time_att = first.end  # 10:10

    for point in local.points[1:stop_index]:
        new_start = end_time_att + (point.start - end_time_old)
        if point == stop:
            end_time_att = point.end
        else:
            end_time_old = point.end
            end_time_att = new_start + point.get_duration()
        point.start = new_start
        point.end = end_time_att


# algorithm 3
def flip_flop_exchange(trajectory: Segmented, subtrajectories: list[SubSegment], all_pois: list[Stop]) -> \
        Segmented:

    if not subtrajectories:
        return trajectory

    subsegments = []
    settings = trajectory.privacy_settings
    for local in subtrajectories:
        # procura por pois menos sensíveis que o poi no inicio da trajetória local
        # de [1:-1] para desconsiderar o inicio e fim da trajetória
        pois = [(segment, segment.sensitivity) for segment in local.points[1:-1]
                if isinstance(segment, Stop) and segment.sensitivity < local.points[0].sensitivity]
        if pois:
            least_sensitive, _ = min(pois, key=lambda value: value[1])
            stop_replacement(local, least_sensitive)
            subsegments.append(local)
        else:
            subsegment, found = stop_displacement(local, all_pois, trajectory.length, settings)
            if found:
                subsegments.append(subsegment)

    anonymized = []
    if subsegments[0].init_index != 0:
        anonymized.extend(trajectory.points[0:subsegments[0].init_index])
    anonymized.extend([points for segment in subsegments for points in segment.points[:-1]])

    if len(trajectory.points) - 1 != subsegments[-1].end_index:
        anonymized.extend(trajectory.points[subsegments[-1].end_index:])

    return Segmented(trajectory.uid, anonymized, trajectory.privacy_settings, trajectory.length)

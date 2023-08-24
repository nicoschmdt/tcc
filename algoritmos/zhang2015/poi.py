from dataclasses import dataclass
from datetime import datetime, timedelta

from algoritmos.utils.math_utils import distance, compute_angle
from algoritmos.utils.trajetory import Point


@dataclass
class PoI:
    id: str
    loc: tuple[float, float]
    t: datetime

    def __hash__(self):
        return hash(repr(self))


# Algorithm 2, Pag 4
# POIs consist of the start and the end, stay points and turning
# points. The goal of the privacy protection of entire trajectory
# is achieved by the recognition and protection of these sensitive
# points
def extract_poi(trajectory: list[Point], min_angle: float, min_dist: float, min_stay_time: timedelta) -> set[PoI]:
    pois = {point_to_poi(trajectory[0])}
    current_pos = 1
    next_pos = 2
    point = trajectory[1]

    while current_pos < len(trajectory):
        # TODO: ele quer que eu encontre o próximo ponto da
        # trajetoria que possua uma distancia não menor que
        # minDist tendo o ponto atual (cur_point) como base
        # mas se a distancia de tempo entre esse ponto e o
        # próximo não for maior que minstaytime eu faço o que
        # com o próximo ponto? calculo ele antes?
        next_point = trajectory[current_pos + 1]

        if next_pos >= len(trajectory) > current_pos + 1:
            # TODO: confirmar que esse if funciona caso 1 ponto de uma
            #  trajetoria não seja próximo de nenhum outro.
            # TODO: talvez só fazer um for para encontrar o próximo
            #  ponto com uma distancia minima?
            current_pos += 1
            next_pos = current_pos + 1

        if distance(point.get_coordinates(), next_point.get_coordinates()) > min_dist:
            next_pos += 1
            continue

        if get_time_span(point, next_point) >= min_stay_time:
            if next_pos == current_pos + 1:
                pois |= {point_to_poi(point)}
            else:
                pois |= {PoI(
                    id="",  # TODO
                    loc=get_center(point, next_point),
                    t=point.utc_timestamp
                )}
        else:  # TODO: acho valido considerar que é ponto anterior, atual e proximo
            angle = compute_angle(
                trajectory[current_pos-1].get_coordinates(), point.get_coordinates(), next_point.get_coordinates())
            if angle >= min_angle:
                pois |= {point_to_poi(point)}

        current_pos = next_pos
    pois |= {point_to_poi(trajectory[-1])}  # adding the end
    return pois


def get_time_span(point: Point, next_point: Point) -> timedelta:
    if point.utc_timestamp > next_point.utc_timestamp:
        raise RuntimeError
    return next_point.utc_timestamp - point.utc_timestamp


def get_center(point: Point, point2: Point) -> tuple[float, float]:
    latitude = (point.latitude + point2.latitude)/2
    longitude = (point.longitude + point2.longitude)/2
    return latitude, longitude


def point_to_poi(point: Point) -> PoI:
    return PoI(
        id="",  # TODO: ver o que usar de ID unico
        loc=point.get_coordinates(),
        t=point.utc_timestamp
    )


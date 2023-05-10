import math
from dataclasses import dataclass, field
from typing import List

from algoritmos.utils.semantic import SemanticPoint


@dataclass
class Region:
    center_point: SemanticPoint
    area: int
    points: List[SemanticPoint]
    neighbours: List['Region'] = field(default_factory=list)

    def is_inside(self, point: SemanticPoint) -> bool:
        return distance(self.center_point, point) <= self.area

    def is_neighbour(self, region: 'Region') -> bool:
        return self.area * 2 >= distance(self.center_point, region.center_point) > self.area

    def add_point(self, region: 'Region') -> None:
        self.points.append(region.center_point)
        self.add_neighbour(region)

    def add_neighbour(self, region: 'Region') -> None:
        self.neighbours.append(region)


def distance(point_a: SemanticPoint, point_b: SemanticPoint) -> float:
    x_part = math.pow(point_a.latitude - point_b.latitude, 2)
    y_part = math.pow(point_a.longitude - point_b.longitude, 2)
    return math.sqrt(x_part + y_part)
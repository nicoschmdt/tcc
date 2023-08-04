import math
from dataclasses import dataclass, field

from algoritmos.utils.semantic import SemanticPoint, PoiCategory


@dataclass
class Region:
    center_point: tuple[float, float]
    area: int
    points: list[SemanticPoint]
    categories: dict[PoiCategory, int] = field(default_factory=list)
    neighbours: list['Region'] = field(default_factory=list)

    def is_inside(self, region: 'Region') -> bool:
        return distance(self, region) <= self.area

    def is_neighbour(self, region: 'Region') -> bool:
        return self.area * 2 >= distance(self, region) > self.area

    def add_point(self, region: 'Region') -> None:
        self.add_neighbour(region)

    def join_region(self, region: 'Region') -> None:
        if self.is_neighbour(region):
            self.neighbours.remove(region)

        self.area += region.area

        for category in self.categories:
            self.categories[category] += region.categories[category]

        for point in region.points:
            point.region = self
            self.points.append(point)

    def add_neighbour(self, region: 'Region') -> None:
        self.neighbours.append(region)

    def get_diversity(self) -> int:
        """
        Quantidade de categorias que a região possui.
        """
        diversity = 0
        for category in self.categories.keys():
            if self.categories[category] != 0:
                diversity += 1

        return diversity

    def get_closeness(self, general_poi_distribution: dict[PoiCategory, float]) -> float:
        """
        Calcula a diferença entre a distribuição de PoIs dessa região
        comparada a todas as outras.
        """

        x = self.poi_distribution()
        y = general_poi_distribution
        return sum(x[category] * math.log(x[category] / y[category]) for category in x)

    def poi_distribution(self) -> dict[PoiCategory, float]:
        """
        Distribuição de PoI na região.
        """

        poi_sum = sum(category for category in self.categories.values())
        return {category: self.categories[category] / poi_sum for category in self.categories}


def get_possible_diversity(region_a: Region, region_b: Region) -> int:
    diversity = 0
    for category in region_a.categories.keys():
        if region_a.categories[category] != 0 or region_b.categories[category] != 0:
            diversity += 1

    return diversity


def get_possible_closeness(region_a: Region, region_b: Region, general_distribution: dict[PoiCategory, float]) -> float:
    categories = {}
    poi_sum = 0
    for category in region_a.categories.keys():
        categories[category] = region_a.categories[category] + region_b.categories[category]
        poi_sum += categories[category]

    new_dist = {category: categories[category] / poi_sum for category in categories}

    return sum(new_dist[category] * math.log(new_dist[category] / general_distribution[category]) for category in new_dist)


def distance(region_a: Region, region_b: Region) -> float:
    x_a, y_a = region_a.center_point
    x_b, y_b = region_b.center_point
    x_part = math.pow(x_a - x_b, 2)
    y_part = math.pow(y_a - y_b, 2)
    return math.sqrt(x_part + y_part)

import math
from dataclasses import dataclass, field

from geopy import distance

from algoritmos.utils.math_utils import get_middle
from algoritmos.utils.semantic import PoiCategory


@dataclass
class Region:
    id: int
    center_point: tuple[float, float]
    area: int
    categories: dict[PoiCategory, int] = field(default_factory=dict)
    neighbours_id: set[int] = field(default_factory=set)

    def __hash__(self):
        return hash(repr(self))

    def is_inside(self, region: 'Region') -> bool:
        return distance.distance(self.center_point, region.center_point).meters <= self.area

    def is_neighbour(self, region: 'Region') -> bool:
        value = distance.distance(self.center_point, region.center_point).meters
        result = self.area * 2 >= value > self.area

        return result

    def join_region(self, regions: set['Region']) -> None:
        self.neighbours_id -= regions

        self.area += sum([region.area for region in regions])/len(regions)
        center_points = [region.center_point for region in regions]
        x, y = [sum(tup) for tup in zip(*center_points)]
        middle = (x/len(center_points), y/len(center_points))
        self.center_point = get_middle(self.center_point, middle)

        for category in self.categories:
            for region in regions:
                self.categories[category] += region.categories[category]

    def add_neighbour(self, region: 'Region') -> None:
        self.neighbours_id.add(region.id)
        region.neighbours_id.add(self.id)

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
        category: PoiCategory
        return sum([x[category] * math.log((x[category] / y[category])) for category in PoiCategory
                    if x[category] != 0 if y[category] != 0])

    def poi_distribution(self) -> dict[PoiCategory, float]:
        """
        Distribuição de PoI na região.
        """

        poi_sum = sum(category for category in self.categories.values())
        return {category: self.categories[category] / poi_sum for category in self.categories}


def calculate_diversity(regions: set[Region]) -> int:
    presence = {}
    category: PoiCategory
    for category in PoiCategory:
        for region in regions:
            if region.categories[category] != 0:
                presence[category] = 1

    return sum(presence.values())


def calculate_closeness(region_a: Region, region_b: Region, general_distribution: dict[PoiCategory, float]) -> float:
    categories = {}
    poi_sum = 0
    for category in region_a.categories.keys():
        categories[category] = region_a.categories[category] + region_b.categories[category]
        poi_sum += categories[category]

    new_dist = {category: categories[category] / poi_sum for category in categories}

    return sum(new_dist[category] * math.log(new_dist[category] / general_distribution[category]) for category in new_dist)


def get_closeness(regions: set[Region], dist: dict[PoiCategory, float]) -> float:
    categories = {}
    poi_sum = 0
    category: PoiCategory
    for category in PoiCategory:
        for region in regions:
            try:
                categories[category] += region.categories[category]
            except KeyError:
                categories[category] = region.categories[category]
        poi_sum += categories[category]

    new_dist = {category: categories[category] / poi_sum for category in categories}

    return sum(new_dist[category] * math.log(new_dist[category] / dist[category])
               if new_dist[category] != 0 else 0 for category in new_dist)

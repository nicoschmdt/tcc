from datetime import timedelta, datetime, timezone

from algoritmos.tu2017.treat_data import construct_region
from algoritmos.utils.region import Region
from algoritmos.utils.semantic import SemanticPoint, PoiCategory


def test_is_inside():
    region_one = Region(center_point=(175.0, 85.0),
                        area=150,
                        categories={PoiCategory.Transport: 1},
                        neighbours=[])
    region_two = Region(center_point=(10.0, 5.0),
                        area=150,
                        categories={PoiCategory.Business: 1},
                        neighbours=[])

    assert region_one.is_inside(region_two) is False

    region_three = Region(center_point=(75.0, 85.0),
                          area=150,
                          categories={PoiCategory.Transport: 1},
                          neighbours=[])

    assert region_two.is_inside(region_three)


def test_is_neighbour():
    region_one = Region(center_point=(175.0, 85.0),
                        area=150,
                        categories={PoiCategory.Transport: 1},
                        neighbours=[])
    region_two = Region(center_point=(10.0, 5.0),
                        area=150,
                        categories={PoiCategory.Business: 1},
                        neighbours=[])
    region_three = Region(center_point=(75.0, 85.0),
                          area=150,
                          categories={PoiCategory.Transport: 1},
                          neighbours=[])

    region_four = Region(center_point=(360.0, 134.0),
                         area=150,
                         categories={PoiCategory.Business: 1},
                         neighbours=[])

    assert region_two.is_neighbour(region_one)
    assert region_two.is_neighbour(region_three) is False
    assert region_two.is_neighbour(region_four) is False


def test_join_region():
    pass


def test_add_neighbour():
    pass


def test_get_diversity():
    pass


def test_get_closeness():
    pass


def test_poi_distribution():
    pass


def test_get_possible_diversity():
    pass


def test_get_possible_closeness():
    pass

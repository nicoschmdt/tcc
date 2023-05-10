from datetime import timedelta, datetime, timezone

from algoritmos.utils.region import Region
from algoritmos.utils.semantic import SemanticPoint, PoiCategory

AREA = 150


def construct_region(point: SemanticPoint) -> Region:
    return Region(
        center_point=point,
        area=AREA,
        points=[point],
        neighbours=[]
    )


def test_is_inside():
    point = SemanticPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=9.0, longitude=8.0,
                          utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))

    region = construct_region(point)

    point2 = SemanticPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=50.0, longitude=78.0,
                           utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
    point3 = SemanticPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=100.0, longitude=250.0,
                           utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))

    assert region.is_inside(point2)
    assert not region.is_inside(point3)


def test_is_neighbour():
    point = SemanticPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=9.0, longitude=8.0,
                          utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))

    region = construct_region(point)

    point2 = SemanticPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=50.0, longitude=78.0,
                           utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
    point3 = SemanticPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=100.0, longitude=250.0,
                           utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))

    region2 = construct_region(point2)
    region3 = construct_region(point3)
    assert not region.is_neighbour(region2)
    assert region.is_neighbour(region3)


def test_add_point():
    pass


def test_add_neighbour():
    pass


def test_distance():
    pass

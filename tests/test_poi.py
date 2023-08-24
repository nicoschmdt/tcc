from datetime import datetime, timezone, timedelta

import pytest as pytest

from algoritmos.utils.trajetory import Point, Trajectory
from algoritmos.zhang2015.poi import get_time_span, get_center, point_to_poi, extract_poi


def test_get_time_span():
    point_one = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))
    point_two = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 30, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))

    time_span = get_time_span(point_one, point_two)

    assert type(time_span) is timedelta
    assert time_span == timedelta(seconds=1800)


def test_get_time_span_older_event_last():
    point_one = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))
    point_two = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 30, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))

    with pytest.raises(RuntimeError) as result:
        get_time_span(point_two, point_one)
    assert str(result.value) == ''


def test_get_time_span_same_times():
    point_one = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))
    point_two = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))

    time_span = get_time_span(point_one, point_two)

    assert type(time_span) is timedelta
    assert time_span == timedelta(0)


def test_get_center_both_positive():
    point_one = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=50.0, longitude=120.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))
    point_two = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=20.0, longitude=68.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))

    lat, lon = get_center(point_one, point_two)
    assert lat == (50.0 + 20.0) / 2
    assert lon == (120.0 + 68.0) / 2


def test_get_center_both_negative():
    point_one = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=-50.0, longitude=-120.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))
    point_two = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=-20.0, longitude=-68.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))

    lat, lon = get_center(point_one, point_two)
    assert lat == (-50.0 + -20.0) / 2
    assert lon == (-120.0 + -68.0) / 2


def test_get_center_one_negative():
    point_one = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=-50.0, longitude=-120.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))
    point_two = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                      latitude=20.0, longitude=68.0,
                      utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                      duration=timedelta(0))

    lat, lon = get_center(point_one, point_two)
    assert lat == (-50.0 + 20.0) / 2
    assert lon == (-120.0 + 68.0) / 2


def test_point_to_poi():
    point = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                  latitude=20.0, longitude=68.0,
                  utc_timestamp=datetime(2012, 4, 3, 18, 00, 00, tzinfo=timezone.utc),
                  duration=timedelta(0))

    poi = point_to_poi(point)

    assert poi.loc == (point.latitude, point.longitude)
    assert poi.t == point.utc_timestamp


# TODO: mais testes de extract poi
def test_extract_poi():
    trajectory = Trajectory(points=[
            Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                  latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc),
                  duration=timedelta(0)),
            Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store',
                  latitude=10.0, longitude=5.0, utc_timestamp=datetime(2012, 4, 3, 19, 20, 0, tzinfo=timezone.utc),
                  duration=timedelta(0)),
            Point(name='12', user_id='1', venue_id={'12'}, venue_category_id={'12'}, venue_category='Station',
                  latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc),
                  duration=timedelta(0))
        ])

    pois = extract_poi(trajectory.points, min_angle=30.0, min_dist=200, min_stay_time=timedelta(minutes=20))

    for poi in pois:
        print(f'{poi.loc=}, {poi.t=}')
    print('mewo')

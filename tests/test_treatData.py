from algoritmos.tu2017.treatData import get_venue_category, modify_point, generalize_venue_category, create_similarity_matrix, TuTrajectory, TuPoint, PoiCategory
from algoritmos.utils.trajetoria import Trajectory, Point
from datetime import timedelta, datetime, timezone

def test_get_venue_category():
    trajectory = [
        Trajectory(trajectory=[
                Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store', latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(seconds=3600)),
                Point(name='12', user_id='1', venue_id={'12'}, venue_category_id={'12'}, venue_category='Station', latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
            ])
    ]

    expected_result = [
        TuTrajectory(trajectory=[
            TuPoint(name='10', user_id='1', category={PoiCategory.Business}, latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(seconds=3600)),
            TuPoint(name='12', user_id='1', category={PoiCategory.Transport}, latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
        ], n=1)
    ]

    altered = get_venue_category(trajectory)

    assert altered == expected_result


def test_modify_point():
    point = Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, venue_category='Store', latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(seconds=3600))

    expected_point = TuPoint(name='10', user_id='1', category={PoiCategory.Business}, latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(seconds=3600))

    altered = modify_point(point)

    assert altered == expected_point

def test_generalize_venue_category():
    assert generalize_venue_category('Gym') == PoiCategory.Entertainment
    assert generalize_venue_category('College') == PoiCategory.Education
    assert generalize_venue_category('Park') == PoiCategory.Scenery
    assert generalize_venue_category('Restaurant') == PoiCategory.Business
    assert generalize_venue_category('Facility') == PoiCategory.Industry
    assert generalize_venue_category('House') == PoiCategory.Residence
    assert generalize_venue_category('Train') == PoiCategory.Transport

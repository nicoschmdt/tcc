from algoritmos.trajetoria import return_dict, create_point, Trajectory, Point, split_trajectories, add_duration
from datetime import timedelta, datetime, timezone
from typing import List, Set, Sequence

def test_create_point():
    point = ['1541','4f0fd5a8e4b03856eeb6c8cb','4bf58dd8d48988d10c951735','Cosmetics Shop',
                '35.70510109','139.61959','540','Tue Apr 03 18:17:18 +0000 2012']

    created_point = create_point(point)

    assert point[0] == created_point.user_id
    assert {point[1]} == created_point.venue_id
    assert {point[2]} == created_point.venue_category_id
    assert float(point[4]) == created_point.latitude
    assert float(point[5]) == created_point.longitude
    assert datetime.strptime(point[7],'%a %b %d %H:%M:%S %z %Y') == created_point.utc_timestamp


def test_split_trajectory():
    trajectories = {
        '1': Trajectory(trajectory=[
                Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 17, 18, tzinfo=timezone.utc), duration=timedelta(0)),
                Point(name='11', user_id='1', venue_id={'11'}, venue_category_id={'11'}, latitude=10.0, longitude=5.0, utc_timestamp=datetime(2012, 4, 3, 19, 20, 9, tzinfo=timezone.utc), duration=timedelta(0)),
                Point(name='12', user_id='1', venue_id={'12'}, venue_category_id={'12'}, latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 4, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
            ], n=1),
    }

    expected_trajectories = [
        Trajectory(trajectory=[
                Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 17, 18, tzinfo=timezone.utc), duration=timedelta(0)),
                Point(name='11', user_id='1', venue_id={'11'}, venue_category_id={'11'}, latitude=10.0, longitude=5.0, utc_timestamp=datetime(2012, 4, 3, 19, 20, 9, tzinfo=timezone.utc), duration=timedelta(0)),
            ], n=1),
        Trajectory(trajectory=[
                Point(name='12', user_id='1', venue_id={'12'}, venue_category_id={'12'}, latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 4, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
            ], n=1)
    ]

    splitted_trajectories = split_trajectories(trajectories, 0)

    assert splitted_trajectories == expected_trajectories

def test_add_duration():
    trajectories = [
        Trajectory(trajectory=[
                Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(0)),
                Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, latitude=10.0, longitude=5.0, utc_timestamp=datetime(2012, 4, 3, 19, 20, 0, tzinfo=timezone.utc), duration=timedelta(0)),
                Point(name='12', user_id='1', venue_id={'12'}, venue_category_id={'12'}, latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
            ], n=1)
    ]

    expected_result = [
        Trajectory(trajectory=[
                Point(name='10', user_id='1', venue_id={'10'}, venue_category_id={'10'}, latitude=0.0, longitude=0.0, utc_timestamp=datetime(2012, 4, 3, 18, 20, 0, tzinfo=timezone.utc), duration=timedelta(seconds=3600)),
                Point(name='12', user_id='1', venue_id={'12'}, venue_category_id={'12'}, latitude=9.0, longitude=8.0, utc_timestamp=datetime(2012, 4, 3, 20, 21, tzinfo=timezone.utc), duration=timedelta(0))
            ], n=1)
    ]

    with_duration = add_duration(trajectories)

    assert with_duration == expected_result


def test_return_dict_basic():
    dataset_name = 'datasetTest.csv'
    #TODO
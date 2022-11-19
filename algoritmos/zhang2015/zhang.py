import csv


# construct trajectories

# informações
# o POI consiste do inicio e fim da trajetoria, pontos de parada e pontos de virada


# The start and the end of a trajectory are added into the set directly during extracting

# POIs. If the angle of two adjacent segments exceeds a threshold which is set before-
# hand, the point which connects these two segments is a turning point. Then add the

# turning point into the set. Stay points are locations or approximate locations which the
# stay time exceeds a threshold. There are two cases: One is stopping for a long time at

# one location; the other is wandering for a long time near a location. For the first situa-
# tion, we just need to judge the stay time between a point and the next one. If the stay

# time is larger than the predefined threshold, the point would be regarded as a stay

# point, and be added to the set. For the second situation, points which are near the loca-
# tion need to find first. If the spatial distance between two points is less than MinDist,

# these points will be looked as one location. A represented point is the nearest point to
# the center point. The stay time of this place is the time span between the first point
# and the last point. If the stay time exceeds the threshold MinStayTime, this
# represented point of this place is added into the set, the other points of this place are
# removed finally. Algorithm 2 gives a description about the POI extracting.

# o que preciso:
#       - uma trajetória, angulo minimo, distancia minima, tempo de espera minimo
#       tá meio dificil pensar em um jeito de recolher essas informações

def return_dict(name):
    trajectories = {}
    with open(name) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            # print(row)
            user_id, *data = row
            # print(data)
            if user_id not in trajectories:
                trajectories[user_id] = data
            else:
                trajectories[user_id].append(data)
                # print(trajectories[user_id])
            # point_created = Point(
            #     row[1],
            #     row[0],
            #     {row[1]},
            #     {row[2]},
            #     float(row[4]),
            #     float(row[5]),
            #     int(row[6]),
            #     datetime.strptime(row[7],'%a %b %d %H:%M:%S %z %Y'),
            #     timedelta(hours=0))
            # trajectories[user_id].trajectory.append(point_created)
    return trajectories


# extracting POIs - algorithm 2
# inputs: trajectory t, minAngle, minDist, minStayTime



if __name__ == '__main__':
    trajectories = return_dict('resources/dataset_TSMC2014_TKY.csv')
    # for trajectory in trajectories.items():
    #     print(trajectory)
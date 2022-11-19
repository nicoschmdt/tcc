import numpy as np
from datetime import timedelta,datetime
from geopy.distance import geodesic

#10 and 0.5 are thresholds
def msm(trajectory_a,trajectory_b):
    results = []
    for point_a in trajectory_a.trajectory:
        line = []
        for point_b in trajectory_b.trajectory:
            variable = 0
            if distance(point_a,point_b) < 2:
                variable = 1
            if time(point_a,point_b) < 0.5:
                variable += 1
            if semantics(point_a,point_b) >= 0.5:
                variable += 1
            line.append(variable/3)
        results.append(line)
    ab,ba = score(results)
    return (ab + ba)/(len(trajectory_a.trajectory)+len(trajectory_b.trajectory))

def score(matrix):
    sum_max_line = 0
    sum_max_column = 0
    for line in matrix:
        sum_max_line += max(line)
    for i in range(len(matrix[0])):
        max_column = matrix[0][i]
        for line in matrix[1:]:
            max_column = max(max_column,line[i])
        sum_max_column += max_column
    return sum_max_line,sum_max_column

#space dimension
def distance(a,b):
    coordinate_one = (a.latitude,a.longitude)
    coordinate_two = (b.latitude,b.longitude)
    return geodesic(coordinate_one,coordinate_two).miles

#time dimension
def time(a,b):
    tempo2_a = a.utc_timestamp + a.duration
    tempo2_b = b.utc_timestamp + b.duration
    if tempo2_a < b.utc_timestamp or tempo2_b < a.utc_timestamp:
        return 1
    numerador = diam(max(a.utc_timestamp,tempo2_a),min(b.utc_timestamp,tempo2_b))
    divisor = diam(min(a.utc_timestamp,b.utc_timestamp),max(tempo2_a,tempo2_b))
    if divisor == timedelta(hours=0):
        return 1
    return 1 - (numerador/divisor)

def diam(a,b):
    return abs(b-a)

#semantic dimension
def semantics(a,b):
    if a.venue_category_id.intersection(b.venue_category_id):
        return 1
    return 0
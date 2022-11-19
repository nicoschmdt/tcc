import csv
import math
import similarity
from geopy.distance import geodesic
from dataclasses import dataclass
from datetime import timedelta,datetime
from networkx import Graph
from pprint import pprint
from numpy import argmax,argmin
from typing import List,Set

@dataclass
class Point:
    name: str
    user_id: str
    venue_id: Set[str]
    venue_category_id: Set[str]
    latitude: float
    longitude: float
    timezone_offset: int
    utc_timestamp: datetime
    duration: float

@dataclass
class Trajectory:
    trajectory: List[Point]
    n: int = 1

def main(name,anonymity_criteria):
    trajectories = return_dict(name)
    trajectories = split_trajectories(trajectories)
    trajectories = add_duration(trajectories)
    similarity_matrix = create_similarity_matrix(trajectories)
    anonymized = merge_trajectories(trajectories,similarity_matrix,anonymity_criteria)

def return_dict(name):
    trajectories = {}
    with open(name) as csvfile:
        reader = csv.reader(csvfile)
        next(reader)
        for row in reader:
            user_id, *data = row
            if user_id not in trajectories:
                trajectories[user_id] = Trajectory([])
            point_created = Point(
                row[1],
                row[0],
                {row[1]},
                {row[2]},
                float(row[4]),
                float(row[5]),
                int(row[6]),
                datetime.strptime(row[7],'%a %b %d %H:%M:%S %z %Y'),
                timedelta(hours=0))
            trajectories[user_id].trajectory.append(point_created)
    return trajectories

#merging two spatiotemporal points, returns a new Point of the merged locations
def merge_points(point_one,point_two,diversity_criteria,closeness_criteria,trajectories):
    timestamp1 = point_one.utc_timestamp
    timestamp2 = point_two.utc_timestamp
    #prob gotta turn this one like the utc_timestamp format
    timestamp = min(timestamp1,timestamp2)
    duration = max(point_one.duration + timestamp1,
                   point_two.duration + timestamp2)
    # location = get_connected_region(graph,point_one,point_two)
    duration -= timestamp
    location = point_one.venue_id | point_two.venue_id
    categories = point_one.venue_category_id | point_two.venue_category_id

    graph = generate_distance_graph([point
                                 for tr in trajectories
                                 for point in tr.trajectory])

    points = [point_one,point_two]
    diversity = get_diversity(location)

    while diversity < diversity_criteria:
        x = nearest_points(point_one,graph)
        B = []
        for x_i, _ in x:
            holder = location | x_i.venue_id
            B.append(get_diversity(holder))
        i = argmax(B)
        x_i, _ = x[i]
        location |= x_i.venue_id
        categories |= x_i.venue_category_id
        points.append(x_i)
        diversity = get_diversity(location)

    all_points = [graph.nodes[node]['point'] for node in graph.nodes] + points

    #arrumar
    closeness = get_closeness(points,all_points)
    tries = 0
    while closeness > closeness_criteria and tries < 100:
        x = nearest_points(point_one,graph)
        B = []
        for x_i, _ in x:
            holder_point = points + [x_i]
            B.append(get_closeness(holder_point,all_points))
        i = argmin(B)
        x_i, _ = x[i]
        location |= x_i.venue_id
        categories |= x_i.venue_category_id
        points.append(x_i)
        closeness = get_closeness(points,all_points)
        tries += 1

    #create new point
    new_point = Point(
        name=point_one.name,
        user_id='',
        venue_id=location,
        venue_category_id=categories,
        latitude=point_one.latitude,#ver com a fernanda como fazer em relação a latitude
        longitude=point_one.longitude,# e longitude dos pontos mergeados
        timezone_offset=point_one.timezone_offset,
        utc_timestamp=timestamp,
        duration=duration)

    return new_point

def nearest_points(point: Point, g: Graph,n: int = 10):
    point_a = point.name

    nearest = sorted(
        [
            (g.nodes[point_b]['point'], g.edges[point_a, point_b]['weight'])
            for point_b in g.nodes
        ], key=lambda k: k[1])
    return nearest[:n]

#receives a trajectory list and generates a new one with the duration category updated
def add_duration(trajectories):
    new_list = []
    for trajectory in trajectories:
        #iterate in each segment of the trajectory
        point_one = trajectory.trajectory[0] #the point that will be used as a comparison
        new_trajectory = Trajectory([])
        for segment in trajectory.trajectory[1:]:
            if point_one.venue_id != segment.venue_id:
                new_trajectory.trajectory.append(point_one)
                point_one = segment
            #if its the same location just update the duration of it
            else:
                timestamp_one = point_one.utc_timestamp
                timestamp_two = segment.utc_timestamp
                new_duration = timestamp_two - timestamp_one
                point_one.duration = new_duration + point_one.duration
        new_trajectory.trajectory.append(point_one)
        new_list.append(new_trajectory)
    return new_list

def build_neighbours_matrix(trajectories):
    matrix = []
    for trajectory in trajectories:
        for point in trajectory.trajectory:
            list_point = []
            for trajectory2 in trajectories:
                for point2 in trajectory2.trajectory:
                    if point == point2:
                        list_point.append(0)
                    else:
                        list_point.append(calculate_distance(point,point2))
            matrix.append(list_point)
    return matrix

#generates a graph with distances
def generate_distance_graph(points: List[Point]):
    g = Graph({
            point_a.name: {
                point_b.name: {
                    # Ter um dicionário com esse 'weight' como chave é
                    # necessário para o networkx montar um grafo com pesos
                    'weight': calculate_distance(point_a, point_b) if point_a != point_b
                              else float('inf')
                } for point_b in points
            } for point_a in points
        })
    for point, node in zip(points, g.nodes):
        g.nodes[node]['point'] = point
    return g
#to know if venue 2 and venue1 are neighbours
def is_neighbour(graph,venue1,venue2):
    for neighbor, _ in graph[venue1]:
        if neighbor == venue2:
            return True
    return False

def calculate_distance(point_one,point_two):
    coordinate_one =  (point_one.latitude, point_one.longitude)
    coordinate_two = (point_two.latitude,point_two.longitude)
    return geodesic(coordinate_one,coordinate_two).miles

def Dijkstra(graph, source):
    queue = set()
    distances = {}
    previous = {}
    for vertex in graph:
        distances[vertex] = float('inf')
        previous[vertex] = None
        queue.add(vertex)
    for venue_id in source.venue_id:
        distances[venue_id] = 0

    while queue:
        u = min(queue, key=lambda k: distances[k])
        queue.remove(u)

        for neighbor in graph[u]:
            venue_id, distance = neighbor
            alt = distances[u] + distance
            if alt < distances[venue_id]:
                distances[venue_id] = alt
                previous[venue_id] = u

    return distances,previous

def get_connected_region(graph,source, destiny):
    distances,previous = Dijkstra(graph,source)
    path = [destiny]
    it = next(iter(destiny.venue_id))
    while destiny != source:
        destiny = previous[it]
        if destiny is None:
            break
        path.append(destiny)
        it = destiny
    return [*reversed(path + [source])]

#receives a list of venue_ids and returns a list of neighbors
def get_neighbors(locations,graph):
    neighbors = set()
    for location in locations:
        if isinstance(location, str):
            neighbors |= {*graph[location]}
        else:
            for venue_id in location.venue_id:
                neighbors |= {*graph[venue_id]}
    return neighbors

#get how many diverse venue_ids we have in a point
def get_diversity(places):
    return len(places)

def poi_distribution(points):
    m = {}
    for point in points:
        for category in point.venue_category_id:
            try:
                m[category] += 1
            except KeyError:
                m[category] = 1
    m_sum = sum(v for v in m.values())
    return {u: m[u]/m_sum for u in m}

#get how many diverse category_ids we have in a point
def get_closeness(r, R):
    x = poi_distribution(r)
    y = poi_distribution(R)
    return sum(x[u]*math.log(x[u]/y[u]) for u in x)

#merging trajectories // acho que vou precisar passar o graph tb..
# The algorithm will iterate until all the trajectories in T have been k-anonymized.
def merge_trajectories(trajectories,similarity_matrix,anonymity_criteria):
    generalized_dataset = []
    possible_to_merge = True #depois penso em um nome melhor
    while possible_to_merge: #enquanto tiver duas trajetorias com o k menor que o criterio
        k = argmax(similarity_matrix)#os que tiverem a maior similaridade serão escolhidos
        i = k % len(similarity_matrix)
        j = k // len(similarity_matrix)
        new_trajectory = merge(trajectories[i],trajectories[j], trajectories)
        new_trajectory.n = trajectories[i].n + trajectories[j].n
        #tirando as trajetorias da lista de trajectories
        trajectories.pop(i)
        trajectories.pop(j-1)
        #how do I remove things from the similarity matrix??
        remove_from(i,j,similarity_matrix)
        if new_trajectory.n < anonymity_criteria:
            # for trajectory in trajectories:
            add_similarity(similarity_matrix,trajectories,new_trajectory)
            trajectories.append(new_trajectory)
        else:
            generalized_dataset.append(new_trajectory)
        if len(trajectories) < 2: #preciso pensar nessa condição aqui
            possible_to_merge = False
    return generalized_dataset

#returns a list of trajectories splitted by day
def split_trajectories(trajectories):
    splitted_trajectories = []
    for user_id in trajectories:
        trajectory = trajectories[user_id].trajectory
        compare = trajectory[0]
        lista = Trajectory([compare])
        for point in trajectory[1:]:
            if compare.utc_timestamp.day == point.utc_timestamp.day:
                lista.trajectory.append(point)
            else:
                splitted_trajectories.append(lista)
                lista = Trajectory([point])
            compare = point
        splitted_trajectories.append(lista)

    splitted_trajectories = [trajectory
                            for trajectory in splitted_trajectories
                            if len(trajectory.trajectory) > 6]

    return splitted_trajectories

def create_similarity_matrix(trajectories):
    matrix = []
    for trajectory_one in trajectories:
        lista = []
        for trajectory_two in trajectories:
            if trajectory_one == trajectory_two:
                lista.append(float('-inf'))
            else:
                lista.append(similarity.msm(trajectory_one,trajectory_two))
        matrix.append(lista)
    return matrix

#I plan on organizing a lil better this method
def merge(trajectory_one,trajectory_two,trajectories):
    bigger_traj = trajectory_two.trajectory.copy()
    smaller_traj = trajectory_one.trajectory.copy()

    if len(trajectory_two.trajectory) < len(trajectory_one.trajectory):
        smaller_traj, bigger_traj = bigger_traj, smaller_traj

    haventbeenmerged = smaller_traj.copy()
    for point in bigger_traj:
        #search for the cheapest merge for this point
        cost = []
        for point2 in smaller_traj:
            cost.append(calculate_distance(point,point2))
        i = argmin(cost)
        if smaller_traj[i] in haventbeenmerged:
            haventbeenmerged.remove(smaller_traj[i])
        #3,3 = respectively diversity criteria and closeness criteria
        new_point = merge_points(point,smaller_traj[i],3,1,trajectories)

        smaller_traj[i] = new_point

    if haventbeenmerged:
        # for point in haventbeenmerged:
        #     if point in smaller_traj:
        #         smaller_traj.remove(point)

        for point in haventbeenmerged:
            cost = []
            for point2 in smaller_traj:
                cost.append(calculate_distance(point,point2))
            i = argmin(cost)
            new_point = (merge_points(point,smaller_traj[i],4,2,trajectories))

            smaller_traj[i] = new_point

    return Trajectory(smaller_traj)

def remove_from(i,j,similarity_matrix):
    similarity_matrix.pop(i)
    similarity_matrix.pop(j-1)
    for line in similarity_matrix:
        line.pop(i)
        line.pop(j-1)

#calcular o custo dessa nova trajetoria com as já existentes e adicionar na sm
def add_similarity(matrix,trajectories,trajectory1):
    cost = []
    for trajectory in trajectories:
        cost.append(similarity.msm(trajectory,trajectory1))
    cost.append('-inf')
    i = 0
    for line in matrix:
        line.append(cost[i])
        i += 1
    matrix.append(cost)

if __name__ == '__main__':
    main('dataset_TSMC2014_TKY.csv', 3)
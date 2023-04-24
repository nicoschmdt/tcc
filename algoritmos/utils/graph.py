import math
from dataclasses import dataclass, field
from typing import List

from algoritmos.utils.semantic import SemanticPoint


@dataclass
class Region:
    center_point: SemanticPoint
    area: int
    points: List[SemanticPoint]
    neighbours: List['Region'] = field(default_factory=list)

    def is_inside(self, point: SemanticPoint) -> bool:
        if distance(self.center_point, point) > self.area:
            return False
        return True

    def is_neighbour(self, region: 'Region') -> bool:
        if distance(self.center_point, region.center_point) < 500:
            return True
        return False

    def add_point(self, region: 'Region') -> None:
        self.points.append(region.center_point)
        self.add_neighbour(region)

    def add_neighbour(self, region: 'Region') -> None:
        self.neighbours.append(region)


def distance(point_a: SemanticPoint, point_b: SemanticPoint) -> float:
    x_part = math.pow(point_a.latitude - point_b.latitude, 2)
    y_part = math.pow(point_a.longitude - point_b.longitude, 2)
    return math.sqrt(x_part + y_part)


@dataclass
class Graph:
    vertices: set[Region]

    def add_vertex(self, region: Region) -> None:
        self.vertices.add(region)

    def remove_vertex(self, region: Region) -> None:
        self.vertices.remove(region)

    def prune_and_simplify(self) -> 'Graph':
        new_graph = Graph()
        united = set()
        for i, region in enumerate(self.vertices):
            if i in united:
                continue

            # triangulo superior
            for j, other_region in enumerate(self.vertices[i:]):
                if i == j or j in united:
                    # região com ela mesma ignora ou trajetória já considerada
                    continue

                # se marcar alguma dessas condições abaixo tenque registrar a região já utilizada
                if other_region.is_inside(region.center_point):
                    # cria uma nova região com os dois pontos dentro
                    united.add(j)
                    region.add_point(other_region)
                elif region.is_neighbour(other_region):
                    # adiciona na vizinhança
                    region.add_neighbour(other_region)
                    other_region.add_neighbour(region)

            new_graph.add_vertex(region)

        return new_graph

    # def connect(region_a: Region, region_b: Region, weight):
    #     """
    #     Adiciona vizinhos à um vértice
    #     usa o peso
    #     """
    #     pass

    # def get_neighbours():
    #     """
    #     Pega os vizinhos de um vértice
    #     """
    #     pass
    #
    # def merge(a: Vertex, b: Vertex) -> Vertex:
    #     pass

    # def dijkstra():
    #     """
    #     implementar dijkstra
    #     """
    #     pass

# def Dijkstra(graph, source):
#     queue = set()
#     distances = {}
#     previous = {}
#     for vertex in graph:
#         distances[vertex] = float('inf')
#         previous[vertex] = None
#         queue.add(vertex)
#     for venue_id in source.venue_id:
#         distances[venue_id] = 0

#     while queue:
#         u = min(queue, key=lambda k: distances[k])
#         queue.remove(u)

#         for neighbor in graph[u]:
#             venue_id, distance = neighbor
#             alt = distances[u] + distance
#             if alt < distances[venue_id]:
#                 distances[venue_id] = alt
#                 previous[venue_id] = u

#     return distances,previous

# def get_connected_region(graph,source, destiny):
#     distances,previous = Dijkstra(graph,source)
#     path = [destiny]
#     it = next(iter(destiny.venue_id))
#     while destiny != source:
#         destiny = previous[it]
#         if destiny is None:
#             break
#         path.append(destiny)
#         it = destiny
#     return [*reversed(path + [source])]

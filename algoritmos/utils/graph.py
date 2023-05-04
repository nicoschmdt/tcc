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
        # ver se 500 funciona como 500 metros
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

    # def get_neighbours():
    #     """
    #     Pega os vizinhos de um vértice
    #     """
    #     pass


def dijkstra(graph: Graph, source: Region):
    """
    Calcula as distancias de todas as regiões dada uma região em específico
    """
    pass
    unchecked_vertices = set()
    distances = {}
    previous = {}
    # todos os nodos são marcados como não visitados e recebem o valor inf
    for vertex in graph.vertices:
        distances[vertex] = float('inf')
        previous[vertex] = None
        unchecked_vertices.add(vertex)

    # o nodo inicial recebe a distancia 0
    distances[source] = 0

    while unchecked_vertices:
        selected_vertex = min(unchecked_vertices, key=lambda k: distances[k])
        unchecked_vertices.remove(selected_vertex)

        for neighbor in selected_vertex.neighbours:
            # create def to get distance between two regions
            distance = 0 # todo oq foi escrito acima
            alt_distance = distances[selected_vertex] + distance
            if alt_distance < distances[neighbor]:
                distances[neighbor] = alt_distance
                previous[neighbor] = selected_vertex

    return distances, previous


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

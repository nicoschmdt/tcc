from dataclasses import dataclass, field

from geopy import distance
from algoritmos.utils.region import Region
from algoritmos.utils.semantic import PoiCategory


@dataclass
class Graph:
    vertices: set[Region] = field(default_factory=set)
    poi_distribution: dict[PoiCategory, float] = field(default_factory=list)

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
                if other_region.is_inside(region):
                    # cria uma nova região com os dois pontos dentro
                    united.add(j)
                    region.join_region(other_region)
                elif region.is_neighbour(other_region):
                    # adiciona na vizinhança
                    region.add_neighbour(other_region)
                    other_region.add_neighbour(region)

            new_graph.add_vertex(region)

        return new_graph


def dijkstra(graph: Graph, source: Region):
    """
    Calcula as distancias de todas as regiões dada uma região em específico
    """
    unchecked_vertices = set()
    distances = {}
    previous = {}
    # todos os nodos são marcados como não visitados e recebem o valor inf
    for vertex in graph.vertices:
        distances[vertex] = float('inf')
        previous[vertex] = None
        unchecked_vertices.add(vertex)

    # o nodo inicial recebe a distancia 0
    distances[source] = 0.0

    while unchecked_vertices:
        selected_vertex = min(unchecked_vertices, key=distances.get)
        unchecked_vertices.remove(selected_vertex)

        for neighbor in selected_vertex.neighbours:
            weight = distance.distance(selected_vertex.center_point, neighbor.center_point).meters
            alt_distance = distances[selected_vertex] + weight
            if alt_distance < distances[neighbor]:
                distances[neighbor] = alt_distance
                previous[neighbor] = selected_vertex

    return distances, previous


def get_connected_region(graph: Graph, source: Region, destiny: Region) -> Region:
    distances, previous = dijkstra(graph, source)
    path = [destiny]
    it = destiny
    while destiny != source:
        destiny = previous[it]
        if destiny is None:
            break
        path.append(destiny)
        it = destiny
    # TODO: revisar como funciona a região resultante, preciso ver com a fernanda como vai funcionar
    result = Region(
        center_point=source.center_point,
        area=source.area,
        categories=source.categories,
        neighbours=source.neighbours
    )
    for region in path:
        result.join_region(region)

    return result

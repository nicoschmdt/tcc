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

    def prune_and_simplify(self) -> \
            tuple['Graph', dict[int, list[int]]]:
        new_graph = Graph()
        not_visited = self.vertices.copy()
        id_merged = {}
        for region in self.vertices.copy():
            if region not in not_visited:
                continue
            not_visited.remove(region)

            remove = {other for other in not_visited if other.is_inside(region)}
            if remove:
                region.join_region(remove)
                id_merged[region.id] = [reg.id for reg in remove]
                not_visited -= remove

            neighbours = {other.id for other in not_visited if region.is_neighbour(other)}
            print(f'{len(not_visited)}')
            region.neighbours_id |= neighbours
            new_graph.add_vertex(region)
        new_graph.poi_distribution = self.poi_distribution
        return new_graph, id_merged


def dijkstra(graph: Graph, source: Region, regions: dict[int, Region]):
    """
    Calcula as distancias de todas as regiões dada uma região em específico
    """
    unchecked_vertices = set()
    distances = {}
    previous = {}
    # todos os nodos são marcados como não visitados e recebem o valor inf
    for vertex in graph.vertices:
        distances[vertex.id] = float('inf')
        previous[vertex.id] = None
        unchecked_vertices |= {vertex.id}

    # o nodo inicial recebe a distancia 0
    distances[source.id] = 0.0

    while unchecked_vertices:
        selected_vertex_id = min(unchecked_vertices, key=distances.get)
        unchecked_vertices.remove(selected_vertex_id)
        vertex = regions[selected_vertex_id]

        for neighbour_id in vertex.neighbours_id:
            neighbour = regions[neighbour_id]
            weight = distance.distance(vertex.center_point, neighbour.center_point).meters
            alt_distance = distances[vertex.id] + weight
            if alt_distance < distances[neighbour.id]:
                distances[neighbour] = alt_distance
                previous[neighbour] = vertex.id

    return distances, previous


def get_connected_region(graph: Graph, sources: list[int], destinies: list[int],
                         regions: dict[int, Region]) -> set[Region]:
    intersection = set(sources) & set(destinies)
    if intersection:
        ids = list(set(sources) | set(destinies))
        return {regions[region_id] for region_id in ids}

    cost = -1
    start = None
    final = None
    for init in sources:
        for end in destinies:
            if distance.distance(regions[init].center_point, regions[end].center_point) > cost:
                start = init
                final = end

    distances, previous = dijkstra(graph, regions[start], regions)
    destiny = final
    path = [destiny]
    it = destiny
    while destiny != start:
        destiny = previous[it]
        if destiny is None:
            break
        path.append(destiny)
        it = destiny

    result = set(sources) | set(destinies) | set(path)
    return {regions[region_id] for region_id in result}

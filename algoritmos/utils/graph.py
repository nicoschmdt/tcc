from dataclasses import dataclass, field

@dataclass
class Region:
    points: list[TuPoint] # talvez usar sets
    neighbours: list[Region] = field(default_factory=list)

@dataclass
class Graph:

    vertices: set[Region]

    def add_vertex(region: Region) -> None:
        """
        Adiciona um vértice no grafo
        """
        vertices.add(region)

    def connect(region_a: Region, region_b: Region, weight):
        """
        Adiciona vizinhos à um vértice
        usa o peso
        """
        pass

    def get_neighbours():
        """
        Pega os vizinhos de um vértice
        """
        pass

    def merge(a: Vertex, b: Vertex) -> Vertex:
        pass


    def dijkstra():
        """
        implementar dijkstra
        """
        pass

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
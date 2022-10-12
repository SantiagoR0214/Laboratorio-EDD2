from re import A
import geopy.distance
import pandas as pd
import unicodedata
import folium


class City:
    """
    A class for the vertices in the graph.
    
    Attributes
    ----------
    name: str
    coords: tuple[int, int]
    destinations: list[City]
    marker: folium.CircleMarker, default None
    """
    def __init__(self, name: str, lat: float, lon: float) -> None:
        self.name = name
        self.coords = [lat, lon]
        self.destinations = []
        self.marker = None
        
    def __repr__(self):
        return f"{self.name}({self.coords[0]},{self.coords[1]})"

def remove_accents(input_str: str) -> str:
    """
    Returns input string with its accents removed.
    
    Taken from:
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    
    Parameters
    ----------
    input_str: str
    """
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def get_vertices() -> list[City]:
    """
    Returns a list containing vertices with the information of capital cities.
    """
    vertices = []
    with open(file='capital_coords.csv', encoding='utf-8') as f:
        while (line:=f.readline()) != '':
            line = line.removesuffix('\n').split(';')
            vertices.append(City(line[0], line[1], line[2]))
    return vertices

def get_destinations(vertices: list[City]) -> None:
    """
    Adds the destinations for each City contained in input list.
    """
    # Creates dataframe from flight_data
    data = pd.read_csv(filepath_or_buffer='flight_data.csv', delimiter=';')
    data = data[data['ORIGEN'] != data['DESTINO']]
    for v in vertices:
        v.destinations.clear()
        # Filters travel destinies for current origin City
        dest = data[
            data['ORIGEN']==remove_accents(v.name).upper()
        ]['DESTINO'].drop_duplicates()
        # Iterates through destiny cities
        for row in dest:
            # Finds vertex for destiny city and appends it 
            # to origin City destinations
            for u in vertices:
                if remove_accents(u.name).upper() == row:
                    v.destinations.append(u)
                    break


def weight(u: City, v: City) -> float:
    """
    Returns the weight of an edge given its incident vertices.

    The weight is the distance between the two cities in kilometers.
    """
    return geopy.distance.distance(
        u.coords,
        v.coords,
    ).km
    
def dijkstra(V: list[City], source: City) -> tuple[dict, dict]:
    """
    Finds the minimal paths from a source vertex to all other vertexes in V.
    
    Parameters
    ----------
    V: list[City]
        Vertices of the graph.
    source: City
        Source of the paths to find.
        
    Returns
    -------
    dist: dict
        Contains the distances of the shortest paths to each vertex.
    parent: dict
        Contains the vertices each vertex should go back to in order
        to form the path towards it.??? esto ni se entiende pero ajá
    """
    dist, parent, visited = {}, {}, {}
    q = []
    for u in V:
        dist[u] = 999999999
        parent[u] = None
        visited[u] = False
    dist[source] = 0
    q.extend(V)
    while len(q) > 0:
        # Select the element of q with the min distance
        u = min(dist, key=dist.get)
        dist_aux = dist.copy()
        while not u in q:
            dist_aux.pop(u)
            u = min(dist_aux, key=dist_aux.get)
        q.remove(u)         # Remove from q
        visited[u] = True   # Mark as visited
        for v in u.destinations:
            aux = dist[u] + weight(u, v)    # Value of current path
            if aux < dist[v] and not visited[v]:
                dist[v] = aux
                parent[v] = u
    return dist, parent

def draw_shortest_path(map: folium.Map, V: list[City], 
                       source: City, destination: list[City] = None) -> None:
    """
    Draws the shortest path from a source to one or multiples destinations 
    onto a map.
    
    If destination is None, it will draw the shortest paths from source to 
    each vertex in V.
    
    Parameters
    ----------
    map: folium.Map
        Map to draw path(s) on.
    V: list[City]
        List of cities/vertices of the graph.
    source: City
        City the path(s) start from.
    destination: list[City], default None
        Cities the path ends on.
    """
    # Runs dijkstra on V
    dist, parent = dijkstra(V, source)
    
    if destination == None: 
        # Sets list of destinations as V
        destination = V
    
    for d in destination:
        # Creates FeatureGroup for current destination
        layer = folium.FeatureGroup(name=d.name, overlay=True)
        # Adds CircleMarker for current destination showing total distance 
        # of the shortest path towards it
        if dist[d] == 999999999:
            folium.CircleMarker([d.coords[0], d.coords[1]],
                                radius=10,
                                fill_color='red',
                                popup=f'{d.name.upper()}\n\nNo puede llegarse a este destino.',
                                ).add_to(layer)
        else:
            folium.CircleMarker([d.coords[0], d.coords[1]],
                                radius=10,
                                fill_color='red',
                                popup=f'{d.name.upper()}\n\nDistancia total: {round(dist[d], 2)}km',
                                ).add_to(layer)
        # Draws lines from destination to source
        while parent[d] != None:
            folium.PolyLine([[float(i) for i in d.coords], 
                            [float(i) for i in parent[d].coords]],
                            color='red',
                            weight=3,
                            opacity=0.8).add_to(layer)
            d = parent[d]
        # Adds FeatureGroup to map
        layer.add_to(map)
    folium.LayerControl().add_to(map)

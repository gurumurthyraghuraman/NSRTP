from django.contrib.gis.geos import *
from shapely.geometry import *
import copy
import sys


visited_spc = list()

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def is_point_within(polygon, graph):
    graphCopy = copy.deepcopy(graph)
    for key, value in graphCopy.items():
        point = Point(key[0],key[1])
        if polygon.contains(point) or polygon.touches(point):
            graph = removekey(graph, key);
            for ikey, ivalue in graph.items():
                for coor in ivalue:
                    if coor == point:
                        ivalue.remove(coor)
    return graph

def does_line_intersect(polygon, graph):
    graphCopy = copy.deepcopy(graph)
    for key, value in graphCopy.items():
        point = Point(key[0], key[1])
        for coor in value:
            path = LineString([point, coor])
            if path.intersects(polygon):
                graph[key].remove(coor)
    return graph


def dfs(graph, u):
    global size_of_component_spc
    for v in graph[u]:
        if not node_visited[(v.x, v.y)]:
            node_visited[(v.x, v.y)] = True
            size_of_component_spc += 1
            dfs(graph, (v.x, v.y))


def no_of_connected_components(graph):
    connected_component = 0
    global size_of_component_spc
    global largest_size_of_component_spc
    global smallest_size_of_component_spc
    global node_visited;
    node_visited = dict()
    graph_details = dict()
    for key, value in graph.items():
        node_visited[key] = False
    size_of_component_spc = 0
    largest_size_of_component_spc = 0
    smallest_size_of_component_spc = sys.maxsize
    for u in graph:
        if not node_visited[u]:
            node_visited[u] = True
            connected_component += 1
            size_of_component_spc = 1
            dfs(graph, u)
        if size_of_component_spc < smallest_size_of_component_spc:
            smallest_size_of_component_spc = size_of_component_spc
        if size_of_component_spc > largest_size_of_component_spc:
            largest_size_of_component_spc = size_of_component_spc
    graph_details["CC"] = connected_component
    graph_details["LCS"] = largest_size_of_component_spc
    graph_details["SCS"] = smallest_size_of_component_spc
    if connected_component==0:
        graph_details["SCS"] = 0
    graph_details["nodes"] = len(graph)
    graph_details["links"] = 0
    for key, value in graph.items():
        graph_details["links"] = graph_details["links"] + len([item for item in value if item])
    graph_details["links"] = graph_details["links"]/2
    visited_spc.append(graph_details)
    surviving_links = graph_details["links"]
    largest_connected_component_spc = graph_details["LCS"]
    smallest_connected_component_spc = graph_details["SCS"]
    no_of_surviving_nodes_spc = graph_details["nodes"]
    return connected_component, largest_connected_component_spc, smallest_connected_component_spc, surviving_links, no_of_surviving_nodes_spc


def specified_fault(input_graph, specific_fault_points):

    polygon = specific_fault_points.convex_hull
    input_graph = is_point_within(polygon, input_graph)

    input_graph = does_line_intersect(polygon, input_graph)
    a, b, c, d, e = no_of_connected_components(copy.deepcopy(input_graph))
    return a, b, c, d, e




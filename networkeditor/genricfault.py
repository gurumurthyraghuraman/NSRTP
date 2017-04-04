from django.contrib.gis.geos import *

import copy
import math
import sys

r = 700000
buffer = 0.0001
size_of_component = 0
largest_size_of_component = 0
smallest_size_of_component = sys.maxsize
visited = dict()
D_R = (math.pi / 180.0)
R_D = (180.0 / math.pi)
R_MAJOR = 6378137.0
R_MINOR = 6356752.3142
RATIO = (R_MINOR/R_MAJOR)
ECCENT = (math.sqrt(1.0 - (RATIO * RATIO)))
COM = (0.5 * ECCENT)


def deg_rad (ang):
    return ang * D_R


def merc_x(lon):
    return R_MAJOR * deg_rad (lon)


def merc_y(lat):
    lat = min (89.5, max (lat, -89.5))
    phi = deg_rad(lat)
    sinphi = math.sin(phi)
    con = ECCENT * sinphi
    con = pow((1.0 - con) / (1.0 + con), COM)
    ts = math.tan(0.5 * (math.pi * 0.5 - phi)) / con
    return 0 - R_MAJOR * math.log(ts)


def rad_deg(ang):
    return ang * R_D


def merc_lon(x):
    return rad_deg(x) / R_MAJOR


def merc_lat(y):
    ts = math.exp (-y / R_MAJOR)
    phi = (math.pi/2) - 2 * math.atan(ts)
    dphi = 1.0
    for i in range(0, 15):
        if math.fabs(dphi) > 0.000000001:
            con = ECCENT * math.sin(phi)
            dphi = (math.pi/2) - 2 * math.atan (ts * pow((1.0 - con) / (1.0 + con), COM)) - phi
            phi += dphi

    return rad_deg(phi)


def set_of_lines(pa, pb):
    listoflines = list()
    pc = Point(pb.y - pa.y, pa.x - pb.x)
    length = math.sqrt(pc.x * pc.x + pc.y * pc.y)
    pd = Point(pc.x / length, pc.y / length)
    R1 = Point(pa.x + pd.x * r, pa.y + pd.y * r)
    R2 = Point(pa.x - pd.x * r, pa.y - pd.y * r)
    R3 = Point(pb.x + pd.x * r, pb.y + pd.y * r)
    R4 = Point(pb.x - pd.x * r, pb.y - pd.y * r)
    l1 = LineString(R1, R2)
    l2 = LineString(R2, R4)
    l3 = LineString(R4, R3)
    l4 = LineString(R3, R1)
    listoflines.append(l1)
    listoflines.append(l2)
    listoflines.append(l3)
    listoflines.append(l4)
    return listoflines


def line_inter_line(line_list):
    set_lines = copy.deepcopy(line_list)
    list_of_points = list()
    for s in range(0, len(set_lines)-1):
        for t in range(s+1, len(set_lines)):
            inter_line_p = set_lines[s].intersection(set_lines[t])
            if isinstance(inter_line_p, Point):
                list_of_points.append(inter_line_p)

    return list_of_points


def set_of_points(intpoints, p1, p2):
    list_of_int_points = list()
    for i in range(0, len(intpoints)):
        for j in range(0, len(intpoints[i])):
            z = Point(intpoints[i][j][0], intpoints[i][j][1])
            if z.distance(p1) >= r - buffer:
                if z.distance(p1) <= r + buffer:
                    if z.distance(p2) >= r - buffer:
                        if z.distance(p2) <= r + buffer:
                            list_of_int_points.append(z)

    return list_of_int_points


def line_circle_inter(circle, line_list, center_of_circle):
    list_of_points = list()
    for each_line in line_list:
        p = circle.intersection(each_line)

        if len(p) > 0:
            if isinstance(p, Point):
                list_of_points.append(p)

            if isinstance(p, LineString):
                if not p.equals(each_line):
                    for e in p.boundary:
                        if not e.equals(center_of_circle):
                            list_of_points.append(e)

            if isinstance(p, MultiPoint):
                for e in p:
                    if not e.equals(center_of_circle):
                        list_of_points.append(e)

    return list_of_points


def convert_list_to_set(list_of_points):
    set_of_tuples = set()
    return_list_of_points = list()
    for each_point in list_of_points:
        set_of_tuples.add((float("{0:.4f}".format(each_point.x)), float("{0:.4f}".format(each_point.y))))

    for each_tuple in set_of_tuples:
        return_list_of_points.append(Point(each_tuple[0], each_tuple[1]))

    return return_list_of_points


def dfs(graph, u):
    global size_of_component
    for v in graph[u]:
        if not visited[(v.x, v.y)]:
            visited[(v.x, v.y)] = True
            size_of_component += 1
            dfs(graph, v.coords)


def no_of_connected_components(graph):
    connected_component = 0
    global size_of_component
    global largest_size_of_component
    global smallest_size_of_component
    global visited
    largest_size_of_component = 0
    smallest_size_of_component = sys.maxsize
    for u in graph:
        if not visited[u]:
            size_of_component = 1
            visited[u] = True
            connected_component += 1
            dfs(graph, u)
            if size_of_component < smallest_size_of_component:
                smallest_size_of_component = size_of_component
            if size_of_component > largest_size_of_component:
                largest_size_of_component = size_of_component

    return connected_component


def str_of_graph(input_graph):
    new_input_graph = dict()
    for key in input_graph:
        new_list = list()
        for val in input_graph[key]:
            new_list.append((val.x, val.y))
        new_input_graph[key] = new_list

    return str(new_input_graph)


def remove_edge_from_graph(new_edge_in_graph, list_of_nodes):
    new_edge_graph = copy.deepcopy(new_edge_in_graph)
    for new_edge_key in new_edge_graph:
        for each_val_in_key in new_edge_graph[new_edge_key]:
            if (each_val_in_key.x, each_val_in_key.y) in list_of_nodes:
                new_edge_in_graph[new_edge_key].remove(each_val_in_key)

    return copy.deepcopy(new_edge_in_graph)


def remove_node_from_graph(new_in_graph, node_to_be_removed):
    updated_graph_1 = copy.deepcopy(new_in_graph)
    list_of_nodes_to_be_removed = list()
    for new_graph_key in copy.deepcopy(new_in_graph):
        new_r_node = Point(new_graph_key[0], new_graph_key[1])

        if new_r_node.equals(node_to_be_removed):
            del new_in_graph[(new_r_node.x, new_r_node.y)]
            list_of_nodes_to_be_removed.append((new_r_node.x, new_r_node.y))

    new_node_graph = copy.deepcopy(new_in_graph)
    if len(list_of_nodes_to_be_removed) > 0:
        updated_graph_1 = remove_edge_from_graph(new_node_graph, list_of_nodes_to_be_removed)

    #print(str_of_graph(updated_graph_1))
    return updated_graph_1


def remove_inter_edge_from_graph(new_inter_edge_graph, new_i_point):
    i_new_circle = new_i_point.buffer(r+buffer)
    new_inter_graph = copy.deepcopy(new_inter_edge_graph)
    for each_key in new_inter_graph:
        new_key_point = Point(each_key[0], each_key[1])
        for new_key_edge in new_inter_graph[each_key]:
            new_line_edge = LineString(new_key_point, new_key_edge)
            if i_new_circle.intersects(new_line_edge):
                new_inter_edge_graph[each_key].remove(new_key_edge)

    return copy.deepcopy(new_inter_edge_graph)


def graph_i_point(in_graph, i_point, lst_nodes):

    updated_graph_2 = copy.deepcopy(in_graph)
    for eachGraphNode in lst_nodes:
        if eachGraphNode.distance(i_point) <= r:
            updated_graph_2 = remove_node_from_graph(copy.deepcopy(updated_graph_2), eachGraphNode)

    updated_graph_3 = remove_inter_edge_from_graph(updated_graph_2, i_point)
    return updated_graph_3


def remove_edges_only_from_graph(center_i_point, graph_input):
    updated_graph_3 = copy.deepcopy(graph_input)
    circle_from_i_point = center_i_point.buffer(r+buffer)
    for each_key in graph_input:
        for each_val in graph_input[each_key]:
            z = Point(each_key[0], each_key[1])
            edge_line_string = LineString(z, each_val)
            if circle_from_i_point.intersects(edge_line_string):
                updated_graph_3[each_key].remove(each_val)

    return copy.deepcopy(updated_graph_3)


def remove_node_only_from_graph(center_i_point, node_graph_input):
    updated_graph_4 = copy.deepcopy(node_graph_input)
    for each_key in node_graph_input:
        z = Point(each_key[0], each_key[1])
        if z.distance(center_i_point) <= r:
            del updated_graph_4[each_key]

    return updated_graph_4


def compute_generic_fault(input_graph):
    #print("From Generic Function")
    #print(r)
    global size_of_component
    global largest_size_of_component
    global smallest_size_of_component
    global visited
    input_graph2 = copy.deepcopy(input_graph)
    nodevisited = dict()
    map_of_circles = dict()
    list_of_circle_centers = list()
    list_of_nodes = list()
    list_of_i_points = list()
    list_of_lines = list()
    for key in input_graph:
        z = Point(key[0], key[1])
        nodevisited[key] = False
        list_of_nodes.append(z)
        map_of_circles[(z.x, z.y)] = z.buffer(r)

    for eachNode in list_of_nodes:
        list_of_rem_nodes = copy.deepcopy(list_of_nodes)
        #list_of_rem_nodes.remove(eachNode)
        for everyNode in list_of_rem_nodes:
            if eachNode.distance(everyNode) == 2 * r:
                list_of_i_points.append(Point((eachNode.x + everyNode.x) / 2, (eachNode.y + everyNode.y) / 2))
        for dest in input_graph[(eachNode.x, eachNode.y)]:
            list_of_lines.extend(set_of_lines(eachNode, dest))

    list_of_i_points.extend(line_inter_line(list_of_lines))

    list_of_circle_centers.extend(list(map_of_circles.keys()))
    for l in range(0, len(list_of_circle_centers) - 1):
        y = Point(list_of_circle_centers[l][0], list_of_circle_centers[l][1])
        for m in range(l + 1, len(list_of_circle_centers)):
            x = Point(list_of_circle_centers[m][0], list_of_circle_centers[m][1])
            circle1 = map_of_circles[(x.x, x.y)]
            circle2 = map_of_circles[(y.x, y.y)]
            inter_polygon = circle1.intersection(circle2)
            if not inter_polygon.empty:
                list_of_i_points.extend(set_of_points(inter_polygon, y, x))

            list_of_i_points.extend(line_circle_inter(circle1, list_of_lines, x))
            list_of_i_points.extend(line_circle_inter(circle2, list_of_lines, x))

    set_of_i_points = convert_list_to_set(list_of_i_points)

    list_connected_components = list()
    list_of_shortest_components = list()
    list_of_largest_components = list()
    set_of_graphs = set()
    unique_set_of_i_points = list()
    i_point_dict = dict()
    #print(len(set_of_i_points))
    for eachIPoint in set_of_i_points:
        #print((merc_lat(eachIPoint.y), merc_lon(eachIPoint.x)))
        visited = dict()
        new_graph = dict()
        new_graph = copy.deepcopy(input_graph)

        input_connected_graph = copy.deepcopy(
            graph_i_point(copy.deepcopy(new_graph), eachIPoint, copy.deepcopy(list_of_nodes)))
        for input_con_key in input_connected_graph:
            visited[input_con_key] = False

        rem_edge_graph = remove_edges_only_from_graph(eachIPoint, copy.deepcopy(new_graph))
        rem_node_edge_graph=remove_node_only_from_graph(eachIPoint, copy.deepcopy(rem_edge_graph))
        graph_string = str_of_graph(rem_node_edge_graph)

        if graph_string not in set_of_graphs:
            set_of_graphs.add(graph_string)
            unique_set_of_i_points.append((eachIPoint.x, eachIPoint.y))
            if len(input_connected_graph) > 0:
                num_connected_components = no_of_connected_components(copy.deepcopy(input_connected_graph))
                if num_connected_components in i_point_dict:
                    i_point_dict[num_connected_components].append((float(format(merc_lat(eachIPoint.y),'.3f')), float(format(merc_lon(eachIPoint.x),'.3f'))))
                else:
                    i_point_dict[num_connected_components] = [(float(format(merc_lat(eachIPoint.y),'.3f')), float(format(merc_lon(eachIPoint.x),'.3f')))]

                list_connected_components.append(num_connected_components)
                list_of_shortest_components.append(smallest_size_of_component)
                list_of_largest_components.append(largest_size_of_component)
            else:
                num_connected_components = 0
                if num_connected_components in i_point_dict:
                    i_point_dict[num_connected_components].append((float(format(merc_lat(eachIPoint.y),'.3f')), float(format(merc_lon(eachIPoint.x),'.3f'))))
                else:
                    i_point_dict[num_connected_components] = [(float(format(merc_lat(eachIPoint.y),'.3f')), float(format(merc_lon(eachIPoint.x),'.3f')))]
                list_connected_components.append(0)
                list_of_shortest_components.append(0)
                list_of_largest_components.append(0)
    #for everyPoint in set_of_i_points:
        #print((everyPoint[0], everyPoint[1]))
    unique_latLng_i_points=list()
    for unique_merc_i_point in unique_set_of_i_points:
        unique_latLng_i_points.append((merc_lat(unique_merc_i_point[1]), merc_lon(unique_merc_i_point[0])))
    #print(list_connected_components)
    #print("FRom Generic")
    #print(i_point_dict[max(list_connected_components)])
    return max(list_connected_components), min(list_of_shortest_components), min(list_of_largest_components), len(set_of_graphs), i_point_dict[max(list_connected_components)]


#inputGraph = {(1.0, 0.0): [Point(8, 0), Point(1, -8)],
#              (1.0, -8.0): [Point(8, -8), Point(8, 0), Point(1, 0)],
#              (8.0, -8.0): [Point(1, -8), Point(8, 0)],
#              (8.0, 0.0): [Point(1, 0), Point(1, -8), Point(8, -8)]
#              }

#inputGraph = {(-12103211.6364987, 5041779.41042201): [Point(-11031872.8571042, 4651928.01084357),
#                                                     Point(-10841071.2498845, 5392671.93095949),
#                                                      Point(-11638564.0819275, 4321359.27157986)],
#              (-11031872.8571042, 4651928.01084357): [Point(-12103211.6364987, 5041779.41042201),
#                                                      Point(-10841071.2498845, 5392671.93095949)],
#              (-10841071.2498845, 5392671.93095949): [Point(-11031872.8571042, 4651928.01084357),
#                                                      Point(-12103211.6364987, 5041779.41042201)],
#              (-11638564.0819275, 4321359.27157986): [Point(-12103211.6364987, 5041779.41042201)]}

def convert_input_graph_to_mercator(lat_lng_input_graph):
    mercator_input_graph = dict()
    for latLngKey in lat_lng_input_graph:
        merc_list = list()
        x_coord = merc_x(latLngKey[1])
        y_coord = merc_y(latLngKey[0])
        merc_key = (x_coord, y_coord)
        for eachVal in lat_lng_input_graph[latLngKey]:
            val_x_coord = merc_x(eachVal.y)
            val_y_coord = merc_y(eachVal.x)
            merc_list.append(Point(val_x_coord, val_y_coord))
        mercator_input_graph[merc_key] = merc_list

    return mercator_input_graph


def convert_graph_to_reqd_format(single_input_graph):
    copy_graph = copy.deepcopy(single_input_graph)
    for each_key in copy_graph:
        for each_val in copy_graph[each_key]:
            new_point = Point(each_key[0], each_key[1])
            if (each_val.x, each_val.y) in single_input_graph:
                single_input_graph[(each_val.x, each_val.y)].append(new_point)
            else:
                single_input_graph[(each_val.x, each_val.y)] = [new_point]

    return single_input_graph



